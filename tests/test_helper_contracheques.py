from __future__ import annotations

import argparse
import importlib.util
import re
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

    def is_enabled(self):
        return True

    def bounding_box(self):
        if not self._visible:
            return None
        return {"x": 0, "y": 0, "width": 100, "height": 24}

    def inner_text(self, timeout: int | None = None):  # noqa: ARG002
        return self._text

    def evaluate(self, expression: str):  # noqa: ARG002
        if "tagName" in expression:
            return self._attrs.get("tagName", "BUTTON")
        if "outerHTML" in expression:
            attrs = " ".join(f'{k}="{v}"' for k, v in self._attrs.items() if k != "tagName")
            tag = self._attrs.get("tagName", "button").lower()
            return f"<{tag} {attrs}>{self._text}</{tag}>"
        return None


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


class FakeRow:
    def __init__(
        self,
        competencia: str,
        tipo: str,
        *,
        button_text: str = "Baixar",
        buttons: list[str] | None = None,
    ):
        self._competencia = competencia
        self._tipo = tipo
        self._button_text = button_text
        self._buttons = buttons or [button_text]

    def locator(self, selector: str, **kwargs):
        if selector == "td":
            return FakeCollection(
                [
                    FakeElement(self._competencia),
                    FakeElement(self._tipo),
                    FakeElement(self._button_text),
                ],
            )

        if "button" in selector:
            has_text = kwargs.get("has_text")
            if has_text is None:
                return FakeCollection([FakeElement(text) for text in self._buttons])

            if hasattr(has_text, "search"):
                pattern = has_text
            else:
                pattern = re.compile(re.escape(str(has_text or "")), re.I)

            filtrados = [FakeElement(text) for text in self._buttons if pattern.search(text)]
            if filtrados:
                return FakeCollection(filtrados)
            return FakeCollection([])

        if "a[href]" in selector:
            return FakeCollection([])

        return FakeCollection([])

    def get_by_role(self, role: str, name=None):  # noqa: ARG002
        if role != "button":
            return FakeCollection()

        if hasattr(name, "search"):
            pattern = name
        else:
            pattern = re.compile(re.escape(str(name or "")), re.I)

        filtrados = [FakeElement(text) for text in self._buttons if pattern.search(text)]
        if filtrados:
            return FakeCollection(filtrados)
        return FakeCollection([])


class FakePage:
    def __init__(self, *, url: str, title: str, selectors: dict[str, FakeCollection]):
        self.url = url
        self._title = title
        self._selectors = selectors
        self.frames = []

    def locator(self, selector: str, **kwargs):
        collection = self._selectors.get(selector, FakeCollection())
        has_text = kwargs.get("has_text")
        if has_text is None:
            return collection

        if hasattr(has_text, "search"):
            pattern = has_text
        else:
            pattern = re.compile(re.escape(str(has_text or "")), re.I)

        filtrados: list[FakeElement] = []
        for indice in range(collection.count()):
            item = collection.nth(indice)
            texto = " ".join(
                filter(
                    None,
                    [
                        item.text_content() or "",
                        item.get_attribute("aria-label") or "",
                        item.get_attribute("title") or "",
                        item.get_attribute("href") or "",
                    ],
                ),
            )
            if pattern.search(texto):
                filtrados.append(item)

        return FakeCollection(filtrados)

    def get_by_role(self, role: str, name=None):
        if role != "button":
            return FakeCollection()

        if hasattr(name, "search"):
            pattern = name
        else:
            pattern = re.compile(re.escape(str(name or "")), re.I)

        encontrados: list[FakeElement] = []
        for collection in self._selectors.values():
            for indice in range(collection.count()):
                item = collection.nth(indice)
                texto = item.text_content() or ""
                aria = item.get_attribute("aria-label") or ""
                titulo = item.get_attribute("title") or ""
                if pattern.search(texto) or pattern.search(aria) or pattern.search(titulo):
                    encontrados.append(item)

        return FakeCollection(encontrados)

    def get_by_text(self, pattern):
        encontrados: list[FakeElement] = []
        if hasattr(pattern, "search"):
            matcher = pattern
        else:
            matcher = re.compile(re.escape(str(pattern or "")), re.I)

        for collection in self._selectors.values():
            for indice in range(collection.count()):
                item = collection.nth(indice)
                texto = " ".join(
                    filter(
                        None,
                        [
                            item.text_content() or "",
                            item.get_attribute("aria-label") or "",
                            item.get_attribute("title") or "",
                            item.get_attribute("href") or "",
                        ],
                    ),
                )
                if matcher.search(texto):
                    encontrados.append(item)

        return FakeCollection(encontrados)

    def title(self):
        return self._title

    def content(self):
        return "<html><body></body></html>"

    def screenshot(self, path: str, full_page: bool = True):  # noqa: ARG002
        Path(path).write_bytes(b"fake-png")

    def wait_for_load_state(self, state: str, timeout: int | None = None):  # noqa: ARG002
        return None

    def wait_for_timeout(self, timeout: int):  # noqa: ARG002
        return None


