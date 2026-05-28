from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import sys
import time
import unicodedata
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

try:
    import winreg
except ImportError:  # pragma: no cover - only available on Windows
    winreg = None

from config import (
    BACKEND_URL,
    BROWSER_TIMEOUT_MS,
    DOWNLOAD_KEYWORDS,
    DOWNLOAD_SELECTORS,
    DOWNLOAD_TIMEOUT_MS,
    DOWNLOAD_ROOT,
    HELPER_VERSION,
    PORTAL_URL,
)

import portal_automation


LOGGER = logging.getLogger("helper-contracheques")
DEBUG_MODE = False


def configurar_logger() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log(mensagem: str) -> None:
    if not DEBUG_MODE and mensagem.startswith("["):
        return
    LOGGER.info(mensagem)


def debug_log(mensagem: str) -> None:
    if DEBUG_MODE:
        LOGGER.info(mensagem)


def definir_modo_debug(ativo: bool) -> None:
    global DEBUG_MODE
    DEBUG_MODE = ativo
    os.environ["HELPER_DEBUG"] = "1" if ativo else "0"


def normalizar_texto(valor: str) -> str:
    texto = unicodedata.normalize("NFKD", valor or "")
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return re.sub(r"\s+", " ", texto).strip().casefold()


def sanitizar_candidato_para_log(candidato: str) -> str:
    texto = candidato.strip()
    if not texto:
        return texto

    if "token=" not in texto.casefold():
        return texto

    if texto.startswith("token="):
        return "token=[oculto]"

    parsed = urlparse(texto)
    if parsed.scheme:
        parametros = parse_qs(parsed.query, keep_blank_values=True)
        if "token" in parametros:
            parametros["token"] = ["[oculto]" for _ in parametros["token"]]
            query = urlencode(parametros, doseq=True)
            return parsed._replace(query=query).geturl()

    return re.sub(r"(?i)(token=)[^&#\s]+", r"\1[oculto]", texto)


def sanitizar_argv_para_log(argv: list[str]) -> list[str]:
    resultado: list[str] = []
    ocultar_proximo = False

    for argumento in argv:
        if ocultar_proximo:
            resultado.append("[oculto]")
            ocultar_proximo = False
            continue

        if argumento == "--token":
            resultado.append(argumento)
            ocultar_proximo = True
            continue

        if argumento.startswith("--token="):
            resultado.append("--token=[oculto]")
            continue

        resultado.append(sanitizar_candidato_para_log(argumento))

    return resultado


def slugify(valor: str, limite: int = 80) -> str:
    texto = re.sub(r"[^\w\-\. ]+", "", valor, flags=re.UNICODE).strip().replace(" ", "_")
    texto = re.sub(r"_+", "_", texto)
    return (texto or "contracheque")[:limite]


def criar_diretorio_temporario() -> Path:
    pasta = DOWNLOAD_ROOT / f"contracheques_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def exibir_cabecalho_interativo() -> None:
    print("==================================")
    print("Gestão de Carreira - Assistente")
    print("==================================")
    print()


def solicitar_token_interativo() -> str:
    exibir_cabecalho_interativo()
    try:
        print("Não consegui receber o token automaticamente.")
        return input("Cole seu token temporário gerado no site e aperte Enter:\n> ").strip()
    except EOFError:
        return ""


def aguardar_enter_para_sair() -> None:
    try:
        input("\nPressione Enter para sair...")
    except EOFError:
        pass


def exibir_erro_amigavel(mensagem: str) -> None:
    print()
    print(mensagem)
    aguardar_enter_para_sair()


def comando_protocolo_windows() -> str:
    executavel = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        return f'"{executavel}" "%1"'

    script = Path(__file__).resolve()
    return f'"{executavel}" "{script}" "%1"'


def registrar_protocolo_windows() -> None:
    if os.name != "nt" or winreg is None:
        return

    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\gestaodecarreira") as chave:
            winreg.SetValueEx(chave, None, 0, winreg.REG_SZ, "URL:Gestão de Carreira")
            winreg.SetValueEx(chave, "URL Protocol", 0, winreg.REG_SZ, "")
            with winreg.CreateKey(chave, r"shell\open\command") as comando:
                winreg.SetValueEx(comando, None, 0, winreg.REG_SZ, comando_protocolo_windows())
    except OSError as erro:
        log(f"[info] nao foi possivel registrar o protocolo gestaodecarreira: {erro}")


def extrair_token_de_candidato(candidato: str) -> str:
    texto = candidato.strip()
    if not texto:
        return ""

    if "://" not in texto and "token=" not in texto:
        return texto

    if texto.startswith("token="):
        return texto.split("=", 1)[1].strip()

    parsed = urlparse(texto)
    parametros = parse_qs(parsed.query)
    tokens = [item.strip() for item in parametros.get("token", []) if item.strip()]
    if tokens:
        return tokens[0]

    if parsed.scheme == "" and parsed.path.strip():
        return parsed.path.strip()

    return ""


def registrar_diagnostico_de_entrada(args: argparse.Namespace) -> None:
    log(f"[args] sys.argv={sanitizar_argv_para_log(sys.argv)}")
    log(f"[args] token_cli={'sim' if bool(str(getattr(args, 'token', '')).strip()) else 'nao'}")
    log(f"[args] import_url={'sim' if bool(str(getattr(args, 'import_url', '')).strip()) else 'nao'}")
    log(f"[args] import_uri={'sim' if bool(str(getattr(args, 'import_uri', '')).strip()) else 'nao'}")


def resolver_token(args: argparse.Namespace) -> tuple[str | None, str]:
    candidatos = [
        ("cli", getattr(args, "token", "")),
        ("protocolo", getattr(args, "import_url", "")),
        ("protocolo", getattr(args, "import_uri", "")),
    ]

    for origem, candidato in candidatos:
        texto_candidato = str(candidato or "").strip()
        log(f"[token] origem={origem} informado={'sim' if texto_candidato else 'nao'}")
        token = extrair_token_de_candidato(texto_candidato)
        log(f"[token] origem={origem} extraido={'sim' if token else 'nao'}")
        if token:
            return token, origem

    log("Não consegui receber o token automaticamente.")
    log("[token] entrando no modo manual")
    token_interativo = solicitar_token_interativo()
    if token_interativo:
        log("[token] origem=manual extraido=sim")
        return token_interativo, "manual"

    log("[token] origem=manual extraido=nao")
    exibir_erro_amigavel("Token obrigatório para iniciar a importação.")
    return None, "manual"


def exibir_diagnostico_inicial(exec_path: Path, origem: str, token: str | None, portal_url: str) -> None:
    print("====================================")
    print("Gestão de Carreira Assistente")
    print("====================================")
    print(f"Versão: {HELPER_VERSION}")
    print(f"Executavel: {exec_path}")
    print(f"Origem: {origem}")
    print(f"PORTAL_URL carregada: {portal_url}")
    print(f"Token recebido: {'sim' if token else 'nao'}")
    print("====================================")


def texto_elemento(locator) -> str:
    partes: list[str] = []
    for nome in ("aria-label", "title", "href"):
        try:
            valor = locator.get_attribute(nome)
        except Exception:
            valor = None
        if isinstance(valor, str) and valor.strip():
            partes.append(valor.strip())

    try:
        texto = locator.text_content() or ""
    except Exception:
        texto = ""

    if texto.strip():
        partes.append(texto.strip())

    return " | ".join(partes)


