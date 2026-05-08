from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch, Paycheck, PaycheckItem
from backend.repositories.financeiro_repository import criar_lote_financeiro
from backend.queue.tasks.financeiro_tasks import (
    processar_arquivo_financeiro_job,
    processar_lote_financeiro_job,
)


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"
TEST_TEMP_DIR = Path(__file__).parent / "_tmp_financeiro"
TEST_TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _criar_copia_pdf(nome: str) -> Path:
    destino = TEST_TEMP_DIR / nome
    destino.write_bytes(FIXTURE_PDF.read_bytes())
    return destino


def test_processamento_assincrono_persiste_paycheck_e_itens() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=1)

    arquivo = _criar_copia_pdf("contracheque-1.pdf")
    resultado = processar_lote_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo.name,
                    "arquivo_temporario_path": str(arquivo),
                }
            ],
        }
    )

    assert resultado["status"] == "completed"
    assert resultado["processed"] == 1
    assert resultado["failed"] == 0

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote.id)
        assert lote_salvo is not None
        assert lote_salvo.status == "completed"
        assert lote_salvo.processed_files == 1
        assert lote_salvo.failed_files == 0

        paycheck = db.scalar(
            select(Paycheck).where(Paycheck.batch_id == lote.id, Paycheck.user_id == 7)
        )
        assert paycheck is not None
        assert paycheck.competencia == "Janeiro/2022"
        assert paycheck.bruto == Decimal("5375.07")

        itens = db.scalars(select(PaycheckItem).where(PaycheckItem.paycheck_id == paycheck.id)).all()
    assert len(itens) >= 4
    assert any(item.tipo == "vantagem" for item in itens)
    assert any(item.tipo == "desconto" for item in itens)
    assert any(item.categoria_normalizada == "salario_base" for item in itens)
    assert any(item.descricao_original for item in itens)


def test_processamento_por_pdf_atualiza_contadores_progressivamente() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=2)

    arquivo_1 = _criar_copia_pdf("contracheque-progressivo-1.pdf")
    arquivo_2 = _criar_copia_pdf("contracheque-progressivo-2.pdf")

    resultado_1 = processar_arquivo_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivo": {
                "arquivo_nome": arquivo_1.name,
                "arquivo_temporario_path": str(arquivo_1),
                "file_hash": None,
            },
        }
    )
    assert resultado_1["processed_count"] == 1
    assert resultado_1["failed_count"] == 0
    assert resultado_1["status"] in {"processing", "completed"}

    resultado_2 = processar_arquivo_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivo": {
                "arquivo_nome": arquivo_2.name,
                "arquivo_temporario_path": str(arquivo_2),
                "file_hash": None,
            },
        }
    )
    assert resultado_2["processed_count"] + resultado_2["duplicated_count"] + resultado_2["failed_count"] == 2
    assert resultado_2["status"] == "completed"

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote.id)
        assert lote_salvo is not None
        assert lote_salvo.processed_files + lote_salvo.duplicated_files + lote_salvo.failed_files == 2
        assert lote_salvo.processing_seconds_total > 0


def test_duplicidade_de_competencia_conta_como_duplicado_sem_parar_lote() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=1)
        lote_duplicado = criar_lote_financeiro(db, user_id=7, total_files=1)
        paycheck_existente = Paycheck(
            batch_id=lote.id,
            user_id=7,
            file_hash="hash-existente",
            matricula="",
            competencia="Janeiro/2022",
            ano=2022,
            mes=1,
            bruto=Decimal("8816.54"),
            descontos=Decimal("1912.66"),
            liquido=Decimal("6903.88"),
            vencimento_basico=Decimal("5910.41"),
            adicional_desempenho=Decimal("591.04"),
            adicional_noturno=Decimal("182.04"),
            irrf=Decimal("710.39"),
            previdencia=Decimal("842.08"),
        )
        db.add(paycheck_existente)
        db.commit()

    arquivo = _criar_copia_pdf("contracheque-duplicado.pdf")
    resultado = processar_lote_financeiro_job(
        {
            "batch_id": lote_duplicado.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo.name,
                    "arquivo_temporario_path": str(arquivo),
                }
            ],
        }
    )

    assert resultado["status"] == "completed"
    assert resultado["processed"] == 0
    assert resultado["duplicated"] == 1
    assert resultado["failed"] == 0

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote_duplicado.id)
        assert lote_salvo is not None
        assert lote_salvo.status == "completed"
        assert lote_salvo.processed_files == 0
        assert lote_salvo.duplicated_files == 1
        assert lote_salvo.failed_files == 0

        total_paychecks = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.user_id == 7)
        )
        assert total_paychecks == 1


def test_arquivo_com_mesmo_hash_e_nome_diferente_e_duplicado() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=2)

    arquivo_1 = _criar_copia_pdf("contracheque-original.pdf")
    arquivo_2 = _criar_copia_pdf("contracheque-copia.pdf")

    resultado = processar_lote_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo_1.name,
                    "arquivo_temporario_path": str(arquivo_1),
                },
                {
                    "arquivo_nome": arquivo_2.name,
                    "arquivo_temporario_path": str(arquivo_2),
                },
            ],
        }
    )

    assert resultado["status"] == "completed"
    assert resultado["processed_count"] == 1
    assert resultado["duplicated_count"] == 1
    assert resultado["failed_count"] == 0

    with SessionLocal() as db:
        total_paychecks = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.batch_id == lote.id)
        )
        assert total_paychecks == 1

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote.id)
        assert lote_salvo is not None
        assert lote_salvo.processed_files == 1
        assert lote_salvo.duplicated_files == 1
        assert lote_salvo.failed_files == 0

        total_paychecks = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.batch_id == lote.id)
        )
        assert total_paychecks == 1


