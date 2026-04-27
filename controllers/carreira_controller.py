from datetime import date

from models.servidora import Servidora
from services.carreira_service import montar_resumo_funcional, parsear_data
from schemas.carreira_schema import CadastroCarreiraSchema


def ler_data(mensagem: str) -> date:
    while True:
        texto = input(mensagem).strip()
        try:
            return parsear_data(texto)
        except ValueError as erro:
            print(erro)


def ler_texto_nao_vazio(mensagem: str) -> str:
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("Este campo nao pode ficar vazio.")


def ler_sim_nao(mensagem: str) -> bool:
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in {"s", "sim"}:
            return True
        if resposta in {"n", "nao"}:
            return False
        print("Responda com s ou n.")


def executar() -> None:
    print("Gestao de Carreira")
    print("Vamos cadastrar seus dados iniciais.")

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

    print()
    print("Cadastro realizado")
    print(f"Nome: {servidora.nome}")
    print(f"Nascimento: {servidora.data_nascimento.strftime('%d/%m/%Y')}")
    print(f"Ingresso: {servidora.data_ingresso.strftime('%d/%m/%Y')}")
    print(
        "Tempo CLT averbado: "
        f"{'sim' if servidora.tem_tempo_clt_averbado else 'nao'}"
    )
    print()
    print("Resumo funcional")
    print(
        "25 anos de carreira: "
        f"{resumo.data_25_anos_carreira.strftime('%d/%m/%Y')}"
    )
    print(
        "Data de idade minima para aposentadoria: "
        f"{resumo.data_idade_minima_aposentadoria.strftime('%d/%m/%Y')}"
    )
    print(
        "Idade nessa data: "
        f"{resumo.idade_na_data_25_anos_carreira} anos"
    )
    print(
        "Tem idade minima nessa data: "
        f"{'sim' if resumo.possui_idade_minima_na_data_25_anos_carreira else 'nao'}"
    )
    print(
        "Aposentadoria provavel: "
        f"{resumo.data_prevista_aposentadoria.strftime('%d/%m/%Y')}"
    )
    print(
        "Grau aos 45 anos: "
        f"{resumo.grau_aos_45_anos}"
        f" | Nivel aos 45 anos: {resumo.nivel_aos_45_anos}"
    )
    print(
        "Grau na aposentadoria: "
        f"{resumo.grau_na_aposentadoria}"
        f" | Nivel na aposentadoria: {resumo.nivel_na_aposentadoria}"
    )
