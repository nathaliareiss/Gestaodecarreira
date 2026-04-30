from pathlib import Path
import sys
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.servidora import Servidora
from backend.logger import logger
from backend.schemas.carreira_schema import CadastroCarreiraSchema
from backend.services.carreira_service import montar_resumo_funcional, parsear_data


def ler_data(mensagem: str) -> date:
    while True:
        try:
            texto = input(mensagem).strip()
        except EOFError as exc:
            raise SystemExit(
                "Entrada encerrada. Execute este comando em um terminal interativo."
            ) from exc
        try:
            return parsear_data(texto)
        except ValueError as erro:
            logger.warning("Data invalida informada", extra={"valor": texto, "motivo": str(erro)})


def ler_texto_nao_vazio(mensagem: str) -> str:
    while True:
        try:
            texto = input(mensagem).strip()
        except EOFError as exc:
            raise SystemExit(
                "Entrada encerrada. Execute este comando em um terminal interativo."
            ) from exc
        if texto:
            return texto
        logger.warning("Campo obrigatorio vazio")


def ler_sim_nao(mensagem: str) -> bool:
    while True:
        try:
            resposta = input(mensagem).strip().lower()
        except EOFError as exc:
            raise SystemExit(
                "Entrada encerrada. Execute este comando em um terminal interativo."
            ) from exc
        if resposta in {"s", "sim"}:
            return True
        if resposta in {"n", "nao"}:
            return False
        logger.warning("Resposta invalida", extra={"resposta": resposta})


def executar() -> None:
    logger.info("Iniciando fluxo de carreira", extra={"etapa": "inicio"})
    logger.info("Coletando dados iniciais", extra={"etapa": "coleta"})

    nome = ler_texto_nao_vazio("Nome: ")
    data_nascimento = ler_data("Data de nascimento (dd/mm/aaaa): ")
    data_ingresso = ler_data("Data de ingresso/exercicio (dd/mm/aaaa): ")
    tem_tempo_clt_averbado = ler_sim_nao("Tem tempo CLT averbado? (s/n): ")

    cadastro = CadastroCarreiraSchema(
        nome=nome,
        data_nascimento=data_nascimento,
        data_ingresso=data_ingresso,
        tem_tempo_clt_averbado=tem_tempo_clt_averbado,
    )

    servidora = Servidora(
        nome=cadastro.nome,
        data_nascimento=cadastro.data_nascimento,
        data_ingresso=cadastro.data_ingresso,
        tem_tempo_clt_averbado=cadastro.tem_tempo_clt_averbado,
    )

    resumo = montar_resumo_funcional(servidora)

    logger.info("Cadastro realizado", extra={"etapa": "cadastro"})
    logger.info("Nome informado", extra={"nome": servidora.nome})
    logger.info(
        "Data de nascimento informada",
        extra={"data_nascimento": servidora.data_nascimento.strftime("%d/%m/%Y")},
    )
    logger.info(
        "Data de ingresso informada",
        extra={"data_ingresso": servidora.data_ingresso.strftime("%d/%m/%Y")},
    )
    logger.info(
        "Tempo CLT averbado",
        extra={"tem_tempo_clt_averbado": servidora.tem_tempo_clt_averbado},
    )
    logger.info("Resumo funcional", extra={"etapa": "resumo"})
    logger.info(
        "Marco de 25 anos de carreira",
        extra={"data": resumo.data_25_anos_carreira.strftime("%d/%m/%Y")},
    )
    logger.info(
        "Marco de idade minima para aposentadoria",
        extra={"data": resumo.data_idade_minima_aposentadoria.strftime("%d/%m/%Y")},
    )
    logger.info(
        "Idade no marco de 25 anos",
        extra={"idade": resumo.idade_na_data_25_anos_carreira},
    )
    logger.info(
        "Possui idade minima no marco",
        extra={"resultado": resumo.possui_idade_minima_na_data_25_anos_carreira},
    )
    logger.info(
        "Aposentadoria provavel",
        extra={"data": resumo.data_prevista_aposentadoria.strftime("%d/%m/%Y")},
    )
    logger.info(
        "Conferencia de grau e nivel aos 45 anos",
        extra={"grau": resumo.grau_aos_45_anos, "nivel": resumo.nivel_aos_45_anos},
    )
    logger.info(
        "Conferencia de grau e nivel na aposentadoria",
        extra={"grau": resumo.grau_na_aposentadoria, "nivel": resumo.nivel_na_aposentadoria},
    )


if __name__ == "__main__":
    executar()
