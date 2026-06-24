from __future__ import annotations

from datetime import date

from backend.services import historico_funcional_service
from backend.services.historico_funcional_job_service import normalizar_dados_historico_salvo
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


def test_analisa_ate_tres_pdfs_de_ferias_no_mesmo_resumo(monkeypatch) -> None:
    textos = {
        b"regular": """
        Consultar ferias regulamentares
        Ano Referencia Inicio Retorno Previsto Retorno Efetivo
        2026 12/02/2026 26/02/2026 26/02/2026
        """,
        b"premio": """
        Consultar ferias-premio
        Solicitacao Periodo Tempo
        - 17/04/2026 a
        02/05/2026
        15 dias
        """,
    }
    monkeypatch.setattr(historico_funcional_service, "extrair_texto_pdf", lambda conteudo: textos[conteudo])

    periodos, resumo = historico_funcional_service.analisar_ferias_pdfs([b"regular", b"premio"])

    assert len(periodos) == 2
    assert resumo.periodos_por_tipo == {"premium": 1, "regular": 1}
    assert resumo.dias_por_tipo["premium"] == 16
    assert resumo.dias_por_tipo["regular"] == periodos[0].dias_contabilizados


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
    _, data_idade, data_prevista, dias_trabalhados, dias_totais, *_ = historico_funcional_service._cronometro_ate_aposentadoria(
        data_nascimento=date(1988, 8, 12),
        data_exercicio=date(2010, 2, 15),
        anos_clt_averbados=2,
        sexo="feminino",
        categoria_previdenciaria="professor",
    )

    assert data_idade >= date(2039, 8, 12)
    assert data_prevista >= date(2039, 8, 12)
    assert dias_totais - dias_trabalhados == max((data_prevista - date.today()).days, 0)


def test_aposentadoria_seguranca_publica_usa_idade_por_sexo_e_nao_regra_professor() -> None:
    _, data_idade_feminino, data_prevista_feminino, *_ = historico_funcional_service._cronometro_ate_aposentadoria(
        data_nascimento=date(1995, 6, 1),
        data_exercicio=date(2010, 1, 1),
        anos_clt_averbados=0,
        sexo="feminino",
        categoria_previdenciaria="seguranca",
    )
    _, data_idade_masculino, data_prevista_masculino, *_ = historico_funcional_service._cronometro_ate_aposentadoria(
        data_nascimento=date(1995, 6, 1),
        data_exercicio=date(2010, 1, 1),
        anos_clt_averbados=0,
        sexo="masculino",
        categoria_previdenciaria="seguranca",
    )

    assert data_idade_feminino == date(2044, 6, 1)
    assert data_idade_masculino == date(2048, 6, 1)
    assert data_prevista_feminino == date(2044, 6, 1)
    assert data_prevista_masculino == date(2048, 6, 1)


def test_cargo_de_agente_penitenciario_forca_categoria_seguranca_publica() -> None:
    categoria = historico_funcional_service._categoria_previdenciaria_por_cargo(
        "professor",
        "Agente Penitenciario Policial Penal",
    )

    assert categoria == "seguranca"


def test_normaliza_historico_salvo_recalcula_tempo_restante_sem_usar_valor_antigo() -> None:
    dados = {
        "historico_id": 1,
        "usuario_id": 7,
        "data_nascimento": "1995-06-01",
        "data_exercicio": "2020-01-01",
        "sexo": "feminino",
        "categoria_previdenciaria": "professor",
        "tempo_clt_averbado_anos": 0,
        "dias_trabalhados": 1,
        "dias_totais_ate_aposentadoria": 365 * 14,
        "percentual_trabalhado": 1,
        "percentual_restante": 99,
        "eventos": [],
    }

    normalizado = normalizar_dados_historico_salvo(dados, historico_id=1, usuario_id=7)
    resumo = normalizado["resumo_grafico"]
    data_prevista = date.fromisoformat(str(normalizado["data_aposentadoria_prevista"]))

    assert normalizado["tempo_clt_averbado_anos"] == 0
    assert resumo["tempo_restante_dias"] == max((data_prevista - date.today()).days, 0)
    assert resumo["tempo_restante_dias"] > 365 * 18
    assert normalizado["resumo_aposentadoria"]["data_prevista"] == data_prevista.isoformat()


def test_resumo_aposentadoria_projeta_nivel_e_grau_com_intersticios_almg() -> None:
    evento_nomeacao = EventoHistorico(
        tipo="nomeacao",
        descricao="Nomeacao",
        cargo="Professor",
        simbolo="PEB",
        nivel="I",
        grau="A",
        data_publicacao=date(2020, 1, 1),
        data_efetiva=date(2020, 1, 1),
        data_prevista=None,
        status="nao_aplicavel",
        atraso_dias=0,
    )
    evento_progressao = EventoHistorico(
        tipo="progressao",
        descricao="Progressao",
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

    resumo = historico_funcional_service.montar_resumo_aposentadoria(
        data_nascimento=date(1990, 6, 1),
        data_aposentadoria_por_carreira=date(2030, 1, 1),
        data_aposentadoria_por_idade=date(2035, 6, 1),
        data_aposentadoria_prevista=date(2035, 6, 1),
        eventos=[evento_nomeacao, evento_progressao],
        simbolo_atual="PEB",
        nivel_atual="I",
        grau_atual="A",
        inicio_contagem_progressao=date(2023, 1, 1),
        afastamentos=[],
    )

    assert resumo.idade_por_tempo_servico_anos == 39
    assert resumo.idade_minima_governo_anos == 45
    assert resumo.nivel_previsto == "III"
    assert resumo.grau_previsto == "F"