def elemento_visivel(locator) -> bool:
    try:
        if locator.count() == 0:
            return False
        return locator.first.is_visible()
    except Exception:
        return False


def texto_da_pagina(page) -> str:
    partes: list[str] = []

    try:
        corpo = page.locator("body").inner_text(timeout=3000)
        if isinstance(corpo, str) and corpo.strip():
            partes.append(corpo.strip())
    except Exception:
        pass

    try:
        titulo = page.title()
        if isinstance(titulo, str) and titulo.strip():
            partes.append(titulo.strip())
    except Exception:
        pass

    try:
        url = page.url
        if isinstance(url, str) and url.strip():
            partes.append(url.strip())
    except Exception:
        pass

    return " ".join(partes)


def _locators_visiveis(locator) -> list[object]:
    try:
        total = locator.count()
    except Exception:
        return []

    itens: list[object] = []
    for indice in range(total):
        item = locator.nth(indice)
        try:
            if item.is_visible():
                itens.append(item)
        except Exception:
            continue

    return itens


def _texto_visivel_na_pagina(page, termo: str) -> bool:
    return normalizar_texto(termo) in normalizar_texto(texto_da_pagina(page))


def _contar_elementos_visiveis_com_texto(page, termos: list[str]) -> int:
    seletores = ["button", "a", "[role='button']"]
    encontrados: list[str] = []

    for seletor in seletores:
        try:
            locator = page.locator(seletor)
        except Exception:
            continue

        for item in _locators_visiveis(locator):
            assinatura = normalizar_texto(texto_elemento(item))
            if not assinatura:
                continue

            if any(normalizar_texto(termo) in assinatura for termo in termos):
                if assinatura not in encontrados:
                    encontrados.append(assinatura)

    return len(encontrados)


def _contar_textos_visiveis(page, termos: list[str]) -> int:
    texto = normalizar_texto(texto_da_pagina(page))
    return sum(1 for termo in termos if normalizar_texto(termo) in texto)


def _contar_selector(page, seletor: str) -> int:
    try:
        return page.locator(seletor).count()
    except Exception:
        return 0


def _resumo_elemento_download(locator, seletor_base: str) -> dict[str, object]:
    assinatura = texto_elemento(locator)[:220]
    return {
        "seletor": seletor_base,
        "assinatura": assinatura,
        "visivel": True,
    }


def _coletar_amostras_download(page, limite: int = 10) -> list[dict[str, object]]:
    seletores = [
        "text=BAIXAR",
        "a:has-text('BAIXAR')",
        "button:has-text('BAIXAR')",
        "[role='button']:has-text('BAIXAR')",
        "input[value*='BAIXAR' i]",
        "text=EXIBIR",
        "a:has-text('EXIBIR')",
        "button:has-text('EXIBIR')",
        "[role='button']:has-text('EXIBIR')",
        "input[value*='EXIBIR' i]",
    ]

    amostras: list[dict[str, object]] = []
    vistos: set[str] = set()

    for seletor in seletores:
        try:
            locator = page.locator(seletor)
        except Exception:
            continue

        try:
            total = locator.count()
        except Exception:
            continue

        for indice in range(total):
            if len(amostras) >= limite:
                return amostras

            try:
                item = locator.nth(indice)
            except Exception:
                continue

            try:
                if not item.is_visible():
                    continue
            except Exception:
                continue

            resumo = _resumo_elemento_download(item, seletor)
            chave = normalizar_texto(f"{resumo['seletor']}|{resumo['assinatura']}")
            if chave in vistos:
                continue
            vistos.add(chave)
            amostras.append(resumo)

    return amostras


def diagnostico_pagina_contracheque(page) -> dict[str, object]:
    botoes_baixar = encontrar_botoes_baixar(page)
    botoes_exibir = encontrar_botoes_exibir(page)
    texto = normalizar_texto(texto_da_pagina(page))

    diagnostico = {
        "url": getattr(page, "url", ""),
        "title": "",
        "botoes_baixar_visiveis": len(botoes_baixar),
        "botoes_exibir_visiveis": len(botoes_exibir),
        "text_baixar": _contar_selector(page, "text=BAIXAR"),
        "text_exibir": _contar_selector(page, "text=EXIBIR"),
        "tem_consultar_contracheque": "consultar contracheque" in texto,
        "tem_mes_ano": "mes/ano" in texto or "mes ano" in texto,
        "tem_mensal": "mensal" in texto,
        "tem_consultar": _contar_elementos_visiveis_com_texto(page, ["consultar"]),
        "tem_baixar": len(botoes_baixar),
        "tem_exibir": len(botoes_exibir),
    }

    try:
        diagnostico["title"] = page.title()
    except Exception:
        diagnostico["title"] = ""

    return diagnostico


def _parece_alvo_por_termos(locator, assinatura: str, termos: tuple[str, ...]) -> bool:
    texto = normalizar_texto(assinatura)
    if any(termo in texto for termo in termos):
        return True

    for nome in ("aria-label", "title", "href", "download"):
        try:
            valor = locator.get_attribute(nome)
        except Exception:
            valor = None

        if not isinstance(valor, str) or not valor.strip():
            continue

        texto_atributo = normalizar_texto(valor)
        if nome == "download":
            return True
        if ".pdf" in texto_atributo:
            return True
        if any(termo in texto_atributo for termo in termos):
            return True

    return False


def encontrar_botoes_consultar(page) -> list[object]:
    seletores = [
        "button:has-text('Consultar')",
        "a:has-text('Consultar')",
        "button:has-text('CONSULTAR')",
        "a:has-text('CONSULTAR')",
        "button[aria-label*='consult' i]",
        "a[aria-label*='consult' i]",
        "[title*='consult' i]",
        "[role='button']:has-text('Consultar')",
    ]

    candidatos: list[object] = []
    vistos: set[str] = set()

    for seletor in seletores:
        try:
            locator = page.locator(seletor)
        except Exception:
            continue

        for item in _locators_visiveis(locator):
            assinatura = texto_elemento(item) or seletor
            chave = normalizar_texto(assinatura)
            if chave in vistos:
                continue
            if "consult" not in chave:
                continue
            vistos.add(chave)
            candidatos.append(item)

    return candidatos


def solicitar_continuacao_manual(mensagem: str) -> bool:
    try:
        input(f"{mensagem}\n")
        return True
    except EOFError:
        return False


