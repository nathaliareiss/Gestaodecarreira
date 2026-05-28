from __future__ import annotations

import os
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from config import DOWNLOAD_TIMEOUT_MS

try:
    from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
except Exception:  # pragma: no cover - runtime dependency expected in app
    Page = object  # type: ignore[assignment]
    PlaywrightTimeoutError = Exception  # type: ignore[assignment]


@dataclass(frozen=True)
class DocumentoInfo:
    texto_linha: str
    ano: Optional[int]
    mes: Optional[int]
    is_decimo_terceiro: bool


def normalizar_texto(valor: str) -> str:
    texto = unicodedata.normalize("NFKD", valor or "")
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"\s+", " ", texto).strip().lower()
    return texto


def _log(mensagem: str) -> None:
    if debug_ativo():
        print(mensagem, flush=True)


def _debug(mensagem: str) -> None:
    if debug_ativo():
        print(mensagem, flush=True)


def debug_ativo() -> bool:
    valor = os.getenv("HELPER_DEBUG", "").strip().lower()
    return valor in {"1", "true", "sim", "yes", "on"}


def primeiros_dia_mes_ha_n_meses(n: int) -> date:
    hoje = date.today()
    total_meses = hoje.year * 12 + (hoje.month - 1)
    alvo = total_meses - n
    ano_alvo = alvo // 12
    mes_alvo = (alvo % 12) + 1
    return date(ano_alvo, mes_alvo, 1)


def dentro_dos_ultimos_60_meses(ano: Optional[int], mes: Optional[int]) -> bool:
    if ano is None or mes is None:
        return False

    doc = date(ano, mes, 1)
    limite = primeiros_dia_mes_ha_n_meses(59)
    hoje = date.today().replace(day=1)
    return limite <= doc <= hoje


def normalizar_nome_arquivo(texto: str) -> str:
    texto = re.sub(r"[^\w\s.-]", "", texto, flags=re.UNICODE)
    texto = re.sub(r"\s+", "_", texto.strip())
    return texto[:120] if texto else f"arquivo_{int(time.time())}"


def extrair_info_documento(texto: str) -> DocumentoInfo:
    texto_norm = " ".join((texto or "").split())
    texto_lower = texto_norm.lower()

    is_decimo = (
        "13" in texto_lower
        or "décimo" in texto_lower
        or "decimo" in texto_lower
        or "13º" in texto_lower
        or "13o" in texto_lower
    )

    ano = None
    mes = None

    match_mes_ano = re.search(r"\b(0?[1-9]|1[0-2])/(20\d{2})\b", texto_lower)
    if match_mes_ano:
        mes = int(match_mes_ano.group(1))
        ano = int(match_mes_ano.group(2))

    return DocumentoInfo(
        texto_linha=texto_norm,
        ano=ano,
        mes=mes,
        is_decimo_terceiro=is_decimo,
    )


def encontrar_qualquer_pagina_viva(page: Page) -> Page:
    try:
        _ = page.url
        return page
    except Exception:
        pass

    try:
        ctx = page.context
        for p in ctx.pages:
            try:
                _ = p.url
                return p
            except Exception:
                continue
    except Exception:
        pass

    return page


def iterar_contextos_page(page: Page):
    vistos: set[int] = set()
    contextos: list[tuple[str, object]] = []

    def adicionar(rotulo: str, contexto) -> None:
        chave = id(contexto)
        if chave in vistos:
            return
        vistos.add(chave)
        contextos.append((rotulo, contexto))

    try:
        adicionar("page", page)
    except Exception:
        pass

    try:
        for indice, p in enumerate(getattr(page.context, "pages", []) or []):
            adicionar(f"context.page[{indice}]", p)
            try:
                for frame_indice, frame in enumerate(getattr(p, "frames", []) or []):
                    adicionar(f"context.page[{indice}].frame[{frame_indice}]", frame)
            except Exception:
                continue
    except Exception:
        pass

    try:
        for indice, frame in enumerate(getattr(page, "frames", []) or []):
            adicionar(f"page.frame[{indice}]", frame)
    except Exception:
        pass

    return contextos


