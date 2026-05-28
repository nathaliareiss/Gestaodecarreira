from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import portal_automation as base

from config import DOWNLOAD_TIMEOUT_MS

Page = base.Page
PlaywrightTimeoutError = base.PlaywrightTimeoutError

_log = base._log
_restaurar_contexto_lista = base._restaurar_contexto_lista
normalizar_nome_arquivo = base.normalizar_nome_arquivo
criar_sessao_requests = base.criar_sessao_requests
baixar_url_com_sessao = base.baixar_url_com_sessao
encontrar_contexto_lista = base.encontrar_contexto_lista
localizar_linhas_documento = base.localizar_linhas_documento
esperar_lista_em_alguma_frame = base.esperar_lista_em_alguma_frame
extrair_info_documento = base.extrair_info_documento
diagnostico_abrangente = base.diagnostico_abrangente


def _baixar_com_botao_na_linha(
    page: Page,
    linha,
    botao,
    pasta_destino: Path,
    competencia: str,
    tipo: str,
    context=None,
) -> bool:
    try:
        nome_base = f"{competencia}_{tipo}".replace("/", "-").replace(" ", "_")
        nome_base = normalizar_nome_arquivo(nome_base)
        url_antes = page.url

        try:
            botao.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass

        _log(f"Baixando linha {competencia} | {tipo}")

        with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
            botao.click(timeout=5000, force=True)

        download = download_info.value
        suggested = download.suggested_filename or f"{nome_base}.pdf"
        ext = Path(suggested).suffix or ".pdf"
        destino = pasta_destino / f"{nome_base}{ext}"
        download.save_as(str(destino))
        _log(f"Download concluido: {destino.name}")
        _restaurar_contexto_lista(page, url_antes)
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
                _log(f"Download concluido: {destino.name}")
                _restaurar_contexto_lista(page, url_antes)
                return True
            except Exception as exc:
                _log(f"Falha ao baixar via sessao {competencia} - {tipo}: {exc}")

        _restaurar_contexto_lista(page, url_antes)
        _log(f"Timeout ao baixar linha {competencia} - {tipo}")
        return False
    except Exception as exc:
        _restaurar_contexto_lista(page, url_antes)
        _log(f"Erro ao baixar linha {competencia} - {tipo}: {exc}")
        return False


def clicar_baixar_na_linha(
    page: Page,
    linha,
    pasta_destino: Path,
    competencia: str,
    tipo: str,
    context=None,
) -> bool:
    candidatos = base._candidatos_botoes_baixar_na_linha(linha)
    botao, origem, total = base._selecionar_primeiro_botao_visivel(candidatos)
    _log(f"Botões Baixar nesta linha: {total}")

    if botao is None:
        _log(f"Botao Baixar nao encontrado para {competencia} - {tipo}")
        return False

    _log(f"Usando botao Baixar ({origem}) para {competencia} - {tipo}")
    return _baixar_com_botao_na_linha(
        page=page,
        linha=linha,
        botao=botao,
        pasta_destino=pasta_destino,
        competencia=competencia,
        tipo=tipo,
        context=context,
    )


def processar_pagina(page: Page, pasta_mensais: Path, pasta_decimo: Path, vistos: set[str], context=None) -> int:
    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except Exception:
        pass

    try:
        page.wait_for_timeout(1500)
    except Exception:
        pass

    contexto = esperar_lista_em_alguma_frame(page, timeout_ms=20_000)
    linhas = localizar_linhas_documento(contexto)
    total_baixados = 0
    total_linhas = linhas.count()

    _log(f"Linhas encontradas nesta pagina: {total_linhas}")

    for i in range(total_linhas):
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

        _log(f"Processando linha {i + 1}/{total_linhas}")
        _log(f"Competencia: {competencia} | Tipo: {tipo}")

        chave = f"{competencia}|{tipo}".lower()
        if chave in vistos:
            continue

        info = extrair_info_documento(f"{competencia} {tipo}")
        pasta_destino = pasta_mensais
        tipo_lower = tipo.lower()

        if info.is_decimo_terceiro or "13" in tipo_lower or "decimo" in tipo_lower:
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

        if not ok:
            _log(f"Botao Baixar nao encontrado; pulando linha {i + 1}")
            continue

        vistos.add(chave)
        total_baixados += 1

    return total_baixados


def ir_para_proxima_pagina(page: Page) -> bool:
    try:
        contexto = encontrar_contexto_lista(page)

        proximo = contexto.locator('a.z-paging-next[name$="-next"]')
        if proximo.count() == 0:
            _log("Botao de proxima pagina nao encontrado.")
            return False

        botao = proximo.first

        if not botao.is_visible():
            _log("Botao de proxima pagina nao esta visivel.")
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
                _log("Indo para a proxima pagina.")
                return True

        _log("Nao detectei mudanca de pagina; assumindo fim da paginacao.")
        return False

    except Exception as exc:
        _log(f"Nao foi possivel ir para a proxima pagina: {exc}")
        return False
