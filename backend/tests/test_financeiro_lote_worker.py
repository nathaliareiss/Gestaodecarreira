from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch, Paycheck, PaycheckItem
from backend.repositories.financeiro_repository import criar_lote_financeiro
from backend.queue.tasks.financeiro_tasks import processar_lote_financeiro_job


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


def test_duplicidade_de_competencia_marca_falha_sem_parar_lote() -> None:
    with SessionLocal() as db:
        lote = criar_lote_financeiro(db, user_id=7, total_files=1)
        lote_duplicado = criar_lote_financeiro(db, user_id=7, total_files=1)
        paycheck_existente = Paycheck(
            batch_id=lote.id,
            user_id=7,
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

    assert resultado["status"] == "failed"
    assert resultado["processed"] == 0
    assert resultado["failed"] == 1

    with SessionLocal() as db:
        lote_salvo = db.get(PayrollBatch, lote_duplicado.id)
        assert lote_salvo is not None
        assert lote_salvo.status == "failed"
        assert lote_salvo.processed_files == 0
        assert lote_salvo.failed_files == 1

        total_paychecks = db.scalar(
            select(func.count()).select_from(Paycheck).where(Paycheck.user_id == 7)
        )
        assert total_paychecks == 1


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
