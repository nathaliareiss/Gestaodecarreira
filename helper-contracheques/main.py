from __future__ import annotations

import argparse
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from config import (
    BACKEND_URL,
    BROWSER_TIMEOUT_MS,
    DOWNLOAD_KEYWORDS,
    DOWNLOAD_SELECTORS,
    DOWNLOAD_TIMEOUT_MS,
    DOWNLOAD_ROOT,
    PORTAL_URL,
)
from upload_service import UploadError, upload_pdfs_para_backend


LOGGER = logging.getLogger("helper-contracheques")


def configurar_logger() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log(mensagem: str) -> None:
    LOGGER.info(mensagem)


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
        return input("Cole seu token temporário gerado no site:\n> ").strip()
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


def resolver_token(args: argparse.Namespace) -> str | None:
    candidatos = [
        getattr(args, "token", ""),
        getattr(args, "import_url", ""),
        getattr(args, "import_uri", ""),
    ]

    for candidato in candidatos:
        token = extrair_token_de_candidato(str(candidato or ""))
        if token:
            return token

    token_interativo = solicitar_token_interativo()
    if token_interativo:
        return token_interativo

    exibir_erro_amigavel("Token obrigatório para iniciar a importação.")
    return None


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


def encontrar_alvos_download(page) -> list[tuple[str, object]]:
    alvos: list[tuple[str, object]] = []
    assinaturas: set[str] = set()

    for seletor in DOWNLOAD_SELECTORS:
        locator = page.locator(seletor)
        try:
            total = locator.count()
        except Exception:
            continue

        for indice in range(total):
            item = locator.nth(indice)
            try:
                if not item.is_visible():
                    continue
            except Exception:
                continue

            assinatura = texto_elemento(item)
            if not assinatura:
                continue

            texto_normalizado = assinatura.lower()
            if ".pdf" not in texto_normalizado and not any(
                palavra in texto_normalizado for palavra in DOWNLOAD_KEYWORDS
            ):
                continue

            if assinatura in assinaturas:
                continue

            assinaturas.add(assinatura)
            alvos.append((assinatura, item))

    return alvos


def criar_sessao_requests(context, page) -> requests.Session:
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
    except PlaywrightTimeoutError:
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


def baixar_contracheques(page, context, pasta_saida: Path) -> list[Path]:
    alvos = encontrar_alvos_download(page)
    if not alvos:
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


def pedir_login_manual(page) -> None:
    log("[aguardando login] navegador aberto")
    log("[aguardando login] faça login manual e vá até a página de contracheques")

    while True:
        try:
            input("Quando estiver na página de contracheques, pressione ENTER para procurar downloads...")
        except EOFError:
            break

        page.wait_for_timeout(1000)
        if encontrar_alvos_download(page):
            return

        log("[aguardando login] nenhum botão de download ainda. Navegue até a lista e tente de novo.")


def abrir_navegador(playwright, headless: bool):
    tentativas = [
        ("Chromium", lambda: playwright.chromium.launch(headless=headless)),
        ("Edge", lambda: playwright.chromium.launch(headless=headless, channel="msedge")),
        ("Chrome", lambda: playwright.chromium.launch(headless=headless, channel="chrome")),
    ]

    ultimo_erro: Exception | None = None
    for nome, abrir in tentativas:
        try:
            log(f"[info] abrindo navegador: {nome}")
            return abrir()
        except Exception as erro:
            ultimo_erro = erro
            log(f"[info] falha ao abrir {nome}")

    raise RuntimeError(
        "Nao foi possivel abrir um navegador. Instale o Chromium do Playwright ou tenha Edge/Chrome instalados.",
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
    configurar_logger()
    args = parse_args()
    token = resolver_token(args)
    if not token:
        return 1

    pasta_saida = Path(args.download_dir).expanduser().resolve() if args.download_dir else criar_diretorio_temporario()
    pasta_saida.mkdir(parents=True, exist_ok=True)

    browser = None
    try:
        with sync_playwright() as playwright:
            browser = abrir_navegador(playwright, args.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.set_default_timeout(BROWSER_TIMEOUT_MS)
            page.goto(args.portal_url, wait_until="domcontentloaded")

            pedir_login_manual(page)

            arquivos = baixar_contracheques(page, context, pasta_saida)
            if not arquivos:
                exibir_erro_amigavel("Nenhum PDF foi encontrado para baixar.")
                log("[falha] nenhum PDF encontrado para baixar")
                return 1

            log(f"[enviando] {len(arquivos)} arquivo(s) para backend")
            resultado = upload_pdfs_para_backend(
                arquivos,
                token,
                backend_url=args.backend_url,
            )
            log(f"[concluído] batch_id={resultado.batch_id} status={resultado.status}")

        return 0
    except UploadError as erro:
        exibir_erro_amigavel("Não foi possível concluir a importação agora. Verifique o assistente e tente novamente.")
        log(f"[falha] upload para backend: {erro}")
        return 1
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


if __name__ == "__main__":
    raise SystemExit(main())