def wait_until_paystub_page_ready(page) -> bool:
    log("Faça login no navegador aberto. Depois vá até a tela de contracheques. O assistente continuará automaticamente.")
    log("Procurando botões BAIXAR...")
    prazo = time.monotonic() + (15 * 60)
    ultimo_log = 0.0

    while time.monotonic() < prazo:
        try:
            portal_automation.fechar_avisos_se_existirem(page)
        except Exception:
            pass

        try:
            contexto = portal_automation.esperar_lista_em_alguma_frame(page, timeout_ms=2000)
            if portal_automation.localizar_linhas_documento(contexto).count() > 0:
                log_diagnostico_download(page)
                diagnostico = diagnostico_pagina_contracheque(page)
                log(
                    "[debug] "
                    f"url={diagnostico['url']} | "
                    f"title={diagnostico['title']} | "
                    f"baixar={diagnostico['botoes_baixar_visiveis']} | "
                    f"exibir={diagnostico['botoes_exibir_visiveis']} | "
                    f"consultar_contracheque={'sim' if diagnostico['tem_consultar_contracheque'] else 'nao'} | "
                    f"mes_ano={'sim' if diagnostico['tem_mes_ano'] else 'nao'} | "
                    f"mensal={'sim' if diagnostico['tem_mensal'] else 'nao'}"
                )
                log("Página de contracheques encontrada.")
                return True
        except Exception:
            pass

        if pagina_consultar_contracheque_pronta(page):
            log_diagnostico_download(page)
            diagnostico = diagnostico_pagina_contracheque(page)
            log(
                "[debug] "
                f"url={diagnostico['url']} | "
                f"title={diagnostico['title']} | "
                f"baixar={diagnostico['botoes_baixar_visiveis']} | "
                f"exibir={diagnostico['botoes_exibir_visiveis']} | "
                f"consultar_contracheque={'sim' if diagnostico['tem_consultar_contracheque'] else 'nao'} | "
                f"mes_ano={'sim' if diagnostico['tem_mes_ano'] else 'nao'} | "
                f"mensal={'sim' if diagnostico['tem_mensal'] else 'nao'}"
            )
            log("Página de contracheques encontrada.")
            return True

        agora = time.monotonic()
        if agora - ultimo_log >= 5:
            log_diagnostico_download(page)
            diagnostico = diagnostico_pagina_contracheque(page)
            log(
                "[debug] "
                f"url={diagnostico['url']} | "
                f"title={diagnostico['title']} | "
                f"baixar={diagnostico['botoes_baixar_visiveis']} | "
                f"exibir={diagnostico['botoes_exibir_visiveis']} | "
                f"consultar_contracheque={'sim' if diagnostico['tem_consultar_contracheque'] else 'nao'} | "
                f"mes_ano={'sim' if diagnostico['tem_mes_ano'] else 'nao'} | "
                f"mensal={'sim' if diagnostico['tem_mensal'] else 'nao'}"
            )
            log("Ainda não identifiquei a tela de contracheques.")
            ultimo_log = agora

        page.wait_for_timeout(1000)

    log("Não consegui identificar a página de contracheques automaticamente.")
    return solicitar_continuacao_manual("Se você já está vendo os botões BAIXAR, pressione Enter para continuar.")


def criar_sessao_requests(context, page) -> requests.Session:
    import requests

    sessao = requests.Session()
    try:
        sessao.headers.update({"User-Agent": page.evaluate("navigator.userAgent")})
    except Exception:
        pass

    for cookie in context.cookies():
        sessao.cookies.set(
            cookie.get("name", ""),
            cookie.get("value", ""),
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )

    return sessao


def baixar_url_com_sessao(sessao: requests.Session, url: str, destino: Path) -> None:
    import requests

    resposta = sessao.get(url, timeout=DOWNLOAD_TIMEOUT_MS / 1000, stream=True)
    if not resposta.ok:
        raise RuntimeError(f"Falha ao baixar {url} ({resposta.status_code}).")

    content_type = (resposta.headers.get("content-type") or "").lower()
    if "pdf" not in content_type and not url.lower().split("?", 1)[0].endswith(".pdf"):
        raise RuntimeError(f"Resposta nao parece PDF: {url}")

    with destino.open("wb") as arquivo:
        for bloco in resposta.iter_content(chunk_size=1024 * 64):
            if bloco:
                arquivo.write(bloco)


def baixar_um_documento(page, context, alvo, indice: int, total: int, pasta_saida: Path) -> Path:
    assinatura, locator = alvo
    log(f"[baixando] {indice}/{total} {assinatura[:120]}")

    destino = pasta_saida / f"{indice:03d}_{slugify(assinatura)}.pdf"

    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            locator.click(force=True)

        download = download_info.value
        nome_sugerido = download.suggested_filename or destino.name
        destino = pasta_saida / f"{indice:03d}_{slugify(nome_sugerido)}"
        if destino.suffix.lower() != ".pdf":
            destino = destino.with_suffix(".pdf")
        download.save_as(str(destino))
        return destino
    except Exception as erro_download:
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        except Exception:
            PlaywrightTimeoutError = Exception  # type: ignore[assignment]

        if not isinstance(erro_download, PlaywrightTimeoutError):
            raise

        href = None
        try:
            href = locator.get_attribute("href")
        except Exception:
            href = None

        if not href and page.url.lower().split("?", 1)[0].endswith(".pdf"):
            href = page.url

        if not href:
            raise RuntimeError("Botao encontrado, mas nenhum download direto foi detectado.")

        sessao = criar_sessao_requests(context, page)
        url = urljoin(page.url, href)
        baixar_url_com_sessao(sessao, url, destino)
        return destino


def clicar_botao_consultar(page) -> bool:
    botoes = encontrar_botoes_consultar(page)
    if not botoes:
        return False

    botao = botoes[0]
    assinatura = texto_elemento(botao) or "botão Consultar"
    log(f"[info] clicando em {assinatura[:120]}")

    try:
        botao.click(force=True)
        page.wait_for_timeout(1500)
        return True
    except Exception as erro:
        log(f"[falha] botao consultar -> {erro}")
        return False


def baixar_contracheques(page, context, pasta_saida: Path) -> list[Path]:
    alvos = encontrar_alvos_download(page)
    if not alvos:
        if pagina_consultar_contracheque_pronta(page):
            log_diagnostico_download(page)
        return []

    arquivos_baixados: list[Path] = []
    for indice, alvo in enumerate(alvos, start=1):
        try:
            arquivo = baixar_um_documento(page, context, alvo, indice, len(alvos), pasta_saida)
            arquivos_baixados.append(arquivo)
        except Exception as erro:
            assinatura, _ = alvo
            log(f"[falha] {assinatura[:120]} -> {erro}")

    return arquivos_baixados


def pedir_login_manual(_page) -> bool:
    log("[aguardando login] navegador aberto")
    log("[aguardando login] faça login no navegador aberto. Depois vá até a tela de contracheques. O assistente continuará automaticamente.")
    return solicitar_continuacao_manual("Se você já está na página de contracheques, pressione Enter para continuar.")


def baixar_um_documento_baixar(page, context, locator, indice: int, total: int, pasta_saida: Path) -> Path:
    log(f"Baixando {indice}/{total}...")

    destino = pasta_saida / f"{indice:03d}_contracheque.pdf"

    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            locator.click(force=True)

        download = download_info.value
        nome_sugerido = download.suggested_filename or destino.name
        destino = pasta_saida / f"{indice:03d}_{slugify(nome_sugerido)}"
        if destino.suffix.lower() != ".pdf":
            destino = destino.with_suffix(".pdf")
        download.save_as(str(destino))
        return destino
    except Exception as erro_download:
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        except Exception:
            PlaywrightTimeoutError = Exception  # type: ignore[assignment]

        if not isinstance(erro_download, PlaywrightTimeoutError):
            raise

        try:
            href = locator.get_attribute("href")
        except Exception:
            href = None

        if not href and page.url.lower().split("?", 1)[0].endswith(".pdf"):
            href = page.url

        if not href:
            raise RuntimeError("Botao encontrado, mas nenhum download direto foi detectado.")

        sessao = criar_sessao_requests(context, page)
        url = urljoin(page.url, href)
        baixar_url_com_sessao(sessao, url, destino)
        return destino


