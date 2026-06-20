from __future__ import annotations

from datetime import date

from backend.services import historico_funcional_service
from backend.services.historico_funcional_service import AfastamentoPeriodo, EventoHistorico


def test_extrai_ferias_regulamentares_contando_dias_uteis(monkeypatch) -> None:
    texto = """
    > Minha carreira > Ferias > Ferias regulamentares
    Consultar ferias regulamentares
    Ano Referencia Inicio Retorno Previsto Retorno Efetivo
    2026 11/11/2026 03/12/2026 -
    2026 12/02/2026 26/02/2026 26/02/2026
    """
    monkeypatch.setattr(historico_funcional_service, "extrair_texto_pdf", lambda _: texto)

    periodos, resumo = historico_funcional_service.analisar_ferias_pdf(b"pdf")

    assert len(periodos) == 2
    assert periodos[0].tipo == "regular"
    assert periodos[0].data_inicio.isoformat() == "2026-11-11"
    assert periodos[0].data_fim.isoformat() == "2026-12-02"
    assert periodos[0].regra_contagem == "dias_uteis"
    assert periodos[1].data_fim.isoformat() == "2026-02-25"
    assert resumo.periodos_totais == 2
    assert resumo.dias_por_tipo["regular"] == sum(item.dias_contabilizados for item in periodos)


def test_extrai_ferias_premio_contando_dias_corridos(monkeypatch) -> None:
    texto = """
    > Minha carreira > Ferias > Ferias-premio
    Consultar ferias-premio
    Solicitacao Periodo Tempo
    - 01/08/2022 a
    01/09/2022
    1 mes
    - 17/04/2026 a
    02/05/2026
    15 dias
    """
    monkeypatch.setattr(historico_funcional_service, "extrair_texto_pdf", lambda _: texto)

    periodos, resumo = historico_funcional_service.analisar_ferias_pdf(b"pdf")

    assert len(periodos) == 2
    assert all(item.tipo == "premium" for item in periodos)
    assert all(item.regra_contagem == "dias_corridos" for item in periodos)
    assert periodos[0].dias_contabilizados == 32
    assert periodos[1].dias_contabilizados == 16
    assert resumo.dias_totais_usados == 48


def test_proximo_marco_suspende_intersticio_por_licenca_saude_maior_que_90_dias() -> None:
    evento_progressao = EventoHistorico(
        tipo="progressao",
        descricao="Progressao anterior",
        cargo="Professor",
        simbolo="PEB",
        nivel="I",
        grau="A",
        data_publicacao=date(2024, 1, 1),
        data_efetiva=date(2024, 1, 1),
        data_prevista=date(2024, 1, 1),
        status="cumprindo",
        atraso_dias=0,
    )
    afastamento = AfastamentoPeriodo(
        tipo="licenca_para_tratamento_de_saude",
        data_inicio=date(2024, 6, 1),
        data_fim=date(2024, 9, 8),
        total_dias=100,
        legislacao=None,
        publicacao=None,
        mes_ano_afastamento="06/2024",
        dias_restantes_ate_pericia=0,
    )

    proxima = historico_funcional_service._proximo_marco(
        [evento_progressao],
        "progressao",
        date(2024, 1, 1),
        [afastamento],
    )

    assert proxima == date(2026, 4, 11)


def test_aposentadoria_professor_nao_usa_pedagio_automatico_abaixo_da_idade_de_transicao() -> None:
    _, data_idade, data_prevista, *_ = historico_funcional_service._cronometro_ate_aposentadoria(
        data_nascimento=date(1988, 8, 12),
        data_exercicio=date(2010, 2, 15),
        anos_clt_averbados=2,
        sexo="feminino",
        categoria_previdenciaria="professor",
    )

    assert data_idade >= date(2039, 8, 12)
    assert data_prevista >= date(2039, 8, 12)
