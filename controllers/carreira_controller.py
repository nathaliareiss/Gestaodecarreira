from datetime import date

from models.servidora import Servidora
from services.carreira_service import montar_resumo_funcional, parsear_data


def ler_data(mensagem: str) -> date:
    while True:
        texto = input(mensagem).strip()
        try:
            return parsear_data(texto)
        except ValueError as erro:
            print(erro)


def executar() -> None:
    print("Gestao de Carreira")
    print("Vamos cadastrar seus dados iniciais.")

    nome = input("Nome: ").strip()
    data_nascimento = ler_data("Data de nascimento (dd/mm/aaaa): ")
    data_ingresso = ler_data("Data de ingresso/exercicio (dd/mm/aaaa): ")

    servidora = Servidora(
        nome=nome,
        data_nascimento=data_nascimento,
        data_ingresso=data_ingresso,
    )

    resumo = montar_resumo_funcional(servidora)

    print()
    print("Resumo funcional")
    print(f"Nome: {servidora.nome}")
    print(f"Nascimento: {servidora.data_nascimento.strftime('%d/%m/%Y')}")
    print(f"Ingresso: {servidora.data_ingresso.strftime('%d/%m/%Y')}")
    print(
        "25 anos de carreira: "
        f"{resumo.data_25_anos_carreira.strftime('%d/%m/%Y')}"
    )
    print(
        "Idade nessa data: "
        f"{resumo.idade_na_data_25_anos_carreira} anos"
    )
    print(
        "Tera idade minima nessa data: "
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