def baixar_contracheques_baixar(page, context, pasta_saida: Path) -> list[Path]:
    log("Procurando botões BAIXAR...")
    botoes = encontrar_botoes_baixar(page)
    if not botoes and clicar_botao_consultar(page):
        log("Atualizando lista após clicar em CONSULTAR...")
        botoes = encontrar_botoes_baixar(page)
    if not botoes:
        return []

    arquivos_baixados: list[Path] = []
    for indice, botao in enumerate(botoes, start=1):
        try:
            arquivo = baixar_um_documento_baixar(page, context, botao, indice, len(botoes), pasta_saida)
            arquivos_baixados.append(arquivo)
        except Exception as erro:
            log(f"[falha] botao BAIXAR {indice} -> {erro}")

    return arquivos_baixados


def encontrar_botoes_baixar(page) -> list[object]:
    return [item for assinatura, item in encontrar_alvos_download(page) if "baix" in normalizar_texto(assinatura)]


def encontrar_botoes_exibir(page) -> list[object]:
    return [item for assinatura, item in encontrar_alvos_download(page, agressivo=True) if "exib" in normalizar_texto(assinatura)]


def baixar_contracheques_baixar(page, context, pasta_saida: Path) -> list[Path]:
    log("Procurando botões BAIXAR...")
    log_diagnostico_download(page)

    botoes = encontrar_botoes_baixar(page)
    if not botoes and clicar_botao_consultar(page):
        log("Atualizando lista após clicar em CONSULTAR...")
        botoes = encontrar_botoes_baixar(page)

    if not botoes:
        exibir = encontrar_botoes_exibir(page)
        if exibir:
            log("Encontrei EXIBIR, tentando abrir os contracheques antes de baixar...")
            try:
                exibir[0].click(force=True)
                page.wait_for_timeout(1500)
            except Exception as erro:
                log(f"[falha] botao EXIBIR -> {erro}")
            log_diagnostico_download(page)
            botoes = encontrar_botoes_baixar(page)

    if not botoes and solicitar_continuacao_manual("Se você já está vendo os botões BAIXAR, pressione Enter para continuar."):
        log("Fazendo varredura agressiva de links clicáveis...")
        log_diagnostico_download(page)
        botoes = [item for assinatura, item in encontrar_alvos_download(page, agressivo=True) if "baix" in normalizar_texto(assinatura)]

    if not botoes:
        return []

    arquivos_baixados: list[Path] = []
    for indice, botao in enumerate(botoes, start=1):
        try:
            arquivo = baixar_um_documento_baixar(page, context, botao, indice, len(botoes), pasta_saida)
            arquivos_baixados.append(arquivo)
        except Exception as erro:
            log(f"[falha] botao BAIXAR {indice} -> {erro}")

    return arquivos_baixados


def iniciar_playwright():
    log("Carregando Playwright...")
    inicio = time.perf_counter()
    from playwright.sync_api import sync_playwright

    log(f"[tempo] Playwright carregado em {time.perf_counter() - inicio:.2f}s")
    return sync_playwright()


def abrir_navegador(playwright, headless: bool):
    if os.name == "nt":
        tentativas = [
            ("Microsoft Edge", lambda: playwright.chromium.launch(headless=headless, channel="msedge")),
            ("Google Chrome", lambda: playwright.chromium.launch(headless=headless, channel="chrome")),
            ("Chromium do Playwright", lambda: playwright.chromium.launch(headless=headless)),
        ]
    else:
        tentativas = [
            ("Chromium do Playwright", lambda: playwright.chromium.launch(headless=headless)),
            ("Google Chrome", lambda: playwright.chromium.launch(headless=headless, channel="chrome")),
        ]

    ultimo_erro: Exception | None = None
    for nome, abrir in tentativas:
        try:
            log(f"[info] abrindo navegador: {nome}")
            browser = abrir()
            log(f"[info] navegador aberto com sucesso: {nome}")
            return browser
        except Exception as erro:
            ultimo_erro = erro
            log(f"[info] falha ao abrir {nome}: {erro}")

    raise RuntimeError(
        "Nao foi possivel abrir um navegador. O Microsoft Edge ou o Google Chrome precisam estar instalados, ou o Chromium do Playwright precisa estar disponivel.",
    ) from ultimo_erro


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Helper local para baixar e enviar contracheques.")
    parser.add_argument("import_uri", nargs="?", default="", help="URI opcional do protocolo gestaodecarreira://.")
    parser.add_argument("--token", default="", help="Token temporario gerado pelo sistema.")
    parser.add_argument("--import-url", default="", help="URI opcional usada pelo protocolo gestaodecarreira://.")
    parser.add_argument("--backend-url", default=BACKEND_URL, help="URL do backend.")
    parser.add_argument("--portal-url", default=PORTAL_URL, help="URL inicial do portal gov.br.")
    parser.add_argument(
        "--download-dir",
        default="",
        help="Pasta opcional para guardar PDFs antes do envio. Se vazio, usa pasta temporaria do helper.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa navegador sem interface. Nao recomendado para login manual.",
    )
    return parser.parse_args()


def main() -> int:
    inicio_programa = time.perf_counter()
    print("Iniciando assistente...", flush=True)
    print("Preparando navegador...", flush=True)
    configurar_logger()
    registrar_protocolo_windows()
    args = parse_args()
    registrar_diagnostico_de_entrada(args)

    token, origem_token = resolver_token(args)
    if not token:
        return 1

    log(f"[tempo] programa_iniciado={time.perf_counter() - inicio_programa:.2f}s")
    exibir_diagnostico_inicial(Path(sys.executable).resolve(), origem_token, token, args.portal_url)
    log("Se o navegador demorar, aguarde alguns segundos.")
    log("Faça login no Portal do Servidor e vá até a tela com os botões BAIXAR.")

    pasta_saida = Path(args.download_dir).expanduser().resolve() if args.download_dir else criar_diretorio_temporario()
    pasta_saida.mkdir(parents=True, exist_ok=True)

    browser = None
    resultado = 1
    try:
        log("Carregando navegador automático...")
        with iniciar_playwright() as playwright:
            try:
                inicio_navegador = time.perf_counter()
                log("Abrindo navegador...")
                browser = abrir_navegador(playwright, args.headless)
                log(f"[tempo] navegador_aberto={time.perf_counter() - inicio_navegador:.2f}s")
                context = browser.new_context(accept_downloads=True)
                page = context.new_page()
                page.set_default_timeout(BROWSER_TIMEOUT_MS)
                log("Abrindo Portal do Servidor...")
                inicio_portal = time.perf_counter()
                page.goto(args.portal_url, wait_until="domcontentloaded")
                log(f"[tempo] portal_aberto={time.perf_counter() - inicio_portal:.2f}s")
                log("Aguardando login...")

                if not wait_until_paystub_page_ready(page):
                    raise RuntimeError("Não consegui confirmar a tela de contracheques.")

                log("Página pronta.")
                log("Iniciando download automático dos contracheques...")

                arquivos = baixar_contracheques_baixar(page, context, pasta_saida)
                if not arquivos:
                    log("Não consegui encontrar botões de download automaticamente.")
                    if pedir_login_manual(page):
                        arquivos = baixar_contracheques_baixar(page, context, pasta_saida)

                if not arquivos:
                    raise RuntimeError("Nenhum PDF foi encontrado para baixar.")

                inicio_upload_import = time.perf_counter()
                from upload_service import upload_pdfs_para_backend
                log(f"[tempo] import_upload_service={time.perf_counter() - inicio_upload_import:.2f}s")
                log(f"Encontrados {len(arquivos)} contracheques.")
                log(f"[enviando] {len(arquivos)} arquivo(s) para backend")
                resultado_upload = upload_pdfs_para_backend(
                    arquivos,
                    token,
                    backend_url=args.backend_url,
                )
                log("Upload concluído.")
                log(f"[concluído] batch_id={resultado_upload.batch_id} status={resultado_upload.status}")
                resultado = 0
            except Exception as erro:
                exibir_erro_amigavel("Ocorreu um erro, mas o navegador ficará aberto para diagnóstico. Pressione Enter para fechar.")
                log(f"[falha] {erro}")
                try:
                    solicitar_continuacao_manual("Ocorreu um erro, mas o navegador ficará aberto para diagnóstico. Pressione Enter para fechar.")
                except Exception:
                    pass

        return resultado
    except Exception as erro:
        exibir_erro_amigavel("Não foi possível concluir a importação agora. Verifique o assistente e tente novamente.")
        log(f"[falha] {erro}")
        return 1
    finally:
        try:
            if browser is not None:
                browser.close()
        except Exception:
            pass

        if args.download_dir:
            log(f"[info] PDFs mantidos em {pasta_saida}")
        else:
            try:
                shutil.rmtree(pasta_saida)
            except Exception:
                pass


