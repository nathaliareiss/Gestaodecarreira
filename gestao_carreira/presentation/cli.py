from datetime import date

from gestao_carreira.domain.servidora import Servidora
from gestao_carreira.services.carreira import montar_resumo_funcional


def main() -> None:
    servidora = Servidora(
        nome="Nathalia",
        data_nascimento=date(1985, 5, 10),
        data_ingresso=date(2000, 6, 1),
    )

    resumo = montar_resumo_funcional(servidora)

    print("Gestao de Carreira")
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

