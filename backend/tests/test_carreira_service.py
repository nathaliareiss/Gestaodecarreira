import unittest
from datetime import date

from backend.models.servidora import Servidora
from backend.services.carreira_service import (
    adicionar_anos,
    calcular_data_25_anos_carreira,
    calcular_data_idade_minima_aposentadoria,
    calcular_data_prevista_aposentadoria,
    calcular_grau,
    calcular_idade,
    calcular_nivel,
    montar_resumo_funcional,
    parsear_data,
)


class CarreiraServiceTestCase(unittest.TestCase):
    def test_parsear_data(self) -> None:
        self.assertEqual(parsear_data("05/04/2026"), date(2026, 4, 5))

    def test_adicionar_anos_em_data_bissexta(self) -> None:
        self.assertEqual(adicionar_anos(date(2020, 2, 29), 1), date(2021, 2, 28))

    def test_calcular_idade(self) -> None:
        self.assertEqual(calcular_idade(date(1980, 4, 30), date(2026, 4, 29)), 45)
        self.assertEqual(calcular_idade(date(1980, 4, 30), date(2026, 4, 30)), 46)

    def test_calculos_de_carreira_base(self) -> None:
        self.assertEqual(
            calcular_data_25_anos_carreira(date(2010, 1, 1)),
            date(2035, 1, 1),
        )
        self.assertEqual(
            calcular_data_idade_minima_aposentadoria(date(1980, 1, 1)),
            date(2030, 1, 1),
        )
        self.assertEqual(
            calcular_data_prevista_aposentadoria(date(1980, 1, 1), date(2010, 1, 1)),
            date(2035, 1, 1),
        )

    def test_calcular_grau_e_nivel(self) -> None:
        self.assertEqual(calcular_grau(0), "A")
        self.assertEqual(calcular_grau(4), "C")
        self.assertEqual(calcular_nivel(0), 1)
        self.assertEqual(calcular_nivel(10), 3)

    def test_montar_resumo_funcional(self) -> None:
        servidora = Servidora(
            nome="Maria",
            data_nascimento=date(1980, 1, 1),
            data_ingresso=date(2010, 1, 1),
            tem_tempo_clt_averbado=True,
        )

        resumo = montar_resumo_funcional(servidora)

        self.assertEqual(resumo.data_25_anos_carreira, date(2035, 1, 1))
        self.assertEqual(resumo.idade_na_data_25_anos_carreira, 55)
        self.assertTrue(resumo.possui_idade_minima_na_data_25_anos_carreira)
        self.assertEqual(resumo.data_idade_minima_aposentadoria, date(2030, 1, 1))
        self.assertEqual(resumo.data_prevista_aposentadoria, date(2035, 1, 1))
        self.assertEqual(resumo.grau_aos_45_anos, "H")
        self.assertEqual(resumo.nivel_aos_45_anos, 4)
        self.assertEqual(resumo.grau_na_aposentadoria, "M")
        self.assertEqual(resumo.nivel_na_aposentadoria, 6)


if __name__ == "__main__":
    unittest.main()
