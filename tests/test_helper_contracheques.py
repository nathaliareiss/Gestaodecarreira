from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


HELPER_DIR = Path(__file__).resolve().parents[1] / "helper-contracheques"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))


def carregar_modulo_helper():
    caminho = HELPER_DIR / "main.py"
    spec = importlib.util.spec_from_file_location("helper_contracheques_main", caminho)
    if spec is None or spec.loader is None:
        raise RuntimeError("Nao foi possivel carregar helper-contracheques/main.py")

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


helper = carregar_modulo_helper()


class FakeElement:
    def __init__(self, text: str = "", *, attrs: dict[str, str] | None = None, visible: bool = True):
        self._text = text
        self._attrs = attrs or {}
        self._visible = visible

    def get_attribute(self, name: str):
        return self._attrs.get(name)

    def text_content(self):
        return self._text

    def is_visible(self):
        return self._visible


class FakeCollection:
    def __init__(self, elements: list[FakeElement] | None = None, inner_text: str = ""):
        self._elements = elements or []
        self._inner_text = inner_text

    def count(self):
        return len(self._elements)

    def nth(self, index: int):
        return self._elements[index]

    @property
    def first(self):
        if not self._elements:
            raise IndexError("empty collection")
        return self._elements[0]

    def inner_text(self, timeout: int | None = None):  # noqa: ARG002
        return self._inner_text


class FakePage:
    def __init__(self, *, url: str, title: str, selectors: dict[str, FakeCollection]):
        self.url = url
        self._title = title
        self._selectors = selectors

    def locator(self, selector: str):
        return self._selectors.get(selector, FakeCollection())

    def title(self):
        return self._title

    def wait_for_timeout(self, timeout: int):  # noqa: ARG002
        return None


class HelperContrachequesTests(unittest.TestCase):
    def test_extrair_token_de_candidato_lida_com_protocolo_e_classe(self):
        self.assertEqual(
            helper.extrair_token_de_candidato("gestaodecarreira://importar?token=abc123"),
            "abc123",
        )
        self.assertEqual(helper.extrair_token_de_candidato("token=abc123"), "abc123")

    def test_sanitizar_argv_para_log_oculta_token(self):
        resultado = helper.sanitizar_argv_para_log(
            [
                "helper.exe",
                "--token",
                "abc123",
                "gestaodecarreira://importar?token=xyz987",
            ],
        )

        self.assertEqual(resultado[1], "--token")
        self.assertEqual(resultado[2], "[oculto]")
        self.assertEqual(resultado[3], "gestaodecarreira://importar?token=%5Boculto%5D")

    def test_detecta_pagina_de_contracheques_por_sinais_fortes(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Portal do Servidor",
            selectors={
                "body": FakeCollection(inner_text="Consultar contracheque\nMês/Ano\nMensal\nCONSULTAR\nEXIBIR\nBAIXAR"),
                "button:has-text('Consultar')": FakeCollection([FakeElement("Consultar")]),
                "button:has-text('CONSULTAR')": FakeCollection([FakeElement("CONSULTAR")]),
                "button:has-text('EXIBIR')": FakeCollection([FakeElement("EXIBIR")]),
                "button:has-text('BAIXAR')": FakeCollection([FakeElement("BAIXAR")]),
                "button": FakeCollection([FakeElement("BAIXAR"), FakeElement("EXIBIR"), FakeElement("CONSULTAR")]),
                "a": FakeCollection([]),
                "[role='button']": FakeCollection([]),
            },
        )

        self.assertTrue(helper.pagina_consultar_contracheque_pronta(page))

    def test_detecta_pagina_pronta_quando_texto_baixar_esta_visivel(self):
        page = FakePage(
            url="https://portal.exemplo/outra",
            title="Outra tela",
            selectors={
                "body": FakeCollection(inner_text="Algo diferente"),
                "text=BAIXAR": FakeCollection([FakeElement("BAIXAR")]),
                "text=EXIBIR": FakeCollection([]),
                "a:has-text('BAIXAR')": FakeCollection([FakeElement("BAIXAR")]),
                "a:has-text('EXIBIR')": FakeCollection([]),
                "button:has-text('BAIXAR')": FakeCollection([]),
                "button:has-text('EXIBIR')": FakeCollection([]),
                "[role='button']:has-text('BAIXAR')": FakeCollection([]),
                "[role='button']:has-text('EXIBIR')": FakeCollection([]),
                "input[value*='BAIXAR' i]": FakeCollection([]),
                "input[value*='EXIBIR' i]": FakeCollection([]),
            },
        )

        self.assertTrue(helper.pagina_consultar_contracheque_pronta(page))

    def test_encontra_alvos_download_com_texto_e_link_estilizado(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "body": FakeCollection(inner_text="Lista de contracheques"),
                "text=BAIXAR": FakeCollection([FakeElement("BAIXAR")]),
                "text=EXIBIR": FakeCollection([FakeElement("EXIBIR")]),
                "a:has-text('BAIXAR')": FakeCollection(
                    [
                        FakeElement(
                            "BAIXAR",
                            attrs={
                                "href": "https://portal.exemplo/arquivo.pdf",
                                "aria-label": "Baixar contracheque",
                            },
                        ),
                    ],
                ),
                "a:has-text('EXIBIR')": FakeCollection([FakeElement("EXIBIR")]),
                "button:has-text('BAIXAR')": FakeCollection([]),
                "button:has-text('EXIBIR')": FakeCollection([]),
                "[role='button']:has-text('BAIXAR')": FakeCollection([]),
                "[role='button']:has-text('EXIBIR')": FakeCollection([]),
                "input[value*='BAIXAR' i]": FakeCollection([FakeElement("", attrs={"value": "BAIXAR"})]),
                "input[value*='EXIBIR' i]": FakeCollection([]),
            },
        )

        alvos = helper.encontrar_alvos_download(page)
        self.assertGreaterEqual(len(alvos), 1)
        assinaturas = [assinatura for assinatura, _ in alvos]
        self.assertTrue(any("BAIXAR" in assinatura for assinatura in assinaturas))
        self.assertTrue(any("EXIBIR" in assinatura for assinatura in assinaturas))

    def test_detecta_pagina_pronta_quando_ha_botao_baixar_visivel(self):
        page = FakePage(
            url="https://portal.exemplo/outra",
            title="Outra tela",
            selectors={
                "body": FakeCollection(inner_text="Algo diferente"),
                "button:has-text('BAIXAR')": FakeCollection([FakeElement("BAIXAR")]),
                "button": FakeCollection([FakeElement("BAIXAR")]),
                "a": FakeCollection([]),
                "[role='button']": FakeCollection([]),
            },
        )

        self.assertTrue(helper.pagina_consultar_contracheque_pronta(page))

    def test_detecta_alvos_de_download_por_link_pdf(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "a": FakeCollection(
                    [
                        FakeElement(
                            "BAIXAR",
                            attrs={
                                "href": "https://portal.exemplo/arquivo.pdf",
                                "aria-label": "Baixar contracheque",
                            },
                        ),
                    ],
                ),
                "body": FakeCollection(inner_text="Lista de contracheques"),
            },
        )

        alvos = helper.encontrar_alvos_download(page)
        self.assertEqual(len(alvos), 1)
        self.assertIn("BAIXAR", alvos[0][0])


if __name__ == "__main__":
    unittest.main()