def fechar_avisos_se_existirem(page: Page) -> None:
    try:
        candidatos = [
            page.get_by_role("button", name=re.compile(r"^fechar$", re.I)),
            page.get_by_role("button", name=re.compile(r"^(ok|entendi|continuar|prosseguir)$", re.I)),
            page.get_by_role("button", name=re.compile(r"^(x|×)$", re.I)),
        ]

        for c in candidatos:
            try:
                if c.count() > 0 and c.first.is_visible():
                    c.first.click(timeout=2000)
                    page.wait_for_timeout(300)
                    return
            except Exception:
                continue

        zk_close = page.locator(".z-window .z-window-close, .z-window-modal .z-window-close")
        if zk_close.count() > 0 and zk_close.first.is_visible():
            zk_close.first.click(timeout=2000)
            page.wait_for_timeout(300)
    except Exception:
        pass


def encontrar_contexto_lista(page: Page):
    seletores_linhas = [
        "tr.z-listitem",
        ".z-listbox-body tr",
        "table tbody tr",
    ]

    for sel in seletores_linhas:
        try:
            if page.locator(sel).count() > 0:
                return page
        except Exception:
            pass

    for _, contexto in iterar_contextos_page(page):
        if contexto is page:
            continue
        for sel in seletores_linhas:
            try:
                if contexto.locator(sel).count() > 0:
                    return contexto
            except Exception:
                continue

    return page


def localizar_linhas_documento(contexto):
    candidatos = [
        "tr.z-listitem",
        ".z-listbox-body tr",
        "table tbody tr",
    ]

    for sel in candidatos:
        try:
            loc = contexto.locator(sel)
            if loc.count() > 0:
                return loc
        except Exception:
            continue

    return contexto.locator("tr.z-listitem")


def esperar_lista_em_alguma_frame(page: Page, timeout_ms: int):
    deadline = time.time() + (timeout_ms / 1000)

    while time.time() < deadline:
        page = encontrar_qualquer_pagina_viva(page)

        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        try:
            page.wait_for_timeout(1000)
        except Exception:
            pass

        try:
            fechar_avisos_se_existirem(page)
        except Exception:
            pass

        contexto = encontrar_contexto_lista(page)

        try:
            linhas = localizar_linhas_documento(contexto)
            if linhas.count() > 0:
                return contexto
        except Exception:
            pass

        try:
            page.wait_for_timeout(300)
        except Exception:
            pass

    raise PlaywrightTimeoutError("Timeout aguardando a lista de contracheques.")


def encontrar_pagina_com_lista_flexivel(page: Page) -> Page:
    seletores_linhas = [
        "tr.z-listitem",
        ".z-listbox-body tr",
        "table tbody tr",
    ]

    for _, p in iterar_contextos_page(page):
        try:
            for sel in seletores_linhas:
                if p.locator(sel).count() > 0:
                    return page
        except Exception:
            continue
    return page


def _texto_linha(linha) -> str:
    try:
        return linha.inner_text(timeout=3000).strip()
    except Exception:
        try:
            return linha.text_content() or ""
        except Exception:
            return ""


def criar_sessao_requests(context, page) -> "requests.Session":
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


def diagnostico_abrangente(page) -> dict[str, int]:
    total_contextos = 0
    total_frames = 0
    total_linhas = 0
    total_botoes = 0

    for _, contexto in iterar_contextos_page(page):
        total_contextos += 1
        try:
            total_frames += len(getattr(contexto, "frames", []) or [])
        except Exception:
            pass
        try:
            total_botoes += contexto.locator("button").count()
        except Exception:
            pass
        try:
            total_linhas += localizar_linhas_documento(contexto).count()
        except Exception:
            pass

    return {
        "contextos": total_contextos,
        "frames": total_frames,
        "linhas": total_linhas,
        "botoes": total_botoes,
    }


