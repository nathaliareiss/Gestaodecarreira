from __future__ import annotations

from time import perf_counter

from fastapi import Request

from backend.metrics import (
    liberar_request_em_andamento,
    registrar_request_em_andamento,
    registro_http_request,
)


def registrar_middleware_de_metricas(app) -> None:
    @app.middleware("http")
    async def medir_requisicoes(request: Request, call_next):
        rota = getattr(getattr(request.scope.get("route"), "path", None), "strip", None)
        route = request.scope.get("route")
        nome_rota = getattr(route, "path", None) or request.url.path
        metodo = request.method
        registrar_request_em_andamento(metodo, nome_rota)
        inicio = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duracao = perf_counter() - inicio
            registro_http_request(metodo, nome_rota, status_code, duracao)
            liberar_request_em_andamento(metodo, nome_rota)
