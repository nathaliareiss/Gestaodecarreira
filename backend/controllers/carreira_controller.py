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
            logger.warning("%s", erro)


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
        logger.warning("Este campo nao pode ficar vazio.")


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
        logger.warning("Responda com s ou n.")


def executar() -> None:
    logger.info("Gestao de Carreira")
    logger.info("Vamos cadastrar seus dados iniciais.")

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

    logger.info("Cadastro realizado")
    logger.info("Nome: %s", servidora.nome)
    logger.info(
        "Nascimento: %s",
        servidora.data_nascimento.strftime("%d/%m/%Y"),
    )
    logger.info(
        "Ingresso: %s",
        servidora.data_ingresso.strftime("%d/%m/%Y"),
    )
    logger.info(
        "Tempo CLT averbado: %s",
        "sim" if servidora.tem_tempo_clt_averbado else "nao",
    )
    logger.info("Resumo funcional")
    logger.info(
        "25 anos de carreira: %s",
        resumo.data_25_anos_carreira.strftime("%d/%m/%Y"),
    )
    logger.info(
        "Data de idade minima para aposentadoria: %s",
        resumo.data_idade_minima_aposentadoria.strftime("%d/%m/%Y"),
    )
    logger.info(
        "Idade nessa data: %s anos",
        resumo.idade_na_data_25_anos_carreira,
    )
    logger.info(
        "Tem idade minima nessa data: %s",
        "sim" if resumo.possui_idade_minima_na_data_25_anos_carreira else "nao",
    )
    logger.info(
        "Aposentadoria provavel: %s",
        resumo.data_prevista_aposentadoria.strftime("%d/%m/%Y"),
    )
    logger.info(
        "Grau aos 45 anos: %s | Nivel aos 45 anos: %s",
        resumo.grau_aos_45_anos,
        resumo.nivel_aos_45_anos,
    )
    logger.info(
        "Grau na aposentadoria: %s | Nivel na aposentadoria: %s",
        resumo.grau_na_aposentadoria,
        resumo.nivel_na_aposentadoria,
    )


if __name__ == "__main__":
    executar()
