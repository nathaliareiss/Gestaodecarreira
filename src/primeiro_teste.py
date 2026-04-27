from datetime import date

from gestao_carreira.services.datas import calcular_idade


def main() -> None:
    nome = "Nathalia"
    data_nascimento = date(1985, 5, 10)
    idade = calcular_idade(data_nascimento)

    print(f"Nome: {nome}")
    print(f"Data de nascimento: {data_nascimento.strftime('%d/%m/%Y')}")
    print(f"Idade hoje: {idade} anos")


if __name__ == "__main__":
    main()