def _locator_count(locator) -> int:
    try:
        return locator.count()
    except Exception:
        return 0


def _primeiros_elementos_visiveis(locator, limite: int = 10) -> list[object]:
    try:
        total = locator.count()
    except Exception:
        return []

    itens: list[object] = []
    for indice in range(min(total, limite)):
        try:
            item = locator.nth(indice)
        except Exception:
            continue
        try:
            if item.is_visible():
                itens.append(item)
        except Exception:
            continue
    return itens


def _resumo_elemento_debug(locator) -> tuple[str, str, str]:
    tag = "desconhecido"
    html = ""
    try:
        tag = locator.evaluate("(el) => el.tagName")
    except Exception:
        try:
            tag = locator.get_attribute("tagName") or tag
        except Exception:
            pass

    try:
        html = locator.evaluate("(el) => el.outerHTML")
        if isinstance(html, str):
            html = re.sub(r"\s+", " ", html).strip()
            if len(html) > 220:
                html = html[:220] + "..."
    except Exception:
        try:
            html = texto_elemento(locator)[:220]
        except Exception:
            html = ""

    try:
        visivel = "sim" if locator.is_visible() else "nao"
    except Exception:
        visivel = "desconhecido"

    return tag, html, visivel


def log_diagnostico_download(page, prefixo: str = "[debug]") -> None:
    baixar_role = _locator_count(page.get_by_role("button", name=re.compile(r"baixar", re.I)))
    baixar_button = _locator_count(page.locator("button:has-text('Baixar')"))
    baixar_text = _locator_count(page.locator("text=Baixar"))
    baixar_role_button = _locator_count(page.locator("[role='button']:has-text('Baixar')"))
    exibir_button = _locator_count(page.locator("button:has-text('Exibir')"))
    exibir_text = _locator_count(page.locator("text=Exibir"))

    log(
        f"{prefixo} "
        f"baixar(get_by_role,re.I)={baixar_role} | "
        f"baixar(button:has-text('Baixar'))={baixar_button} | "
        f"baixar(text=Baixar)={baixar_text} | "
        f"baixar([role='button']:has-text('Baixar'))={baixar_role_button} | "
        f"exibir(button:has-text('Exibir'))={exibir_button} | "
        f"exibir(text=Exibir)={exibir_text}"
    )

    amostras: list[object] = []
    for locator in (
        page.get_by_role("button", name=re.compile(r"baixar", re.I)),
        page.locator("button:has-text('Baixar')"),
        page.locator("text=Baixar"),
        page.locator("[role='button']:has-text('Baixar')"),
    ):
        amostras.extend(_primeiros_elementos_visiveis(locator, limite=10))

    vistos: set[str] = set()
    for indice, item in enumerate(amostras[:10], start=1):
        assinatura = texto_elemento(item) or "baixar"
        chave = normalizar_texto(assinatura)
        if chave in vistos:
            continue
        vistos.add(chave)
        tag, html, visivel = _resumo_elemento_debug(item)
        log(
            f"{prefixo} alvo[{indice}] tag={tag} | visivel={visivel} | html={html}"
        )


def _locators_baixar_robustos(page) -> list[tuple[str, object]]:
    candidatos: list[tuple[str, object]] = []
    vistos: set[str] = set()

    seletores = [
        ("get_by_role(button, /baixar/i)", lambda: page.get_by_role("button", name=re.compile(r"baixar", re.I))),
        ("button:has-text('Baixar')", lambda: page.locator("button:has-text('Baixar')")),
        ("a:has-text('Baixar')", lambda: page.locator("a:has-text('Baixar')")),
        ("[role='button']:has-text('Baixar')", lambda: page.locator("[role='button']:has-text('Baixar')")),
        ("text=Baixar", lambda: page.locator("text=Baixar")),
        ("input[value*='Baixar' i]", lambda: page.locator("input[value*='Baixar' i]")),
        ("a[href*='pdf' i]", lambda: page.locator("a[href*='pdf' i]")),
        ("a[href*='download' i]", lambda: page.locator("a[href*='download' i]")),
        ("a[href*='contracheque' i]", lambda: page.locator("a[href*='contracheque' i]")),
        ("a[download]", lambda: page.locator("a[download]")),
        ("button[download]", lambda: page.locator("button[download]")),
    ]

    for nome, factory in seletores:
        try:
            locator = factory()
        except Exception:
            continue

        for item in _primeiros_elementos_visiveis(locator, limite=100):
            assinatura = texto_elemento(item) or nome
            chave = normalizar_texto(assinatura)
            if chave in vistos:
                continue
            if "baix" not in chave and "download" not in chave and ".pdf" not in chave:
                continue
            vistos.add(chave)
            candidatos.append((assinatura, item))

    return candidatos


def encontrar_botoes_baixar(page) -> list[object]:
    return [item for _, item in _locators_baixar_robustos(page)]


def encontrar_botoes_exibir(page) -> list[object]:
    candidatos: list[object] = []
    vistos: set[str] = set()
    seletores = [
        lambda: page.get_by_role("button", name=re.compile(r"exibir", re.I)),
        lambda: page.locator("button:has-text('Exibir')"),
        lambda: page.locator("button:has-text('EXIBIR')"),
        lambda: page.locator("a:has-text('Exibir')"),
        lambda: page.locator("a:has-text('EXIBIR')"),
        lambda: page.locator("[role='button']:has-text('Exibir')"),
        lambda: page.locator("[role='button']:has-text('EXIBIR')"),
        lambda: page.locator("text=Exibir"),
        lambda: page.locator("text=EXIBIR"),
    ]

    for factory in seletores:
        try:
            locator = factory()
        except Exception:
            continue

        for item in _primeiros_elementos_visiveis(locator, limite=100):
            assinatura = texto_elemento(item) or "exibir"
            chave = normalizar_texto(assinatura)
            if chave in vistos:
                continue
            vistos.add(chave)
            candidatos.append(item)

    return candidatos