class HelperContrachequesTests(unittest.TestCase):
    def test_extrair_token_de_candidato_lida_com_protocolo_e_classe(self):
        self.assertEqual(
            helper.extrair_token_de_candidato("gestaodecarreira://importar?token=abc123"),
            "abc123",
        )
        self.assertEqual(helper.extrair_token_de_candidato("token=abc123"), "abc123")

    def test_resolver_token_prioriza_protocolo_e_sanitiza_entrada_posicional(self):
        args = argparse.Namespace(
            token="",
            import_url="",
            import_uri="gestaodecarreira://importar?token=TESTE123",
        )

        token, origem = helper.resolver_token(args)
        self.assertEqual(token, "TESTE123")
        self.assertEqual(origem, "protocolo")

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
        self.assertFalse(any("EXIBIR" in assinatura for assinatura in assinaturas))

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

    def test_detecta_botao_baixar_pelo_css_real_do_portal(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "button.btn-outline-primary2": FakeCollection([FakeElement("Baixar", attrs={"class": "text-uppercase btn btn-sm btn-outline-primary2"})]),
                "button": FakeCollection([FakeElement("Exibir", attrs={"class": "text-uppercase btn btn-sm btn-primary2"}), FakeElement("Baixar", attrs={"class": "text-uppercase btn btn-sm btn-outline-primary2"})]),
                "body": FakeCollection(inner_text="04/2026 Mensal Exibir Baixar"),
            },
        )

        botoes = helper.encontrar_botoes_baixar(page)
        self.assertGreaterEqual(len(botoes), 1)
        self.assertTrue(helper.pagina_consultar_contracheque_pronta(page))

    def test_clicar_baixar_na_linha_prioriza_baixar_sobre_exibir(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "body": FakeCollection(inner_text="04/2026 Mensal Exibir Baixar"),
            },
        )
        linha = FakeRow("04/2026", "Mensal", buttons=["Exibir", "Baixar"])
        pasta = Path("C:/gdc-test/mensais")
        chamadas: list[str] = []

        original = helper.portal_automation._baixar_com_botao_na_linha

        def fake_baixar_com_botao_na_linha(*, botao, **kwargs):
            chamadas.append(botao.inner_text())
            return True

        helper.portal_automation._baixar_com_botao_na_linha = fake_baixar_com_botao_na_linha
        try:
            ok = helper.portal_automation.clicar_baixar_na_linha(
                page=page,
                linha=linha,
                pasta_destino=pasta,
                competencia="04/2026",
                tipo="Mensal",
                context=object(),
            )
        finally:
            helper.portal_automation._baixar_com_botao_na_linha = original

        self.assertTrue(ok)
        self.assertEqual(chamadas, ["Baixar"])

    def test_processar_pagina_baixa_mensal_antigo_sem_limite_de_60_meses(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "tr.z-listitem": FakeCollection(
                    [
                        FakeRow("01/2019", "Mensal"),
                    ],
                ),
                ".z-listbox-body tr": FakeCollection([]),
                "table tbody tr": FakeCollection([]),
                "body": FakeCollection(inner_text="01/2019 Mensal Baixar"),
            },
        )

        pasta_mensais = Path("C:/gdc-test/mensais")
        pasta_decimo = Path("C:/gdc-test/decimo")
        vistos: set[str] = set()
        chamadas: list[tuple[str, Path]] = []

        original = helper.portal_automation.clicar_baixar_na_linha

        def fake_clicar_baixar_na_linha(*, pasta_destino, competencia, tipo, **kwargs):
            chamadas.append((f"{competencia}|{tipo}", pasta_destino))
            return True

        helper.portal_automation.clicar_baixar_na_linha = fake_clicar_baixar_na_linha
        try:
            total = helper.portal_automation.processar_pagina(
                page,
                pasta_mensais,
                pasta_decimo,
                vistos,
                context=object(),
            )
        finally:
            helper.portal_automation.clicar_baixar_na_linha = original

        self.assertEqual(total, 1)
        self.assertEqual(len(chamadas), 1)
        self.assertTrue(str(chamadas[0][1]).endswith("mensais"))

    def test_processar_pagina_manda_decimo_para_pasta_separada(self):
        page = FakePage(
            url="https://portal.exemplo/contracheques",
            title="Contracheques",
            selectors={
                "tr.z-listitem": FakeCollection(
                    [
                        FakeRow("12/2025", "13º Salário"),
                    ],
                ),
                ".z-listbox-body tr": FakeCollection([]),
                "table tbody tr": FakeCollection([]),
                "body": FakeCollection(inner_text="12/2025 13º Salário Baixar"),
            },
        )

        pasta_mensais = Path("C:/gdc-test/mensais")
        pasta_decimo = Path("C:/gdc-test/decimo")
        vistos: set[str] = set()
        chamadas: list[tuple[str, Path]] = []

        original = helper.portal_automation.clicar_baixar_na_linha

        def fake_clicar_baixar_na_linha(*, pasta_destino, competencia, tipo, **kwargs):
            chamadas.append((f"{competencia}|{tipo}", pasta_destino))
            return True

        helper.portal_automation.clicar_baixar_na_linha = fake_clicar_baixar_na_linha
        try:
            total = helper.portal_automation.processar_pagina(
                page,
                pasta_mensais,
                pasta_decimo,
                vistos,
                context=object(),
            )
        finally:
            helper.portal_automation.clicar_baixar_na_linha = original

        self.assertEqual(total, 1)
        self.assertEqual(len(chamadas), 1)
        self.assertTrue(str(chamadas[0][1]).endswith("decimo"))


if __name__ == "__main__":
    unittest.main()