def test_mesmo_mes_ano_com_arquivo_diferente_e_mesma_matricula_e_duplicado(monkeypatch) -> None:
    from backend.services import financeiro_batch_service as service

    monkeypatch.setattr(
        service,
        "parse_contracheque",
        lambda _pdf_path: {
            "competencia": "Janeiro/2024",
            "ano": 2024,
            "mes": 1,
            "matricula": "123456",
            "bruto": Decimal("4000.00"),
            "descontos": Decimal("500.00"),
            "liquido": Decimal("3500.00"),
            "vencimento_basico": Decimal("3000.00"),
            "adicional_desempenho": Decimal("200.00"),
            "adicional_noturno": Decimal("100.00"),
            "irrf": Decimal("100.00"),
            "previdencia": Decimal("100.00"),
        },
    )
    monkeypatch.setattr(
        service,
        "extrair_rubricas_contracheque",
        lambda _pdf_path: [
            {
                "tipo": "vantagem",
                "categoria_normalizada": "salario_base",
                "descricao_original": "Vencimento Basico",
                "descricao": "Vencimento Basico",
                "valor": Decimal("3000.00"),
            }
        ],
    )

    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=2)

    arquivo_1 = TEST_TEMP_DIR / "competencia-1.pdf"
    arquivo_1.write_bytes(b"%PDF-1.4 arquivo-um")
    arquivo_2 = TEST_TEMP_DIR / "competencia-2.pdf"
    arquivo_2.write_bytes(b"%PDF-1.4 arquivo-dois")

    resultado = processar_lote_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo_1.name,
                    "arquivo_temporario_path": str(arquivo_1),
                },
                {
                    "arquivo_nome": arquivo_2.name,
                    "arquivo_temporario_path": str(arquivo_2),
                },
            ],
        }
    )

    assert resultado["status"] == "completed"
    assert resultado["processed_count"] == 1
    assert resultado["duplicated_count"] == 1
    assert resultado["failed_count"] == 0


def test_usuarios_diferentes_mesma_competencia_nao_colidem(monkeypatch) -> None:
    from backend.services import financeiro_batch_service as service

    monkeypatch.setattr(
        service,
        "parse_contracheque",
        lambda _pdf_path: {
            "competencia": "Fevereiro/2024",
            "ano": 2024,
            "mes": 2,
            "matricula": "123456",
            "bruto": Decimal("5000.00"),
            "descontos": Decimal("600.00"),
            "liquido": Decimal("4400.00"),
            "vencimento_basico": Decimal("3000.00"),
            "adicional_desempenho": Decimal("300.00"),
            "adicional_noturno": Decimal("100.00"),
            "irrf": Decimal("200.00"),
            "previdencia": Decimal("100.00"),
        },
    )
    monkeypatch.setattr(
        service,
        "extrair_rubricas_contracheque",
        lambda _pdf_path: [
            {
                "tipo": "vantagem",
                "categoria_normalizada": "salario_base",
                "descricao_original": "Vencimento Basico",
                "descricao": "Vencimento Basico",
                "valor": Decimal("3000.00"),
            }
        ],
    )

    with SessionLocal() as db:
        lote_1 = criar_lote_financeiro(db, user_id=7, total_files=1)
        lote_2 = criar_lote_financeiro(db, user_id=8, total_files=1)

    arquivo_1 = TEST_TEMP_DIR / "usuario-7.pdf"
    arquivo_1.write_bytes(b"%PDF-1.4 usuario-7")
    arquivo_2 = TEST_TEMP_DIR / "usuario-8.pdf"
    arquivo_2.write_bytes(b"%PDF-1.4 usuario-8")

    resultado_1 = processar_lote_financeiro_job(
        {
            "batch_id": lote_1.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo_1.name,
                    "arquivo_temporario_path": str(arquivo_1),
                }
            ],
        }
    )
    resultado_2 = processar_lote_financeiro_job(
        {
            "batch_id": lote_2.id,
            "user_id": 8,
            "arquivos": [
                {
                    "arquivo_nome": arquivo_2.name,
                    "arquivo_temporario_path": str(arquivo_2),
                }
            ],
        }
    )

    assert resultado_1["status"] == "completed"
    assert resultado_2["status"] == "completed"
    assert resultado_1["processed_count"] == 1
    assert resultado_2["processed_count"] == 1

    with SessionLocal() as db:
        total_usuario_7 = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.user_id == 7)
        )
        total_usuario_8 = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.user_id == 8)
        )
        assert total_usuario_7 == 1
        assert total_usuario_8 == 1


def test_pdf_invalido_marca_falha_e_continua_processamento() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=1)

    arquivo = TEST_TEMP_DIR / "contracheque-invalido.pdf"
    arquivo.write_bytes(b"isto nao e um pdf")

    resultado = processar_lote_financeiro_job(
        {
            "batch_id": lote.id,
            "user_id": 7,
            "arquivos": [
                {
                    "arquivo_nome": arquivo.name,
                    "arquivo_temporario_path": str(arquivo),
                }
            ],
        }
    )

    assert resultado["status"] == "failed"
    assert resultado["processed"] == 0
    assert resultado["failed"] == 1

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote.id)
        assert lote_salvo is not None
        assert lote_salvo.status == "failed"
        assert lote_salvo.processed_files == 0
        assert lote_salvo.failed_files == 1
        assert lote_salvo.last_error_message == "O arquivo contracheque-invalido.pdf parece estar inválido ou corrompido."
        assert "O arquivo contracheque-invalido.pdf parece estar inválido ou corrompido." in lote_salvo.failure_messages