def _candidatos_botoes_baixar_na_linha(linha):
    return [
        ("css.text-uppercase.btn-outline-primary2", linha.locator("button.text-uppercase.btn-outline-primary2", has_text=re.compile(r"baixar", re.I))),
        ("css.btn-outline-primary2", linha.locator("button.btn-outline-primary2", has_text=re.compile(r"baixar", re.I))),
        ("texto.Baixar", linha.locator("button:has-text('Baixar')")),
        ("regex.baixar", linha.locator("button", has_text=re.compile(r"baixar", re.I))),
    ]


def _candidatos_botoes_exibir_na_linha(linha):
    return [
        ("css.btn-primary2", linha.locator("button.btn-primary2", has_text=re.compile(r"exibir", re.I))),
        ("texto.Exibir", linha.locator("button:has-text('Exibir')")),
        ("regex.exibir", linha.locator("button", has_text=re.compile(r"exibir", re.I))),
    ]


def _selecionar_primeiro_botao_visivel(candidatos):
    total = 0
    primeiro_encontrado = None
    for rotulo, locator in candidatos:
        try:
            quantidade = locator.count()
        except Exception:
            continue

        total += quantidade
        for indice in range(quantidade):
            try:
                botao = locator.nth(indice)
                if primeiro_encontrado is None:
                    primeiro_encontrado = (botao, rotulo)
                if botao.is_visible():
                    return botao, rotulo, total
            except Exception:
                continue

    if primeiro_encontrado is not None:
        botao, rotulo = primeiro_encontrado
        return botao, rotulo, total

    return None, None, total


def _restaurar_contexto_lista(page: Page, url_antes: str) -> None:
    try:
        if page.url == url_antes:
            return

        try:
            page.go_back(timeout=5000)
        except Exception:
            page.goto(url_antes, wait_until="domcontentloaded", timeout=10000)

        try:
            page.wait_for_timeout(1000)
        except Exception:
            pass
    except Exception:
        pass


def baixar_url_com_sessao(sessao, url: str, destino: Path) -> None:
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


def clicar_baixar_na_linha(
    page: Page,
    linha,
    pasta_destino: Path,
    competencia: str,
    tipo: str,
    context=None,
) -> bool:
    try:
        nome_base = f"{competencia}_{tipo}".replace("/", "-").replace(" ", "_")
        nome_base = normalizar_nome_arquivo(nome_base)

        btn = linha.locator("button.btn-outline-primary2, button:has-text('Baixar'), button.text-uppercase")
        if btn.count() == 0:
            btn = linha.get_by_role("button", name=re.compile(r"baixar", re.I))
        if btn.count() == 0:
            btn = linha.locator("button").filter(has_text=re.compile(r"baixar", re.I))

        if btn.count() == 0:
            _log(f"Botão Baixar não encontrado para {competencia} - {tipo}")
            return False

        botao = btn.first
        try:
            botao.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass

        _log(f"Tentando baixar: {competencia} - {tipo}")

        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            botao.click(timeout=5000, force=True)

        download = download_info.value
        suggested = download.suggested_filename or f"{nome_base}.pdf"
        ext = Path(suggested).suffix or ".pdf"
        destino = pasta_destino / f"{nome_base}{ext}"
        download.save_as(str(destino))

        _log(f"Baixado: {destino.name}")
        return True

    except PlaywrightTimeoutError:
        try:
            href = linha.locator("a[href]").first.get_attribute("href")
        except Exception:
            href = None

        if not href and page.url.lower().split("?", 1)[0].endswith(".pdf"):
            href = page.url

        if href and context is not None:
            try:
                nome_base = f"{competencia}_{tipo}".replace("/", "-").replace(" ", "_")
                nome_base = normalizar_nome_arquivo(nome_base)
                destino = pasta_destino / f"{nome_base}.pdf"
                sessao = criar_sessao_requests(context, page)
                url = urljoin(page.url, href)
                baixar_url_com_sessao(sessao, url, destino)
                _log(f"Baixado via sessão: {destino.name}")
                return True
            except Exception as exc:
                _log(f"Erro ao baixar via sessão {competencia} - {tipo}: {exc}")
                return False

        _log(f"Timeout no download: {competencia} - {tipo}")
        return False
    except Exception as exc:
        _log(f"Erro ao baixar {competencia} - {tipo}: {exc}")
        return False