def pagina_consultar_contracheque_pronta(page) -> bool:
    if _locator_count(page.get_by_role("button", name=re.compile(r"baixar", re.I))) > 0:
        return True
    if _locator_count(page.locator("button:has-text('Baixar')")) > 0:
        return True
    if _locator_count(page.locator("text=Baixar")) > 0:
        return True
    if _locator_count(page.locator("button:has-text('Exibir')")) > 0:
        return True
    if _locator_count(page.locator("text=Exibir")) > 0:
        return True
    if len(encontrar_botoes_baixar(page)) > 0:
        return True
    if len(encontrar_botoes_exibir(page)) > 0:
        return True

    texto = normalizar_texto(texto_da_pagina(page))
    if not texto:
        return False

    sinais = 0
    if "consultar contracheque" in texto:
        sinais += 1
    if "mes/ano" in texto or "mes ano" in texto or ("mes" in texto and "ano" in texto):
        sinais += 1
    if "mensal" in texto:
        sinais += 1

    return sinais >= 3


def encontrar_alvos_download(page, agressivo: bool = False) -> list[tuple[str, object]]:
    candidatos: list[tuple[str, object]] = []
    vistos: set[str] = set()

    for assinatura, item in _locators_baixar_robustos(page):
        chave = normalizar_texto(assinatura)
        if chave in vistos:
            continue
        vistos.add(chave)
        candidatos.append((assinatura, item))

    for item in encontrar_botoes_exibir(page):
        assinatura = texto_elemento(item) or "exibir"
        chave = normalizar_texto(assinatura)
        if chave in vistos:
            continue
        vistos.add(chave)
        candidatos.append((assinatura, item))

    if agressivo:
        extras = [
            "button",
            "a",
            "[role='button']",
            "input[type='button']",
            "input[type='submit']",
        ]
        for seletor in extras:
            try:
                locator = page.locator(seletor)
            except Exception:
                continue
            for item in _primeiros_elementos_visiveis(locator, limite=100):
                assinatura = texto_elemento(item) or seletor
                chave = normalizar_texto(assinatura)
                if chave in vistos:
                    continue
                if any(termo in chave for termo in DOWNLOAD_KEYWORDS) or ".pdf" in chave:
                    vistos.add(chave)
                    candidatos.append((assinatura, item))

    return candidatos


def baixar_contracheques_baixar(page, context, pasta_saida: Path) -> list[Path]:
    log("Procurando botões BAIXAR...")
    log_diagnostico_download(page)

    botoes = encontrar_botoes_baixar(page)
    if not botoes and clicar_botao_consultar(page):
        log("Atualizando lista após clicar em CONSULTAR...")
        botoes = encontrar_botoes_baixar(page)

    if not botoes:
        exibir = encontrar_botoes_exibir(page)
        if exibir:
            log("Encontrei EXIBIR, tentando abrir os contracheques antes de baixar...")
            try:
                exibir[0].click(force=True)
                page.wait_for_timeout(1500)
            except Exception as erro:
                log(f"[falha] botao EXIBIR -> {erro}")
            log_diagnostico_download(page)
            botoes = encontrar_botoes_baixar(page)

    if not botoes and solicitar_continuacao_manual("Se você já está vendo os botões BAIXAR, pressione Enter para continuar."):
        log("Fazendo varredura agressiva de links clicáveis...")
        log_diagnostico_download(page)
        botoes = [item for _, item in encontrar_alvos_download(page, agressivo=True)]

    if not botoes:
        return []

    arquivos_baixados: list[Path] = []
    for indice, botao in enumerate(botoes, start=1):
        try:
            arquivo = baixar_um_documento_baixar(page, context, botao, indice, len(botoes), pasta_saida)
            arquivos_baixados.append(arquivo)
        except Exception as erro:
            log(f"[falha] botao BAIXAR {indice} -> {erro}")

    return arquivos_baixados


def _contextos_de_diagnostico(page) -> list[tuple[str, object]]:
    contextos: list[tuple[str, object]] = [("page", page)]
    frames = getattr(page, "frames", None) or []
    indice = 0

    for frame in frames:
        try:
            if getattr(frame, "parent_frame", None) is None:
                continue
        except Exception:
            pass

        indice += 1
        contextos.append((f"frame[{indice}]", frame))

    return contextos


def _contar_em_contextos(page, selector: str, **kwargs) -> int:
    total = 0
    for _, contexto in _contextos_de_diagnostico(page):
        try:
            locator = contexto.locator(selector, **kwargs)
        except TypeError:
            locator = contexto.locator(selector)
        except Exception:
            continue
        total += _locator_count(locator)
    return total


def _contar_texto_em_contextos(page, padrao) -> int:
    total = 0
    for _, contexto in _contextos_de_diagnostico(page):
        try:
            locator = contexto.get_by_text(padrao)
        except Exception:
            continue
        total += _locator_count(locator)
    return total


def _caminho_debug_portal_contracheque(nome_arquivo: str) -> Path:
    candidatos = [
        Path.cwd(),
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home(),
        Path(tempfile.gettempdir()),
    ]

    for base in candidatos:
        try:
            base.mkdir(parents=True, exist_ok=True)
            teste = base / ".gdc_write_test"
            teste.write_text("ok", encoding="utf-8")
            try:
                teste.unlink()
            except Exception:
                pass
            return base / nome_arquivo
        except Exception:
            continue

    return Path(tempfile.gettempdir()) / nome_arquivo


def _seguro_texto(locator) -> str:
    try:
        texto = locator.inner_text(timeout=1000)
        if isinstance(texto, str) and texto.strip():
            return texto.strip()
    except Exception:
        pass

    try:
        texto = locator.text_content() or ""
        if isinstance(texto, str) and texto.strip():
            return texto.strip()
    except Exception:
        pass

    return ""


def _detalhes_elemento(locator) -> dict[str, object]:
    detalhes: dict[str, object] = {
        "tagName": "desconhecido",
        "id": "",
        "class": "",
        "inner_text": "",
        "is_visible": "desconhecido",
        "is_enabled": "desconhecido",
        "bounding_box": None,
    }

    for atributo in ("id", "class"):
        try:
            valor = locator.get_attribute(atributo)
        except Exception:
            valor = None
        if isinstance(valor, str):
            detalhes[atributo] = valor

    try:
        detalhes["tagName"] = locator.evaluate("(el) => el.tagName")
    except Exception:
        try:
            detalhes["tagName"] = locator.get_attribute("tagName") or detalhes["tagName"]
        except Exception:
            pass

    detalhes["inner_text"] = _seguro_texto(locator)

    try:
        detalhes["is_visible"] = locator.is_visible()
    except Exception:
        pass

    try:
        detalhes["is_enabled"] = locator.is_enabled()
    except Exception:
        pass

    try:
        detalhes["bounding_box"] = locator.bounding_box()
    except Exception:
        pass

    return detalhes