def processar_pagina(page: Page, pasta_mensais: Path, pasta_decimo: Path, vistos: set[str], context=None) -> int:
    try:
        page.wait_for_timeout(1500)
    except Exception:
        pass

    contexto = esperar_lista_em_alguma_frame(page, timeout_ms=20_000)
    linhas = localizar_linhas_documento(contexto)
    total_baixados = 0

    _log(f"Linhas encontradas nesta página: {linhas.count()}")

    for i in range(linhas.count()):
        linha = linhas.nth(i)

        try:
            colunas = linha.locator("td")
            if colunas.count() < 3:
                continue

            competencia = colunas.nth(0).inner_text(timeout=3000).strip()
            tipo = colunas.nth(1).inner_text(timeout=3000).strip()
        except Exception:
            continue

        if not competencia or not tipo:
            continue

        chave = f"{competencia}|{tipo}".lower()
        if chave in vistos:
            continue

        info = extrair_info_documento(f"{competencia} {tipo}")

        deve_baixar = True
        pasta_destino = pasta_mensais
        tipo_lower = tipo.lower()

        if info.is_decimo_terceiro or "13" in tipo_lower or "décimo" in tipo_lower or "decimo" in tipo_lower:
            pasta_destino = pasta_decimo
        elif "mensal" in tipo_lower:
            pasta_destino = pasta_mensais

        ok = clicar_baixar_na_linha(
            page=page,
            linha=linha,
            pasta_destino=pasta_destino,
            competencia=competencia,
            tipo=tipo,
            context=context,
        )

        if ok:
            vistos.add(chave)
            total_baixados += 1

    return total_baixados


def ir_para_proxima_pagina(page: Page) -> bool:
    try:
        contexto = encontrar_contexto_lista(page)

        proximo = contexto.locator('a.z-paging-next[name$="-next"]')
        if proximo.count() == 0:
            _log("Botão de próxima página não encontrado.")
            return False

        botao = proximo.first

        if not botao.is_visible():
            _log("Botão de próxima página não está visível.")
            return False

        linhas_antes = localizar_linhas_documento(contexto)
        primeira_linha_antes = ""

        if linhas_antes.count() > 0:
            try:
                primeira_linha_antes = linhas_antes.nth(0).inner_text(timeout=3000).strip()
            except Exception:
                primeira_linha_antes = ""

        botao.scroll_into_view_if_needed()
        botao.click(timeout=5000)

        try:
            page.wait_for_timeout(2000)
        except Exception:
            pass

        for _ in range(12):
            try:
                page.wait_for_timeout(500)
            except Exception:
                pass

            contexto_depois = encontrar_contexto_lista(page)
            linhas_depois = localizar_linhas_documento(contexto_depois)

            if linhas_depois.count() == 0:
                continue

            try:
                primeira_linha_depois = linhas_depois.nth(0).inner_text(timeout=3000).strip()
            except Exception:
                continue

            if primeira_linha_depois != primeira_linha_antes:
                _log("Avançou para a próxima página.")
                return True

        _log("Não detectei mudança de página; assumindo fim da paginação.")
        return False

    except Exception as exc:
        _log(f"Não foi possível ir para a próxima página: {exc}")
        return False