def _chave_elemento(locator) -> str:
    detalhes = _detalhes_elemento(locator)
    return normalizar_texto(
        "|".join(
            [
                str(detalhes.get("tagName", "")),
                str(detalhes.get("id", "")),
                str(detalhes.get("class", "")),
                str(detalhes.get("inner_text", "")),
                str(detalhes.get("bounding_box", "")),
            ],
        ),
    )


def _dump_botoes_contexto(rotulo: str, contexto) -> None:
    try:
        total = contexto.locator("button").count()
    except Exception:
        total = 0

    print(f"[dom] {rotulo} buttons={total}", flush=True)
    for indice in range(total):
        try:
            locator = contexto.locator("button").nth(indice)
        except Exception:
            continue

        detalhes = _detalhes_elemento(locator)
        print(
            "[dom] "
            f"{rotulo} button[{indice + 1}/{total}] "
            f"tagName={detalhes['tagName']} | "
            f"id={detalhes['id']} | "
            f"class={detalhes['class']} | "
            f"inner_text={detalhes['inner_text']} | "
            f"is_visible={detalhes['is_visible']} | "
            f"is_enabled={detalhes['is_enabled']} | "
            f"bounding_box={detalhes['bounding_box']}",
            flush=True,
        )


def _aguardar_pagina_estabilizar(page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    try:
        page.wait_for_timeout(1000)
    except Exception:
        pass


def salvar_diagnostico_portal_contracheque(page) -> None:
    caminho_html = _caminho_debug_portal_contracheque("debug_portal_contracheque.html")
    caminho_png = _caminho_debug_portal_contracheque("debug_portal_contracheque.png")

    try:
        html = page.content()
        caminho_html.write_text(html, encoding="utf-8")
        log(f"[debug] html salvo em {caminho_html}")
    except Exception as erro:
        log(f"[debug] falha ao salvar html -> {erro}")

    try:
        page.screenshot(path=str(caminho_png), full_page=True)
        log(f"[debug] screenshot salvo em {caminho_png}")
    except Exception as erro:
        log(f"[debug] falha ao salvar screenshot -> {erro}")


def log_diagnostico_download(page, prefixo: str = "[debug]") -> None:
    print(f"url= {getattr(page, 'url', '')}", flush=True)
    try:
        title = page.title()
    except Exception:
        title = ""
    print(f"title= {title}", flush=True)
    print(f"buttons= {_contar_em_contextos(page, 'button')}", flush=True)
    print(f"baixar_text= {_contar_texto_em_contextos(page, re.compile(r'baixar', re.I))}", flush=True)
    print(
        f"baixar_button= {_contar_em_contextos(page, 'button', has_text=re.compile(r'baixar', re.I))}",
        flush=True,
    )
    print(
        f"baixar_css= {_contar_em_contextos(page, 'button.btn-outline-primary2', has_text=re.compile(r'baixar', re.I))}",
        flush=True,
    )
    print(f"exibir_text= {_contar_texto_em_contextos(page, re.compile(r'exibir', re.I))}", flush=True)
    print(
        f"exibir_button= {_contar_em_contextos(page, 'button', has_text=re.compile(r'exibir', re.I))}",
        flush=True,
    )

    for rotulo, contexto in _contextos_de_diagnostico(page):
        try:
            url_contexto = getattr(contexto, "url", "")
        except Exception:
            url_contexto = ""

        try:
            baixar_re = _locator_count(contexto.locator("button", has_text=re.compile(r"baixar", re.I)))
        except Exception:
            baixar_re = 0

        try:
            baixar_css = _locator_count(
                contexto.locator("button.btn-outline-primary2", has_text=re.compile(r"baixar", re.I)),
            )
        except Exception:
            baixar_css = 0

        try:
            exibir_re = _locator_count(contexto.locator("button", has_text=re.compile(r"exibir", re.I)))
        except Exception:
            exibir_re = 0

        try:
            text_baixar = _locator_count(contexto.get_by_text(re.compile(r"baixar", re.I)))
        except Exception:
            text_baixar = 0

        print(
            f"[dom] {rotulo} url={url_contexto} baixar_re={baixar_re} "
            f"baixar_css={baixar_css} exibir_re={exibir_re} text_baixar={text_baixar}",
            flush=True,
        )
        _dump_botoes_contexto(rotulo, contexto)


def _locators_baixar_robustos(page) -> list[tuple[str, object]]:
    candidatos: list[tuple[str, object]] = []
    vistos: set[str] = set()

    seletores = [
        ("button.btn-outline-primary2", lambda contexto: contexto.locator("button.btn-outline-primary2", has_text=re.compile(r"baixar", re.I))),
        ("button has_text baixar", lambda contexto: contexto.locator("button", has_text=re.compile(r"baixar", re.I))),
        ("button:has-text('Baixar')", lambda contexto: contexto.locator("button:has-text('Baixar')")),
        ("a:has-text('Baixar')", lambda contexto: contexto.locator("a:has-text('Baixar')")),
        ("[role='button']:has-text('Baixar')", lambda contexto: contexto.locator("[role='button']:has-text('Baixar')")),
        ("text=Baixar", lambda contexto: contexto.get_by_text(re.compile(r"baixar", re.I))),
        ("input[value*='Baixar' i]", lambda contexto: contexto.locator("input[value*='Baixar' i]")),
        ("a[href*='pdf' i]", lambda contexto: contexto.locator("a[href*='pdf' i]")),
        ("a[href*='download' i]", lambda contexto: contexto.locator("a[href*='download' i]")),
        ("a[href*='contracheque' i]", lambda contexto: contexto.locator("a[href*='contracheque' i]")),
        ("a[download]", lambda contexto: contexto.locator("a[download]")),
        ("button[download]", lambda contexto: contexto.locator("button[download]")),
    ]

    for rotulo, factory in seletores:
        for contexto_rotulo, contexto in _contextos_de_diagnostico(page):
            try:
                locator = factory(contexto)
            except Exception:
                continue

            try:
                total = locator.count()
            except Exception:
                continue

            for indice in range(total):
                try:
                    item = locator.nth(indice)
                except Exception:
                    continue

                try:
                    visivel = item.is_visible()
                except Exception:
                    visivel = False

                try:
                    bbox = item.bounding_box()
                except Exception:
                    bbox = None

                if not visivel and not bbox:
                    continue

                chave = _chave_elemento(item)
                if chave in vistos:
                    continue
                vistos.add(chave)
                assinatura = texto_elemento(item) or f"{contexto_rotulo}:{rotulo}"
                candidatos.append((assinatura, item))

    return candidatos


def encontrar_botoes_baixar(page) -> list[object]:
    return [item for _, item in _locators_baixar_robustos(page)]


def _locators_exibir_robustos(page) -> list[tuple[str, object]]:
    candidatos: list[tuple[str, object]] = []
    vistos: set[str] = set()

    seletores = [
        ("button.btn-primary2", lambda contexto: contexto.locator("button.btn-primary2", has_text=re.compile(r"exibir", re.I))),
        ("button has_text exibir", lambda contexto: contexto.locator("button", has_text=re.compile(r"exibir", re.I))),
        ("button:has-text('Exibir')", lambda contexto: contexto.locator("button:has-text('Exibir')")),
        ("a:has-text('Exibir')", lambda contexto: contexto.locator("a:has-text('Exibir')")),
        ("[role='button']:has-text('Exibir')", lambda contexto: contexto.locator("[role='button']:has-text('Exibir')")),
        ("text=Exibir", lambda contexto: contexto.get_by_text(re.compile(r"exibir", re.I))),
    ]

    for rotulo, factory in seletores:
        for contexto_rotulo, contexto in _contextos_de_diagnostico(page):
            try:
                locator = factory(contexto)
            except Exception:
                continue

            try:
                total = locator.count()
            except Exception:
                continue

            for indice in range(total):
                try:
                    item = locator.nth(indice)
                except Exception:
                    continue

                try:
                    visivel = item.is_visible()
                except Exception:
                    visivel = False

                try:
                    bbox = item.bounding_box()
                except Exception:
                    bbox = None

                if not visivel and not bbox:
                    continue

                chave = _chave_elemento(item)
                if chave in vistos:
                    continue
                vistos.add(chave)
                assinatura = texto_elemento(item) or f"{contexto_rotulo}:{rotulo}"
                candidatos.append((assinatura, item))

    return candidatos


def encontrar_botoes_exibir(page) -> list[object]:
    return [item for _, item in _locators_exibir_robustos(page)]


def pagina_consultar_contracheque_pronta(page) -> bool:
    if len(encontrar_botoes_baixar(page)) > 0:
        return True
    if len(encontrar_botoes_exibir(page)) > 0:
        return True
    if _contar_texto_em_contextos(page, re.compile(r"baixar", re.I)) > 0:
        return True
    if _contar_texto_em_contextos(page, re.compile(r"exibir", re.I)) > 0:
        return True

    texto = normalizar_texto(texto_da_pagina(page))
    if not texto:
        return False

    sinais = 0
    if "consultar contracheque" in texto:
        sinais += 1
    if "mes/ano" in texto or "mes ano" in texto or ("mes" in texto and "ano" in texto):
        sinais += 1
    if "mensal" in texto:
        sinais += 1

    return sinais >= 3


def encontrar_alvos_download(page, agressivo: bool = False) -> list[tuple[str, object]]:
    candidatos: list[tuple[str, object]] = []
    vistos: set[str] = set()

    for assinatura, item in _locators_baixar_robustos(page):
        chave = _chave_elemento(item)
        if chave in vistos:
            continue
        vistos.add(chave)
        candidatos.append((assinatura, item))

    for assinatura, item in _locators_exibir_robustos(page):
        chave = _chave_elemento(item)
        if chave in vistos:
            continue
        vistos.add(chave)
        candidatos.append((assinatura, item))

    if agressivo:
        extras = [
            "button",
            "a",
            "[role='button']",
            "input[type='button']",
            "input[type='submit']",
        ]
        for seletor in extras:
            for contexto_rotulo, contexto in _contextos_de_diagnostico(page):
                try:
                    locator = contexto.locator(seletor)
                except Exception:
                    continue

                try:
                    total = locator.count()
                except Exception:
                    continue

                for indice in range(total):
                    try:
                        item = locator.nth(indice)
                    except Exception:
                        continue

                    try:
                        visivel = item.is_visible()
                    except Exception:
                        visivel = False

                    try:
                        bbox = item.bounding_box()
                    except Exception:
                        bbox = None

                    if not visivel and not bbox:
                        continue

                    chave = _chave_elemento(item)
                    if chave in vistos:
                        continue

                    assinatura = texto_elemento(item) or f"{contexto_rotulo}:{seletor}"
                    chave_textual = normalizar_texto(assinatura)
                    if any(termo in chave_textual for termo in DOWNLOAD_KEYWORDS) or ".pdf" in chave_textual:
                        vistos.add(chave)
                        candidatos.append((assinatura, item))

    return candidatos


def _clicar_locator_download(locator) -> None:
    try:
        locator.scroll_into_view_if_needed(timeout=5000)
    except Exception:
        pass

    try:
        locator.click(force=True)
        return
    except Exception:
        try:
            bbox = locator.bounding_box()
        except Exception:
            bbox = None

        if bbox:
            locator.click(force=True)
            return

        raise


def baixar_um_documento_baixar(page, context, locator, indice: int, total: int, pasta_saida: Path) -> Path:
    log(f"Baixando {indice}/{total}...")

    destino = pasta_saida / f"{indice:03d}_contracheque.pdf"

    try:
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            _clicar_locator_download(locator)

        download = download_info.value
        nome_sugerido = download.suggested_filename or destino.name
        destino = pasta_saida / f"{indice:03d}_{slugify(nome_sugerido)}"
        if destino.suffix.lower() != ".pdf":
            destino = destino.with_suffix(".pdf")
        download.save_as(str(destino))
        return destino
    except Exception as erro_download:
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        except Exception:
            PlaywrightTimeoutError = Exception  # type: ignore[assignment]

        if not isinstance(erro_download, PlaywrightTimeoutError):
            raise

        try:
            href = locator.get_attribute("href")
        except Exception:
            href = None

        if not href and page.url.lower().split("?", 1)[0].endswith(".pdf"):
            href = page.url

        if not href:
            raise RuntimeError("Botao encontrado, mas nenhum download direto foi detectado.")

        sessao = criar_sessao_requests(context, page)
        url = urljoin(page.url, href)
        baixar_url_com_sessao(sessao, url, destino)
        return destino


def baixar_contracheques_baixar(page, context, pasta_saida: Path) -> list[Path]:
    log("Procurando botões BAIXAR...")
    _aguardar_pagina_estabilizar(page)
    salvar_diagnostico_portal_contracheque(page)
    log_diagnostico_download(page)

    arquivos_antes = {
        p.resolve()
        for p in pasta_saida.rglob("*.pdf")
        if p.is_file()
    }
    vistos: set[str] = set()
    pasta_mensais = pasta_saida / "mensais_ultimos_60_meses"
    pasta_decimo = pasta_saida / "decimo_terceiro"
    pasta_mensais.mkdir(parents=True, exist_ok=True)
    pasta_decimo.mkdir(parents=True, exist_ok=True)

    pagina_atual = portal_automation.encontrar_pagina_com_lista_flexivel(page)
    total_baixados = 0

    while True:
        try:
            pagina_atual = portal_automation.encontrar_pagina_com_lista_flexivel(pagina_atual)
            total_baixados += portal_automation.processar_pagina(
                pagina_atual,
                pasta_mensais,
                pasta_decimo,
                vistos,
                context=context,
            )
        except Exception as erro:
            log(f"[falha] processar_pagina -> {erro}")
            break

        try:
            avancou = portal_automation.ir_para_proxima_pagina(pagina_atual)
        except Exception as erro:
            log(f"[falha] ir_para_proxima_pagina -> {erro}")
            break

        if not avancou:
            break

    arquivos_baixados = sorted(
        p
        for p in pasta_saida.rglob("*.pdf")
        if p.is_file() and p.resolve() not in arquivos_antes
    )
    log(f"[info] total_baixados={total_baixados} | arquivos_encontrados={len(arquivos_baixados)}")
    return arquivos_baixados


if __name__ == "__main__":
    raise SystemExit(main())
