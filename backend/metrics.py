from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from backend.config import REDIS_URL
from backend.logger import logger

try:
    from redis import Redis
except ImportError:  # pragma: no cover - optional when redis is not installed
    Redis = None

DEFAULT_HISTOGRAM_BUCKETS: tuple[float, ...] = (
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
)

_METRIC_HELP = {
    "http_requests_total": "Total de requests HTTP recebidas.",
    "http_request_duration_seconds": "Duracao das requests HTTP em segundos.",
    "http_requests_in_flight": "Quantidade de requests HTTP em andamento.",
    "job_executions_total": "Total de execucoes de jobs em fila.",
    "job_execution_duration_seconds": "Duracao das execucoes de jobs em segundos.",
    "email_send_total": "Total de tentativas de envio de email.",
    "email_send_duration_seconds": "Duracao do envio de email em segundos.",
}

_COUNTER_METRICS = (
    "http_requests_total",
    "job_executions_total",
    "email_send_total",
)

_GAUGE_METRICS = ("http_requests_in_flight",)

_HISTOGRAM_METRICS = (
    "http_request_duration_seconds",
    "job_execution_duration_seconds",
    "email_send_duration_seconds",
)


@dataclass
class _HistogramState:
    count: int = 0
    total: float = 0.0
    buckets: dict[float, int] = field(default_factory=lambda: defaultdict(int))


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._histograms: dict[tuple[str, tuple[tuple[str, str], ...]], _HistogramState] = {}
        self._redis = self._conectar_redis()

    def increment_counter(
        self,
        name: str,
        amount: float = 1.0,
        labels: dict[str, Any] | None = None,
    ) -> None:
        key = self._build_key(name, labels)
        if self._redis is not None:
            self._redis.hincrbyfloat(self._redis_key("counter", name), self._serializar_labels(key[1]), amount)
            return

        with self._lock:
            self._counters[key] += amount

    def increment_gauge(
        self,
        name: str,
        amount: float = 1.0,
        labels: dict[str, Any] | None = None,
    ) -> None:
        key = self._build_key(name, labels)
        if self._redis is not None:
            self._redis.hincrbyfloat(self._redis_key("gauge", name), self._serializar_labels(key[1]), amount)
            return

        with self._lock:
            self._gauges[key] += amount

    def decrement_gauge(
        self,
        name: str,
        amount: float = 1.0,
        labels: dict[str, Any] | None = None,
    ) -> None:
        self.increment_gauge(name, -amount, labels)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, Any] | None = None,
    ) -> None:
        key = self._build_key(name, labels)
        if self._redis is not None:
            self._redis.hset(self._redis_key("gauge", name), self._serializar_labels(key[1]), value)
            return

        with self._lock:
            self._gauges[key] = value

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, Any] | None = None,
        buckets: tuple[float, ...] = DEFAULT_HISTOGRAM_BUCKETS,
    ) -> None:
        key = self._build_key(name, labels)
        if self._redis is not None:
            redis_key = self._redis_key("histogram", name)
            serie = self._serializar_labels(key[1])
            pipeline = self._redis.pipeline(transaction=True)
            pipeline.hincrby(redis_key, f"{serie}|count", 1)
            pipeline.hincrbyfloat(redis_key, f"{serie}|sum", value)
            for bucket in buckets:
                if value <= bucket:
                    pipeline.hincrby(redis_key, f"{serie}|bucket:{bucket}", 1)
            pipeline.execute()
            return

        with self._lock:
            state = self._histograms.setdefault(key, _HistogramState())
            state.count += 1
            state.total += value
            for bucket in buckets:
                if value <= bucket:
                    state.buckets[bucket] += 1

    def render(self) -> str:
        if self._redis is not None:
            return self._render_from_redis()
        return self._render_from_memory()

    def _render_from_memory(self) -> str:
        with self._lock:
            counters = dict(self._counters)
            gauges = dict(self._gauges)
            histograms = {
                key: _HistogramState(
                    count=state.count,
                    total=state.total,
                    buckets=dict(state.buckets),
                )
                for key, state in self._histograms.items()
            }

        linhas: list[str] = []
        metric_types: dict[str, str] = {}

        for name, _ in counters:
            metric_types[name] = "counter"
        for name, _ in gauges:
            metric_types[name] = "gauge"
        for name, _ in histograms:
            metric_types[name] = "histogram"

        for name in sorted(metric_types):
            self._append_help_and_type(linhas, name, metric_types[name])

            if metric_types[name] == "counter":
                for (metric_name, labels), value in sorted(counters.items()):
                    if metric_name == name:
                        linhas.append(f"{name}{self._format_labels(labels)} {self._format_value(value)}")

            elif metric_types[name] == "gauge":
                for (metric_name, labels), value in sorted(gauges.items()):
                    if metric_name == name:
                        linhas.append(f"{name}{self._format_labels(labels)} {self._format_value(value)}")

            else:
                for (metric_name, labels), state in sorted(histograms.items()):
                    if metric_name != name:
                        continue
                    base_labels = self._labels_dict(labels)
                    for bucket in DEFAULT_HISTOGRAM_BUCKETS:
                        bucket_labels = dict(base_labels)
                        bucket_labels["le"] = self._format_bucket(bucket)
                        linhas.append(
                            f"{name}_bucket{self._format_labels(bucket_labels)} "
                            f"{state.buckets.get(bucket, 0)}"
                        )
                    bucket_labels = dict(base_labels)
                    bucket_labels["le"] = "+Inf"
                    linhas.append(f"{name}_bucket{self._format_labels(bucket_labels)} {state.count}")
                    linhas.append(f"{name}_sum{self._format_labels(base_labels)} {self._format_value(state.total)}")
                    linhas.append(f"{name}_count{self._format_labels(base_labels)} {state.count}")

        return "\n".join(linhas) + ("\n" if linhas else "")

    def _render_from_redis(self) -> str:
        linhas: list[str] = []

        for name in _COUNTER_METRICS:
            valores = self._redis.hgetall(self._redis_key("counter", name))
            if not valores:
                continue
            self._append_help_and_type(linhas, name, "counter")
            for serie, valor in sorted(valores.items()):
                labels = self._desserializar_labels(serie)
                linhas.append(f"{name}{self._format_labels(labels)} {self._format_value(float(valor))}")

        for name in _GAUGE_METRICS:
            valores = self._redis.hgetall(self._redis_key("gauge", name))
            if not valores:
                continue
            self._append_help_and_type(linhas, name, "gauge")
            for serie, valor in sorted(valores.items()):
                labels = self._desserializar_labels(serie)
                linhas.append(f"{name}{self._format_labels(labels)} {self._format_value(float(valor))}")

        for name in _HISTOGRAM_METRICS:
            valores = self._redis.hgetall(self._redis_key("histogram", name))
            if not valores:
                continue
            self._append_help_and_type(linhas, name, "histogram")

            series: dict[str, dict[str, Any]] = defaultdict(
                lambda: {"count": 0, "sum": 0.0, "buckets": defaultdict(int)}
            )
            for campo, valor in valores.items():
                serie, secao = campo.rsplit("|", 1)
                dados = series[serie]
                if secao == "count":
                    dados["count"] = int(float(valor))
                elif secao == "sum":
                    dados["sum"] = float(valor)
                elif secao.startswith("bucket:"):
                    bucket = secao.split(":", 1)[1]
                    dados["buckets"][bucket] = int(float(valor))

            for serie, dados in sorted(series.items()):
                labels = self._desserializar_labels(serie)
                for bucket in DEFAULT_HISTOGRAM_BUCKETS:
                    bucket_key = self._format_bucket(bucket)
                    bucket_labels = dict(labels)
                    bucket_labels["le"] = bucket_key
                    linhas.append(
                        f"{name}_bucket{self._format_labels(bucket_labels)} "
                        f"{dados['buckets'].get(str(bucket), 0)}"
                    )
                bucket_labels = dict(labels)
                bucket_labels["le"] = "+Inf"
                linhas.append(f"{name}_bucket{self._format_labels(bucket_labels)} {dados['count']}")
                linhas.append(f"{name}_sum{self._format_labels(labels)} {self._format_value(dados['sum'])}")
                linhas.append(f"{name}_count{self._format_labels(labels)} {dados['count']}")

        return "\n".join(linhas) + ("\n" if linhas else "")

    def _build_key(
        self,
        name: str,
        labels: dict[str, Any] | None,
    ) -> tuple[str, tuple[tuple[str, str], ...]]:
        normalized = tuple(sorted((str(chave), str(valor)) for chave, valor in (labels or {}).items()))
        return name, normalized

    def _conectar_redis(self) -> Redis | None:
        if Redis is None or not REDIS_URL:
            return None

        try:
            cliente = Redis.from_url(REDIS_URL, decode_responses=True)
            cliente.ping()
            return cliente
        except Exception as erro:  # pragma: no cover - depends on runtime environment
            logger.warning(
                "Metrica Redis indisponivel, usando armazenamento local",
                extra={"erro": str(erro)},
            )
            return None

    def _redis_key(self, kind: str, name: str) -> str:
        return f"metrics:{kind}:{name}"

    def _serializar_labels(self, labels: tuple[tuple[str, str], ...]) -> str:
        return json.dumps(dict(labels), sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    def _desserializar_labels(self, valor: str) -> dict[str, str]:
        return json.loads(valor) if valor else {}

    def _append_help_and_type(self, linhas: list[str], name: str, metric_type: str) -> None:
        help_text = _METRIC_HELP.get(name)
        if help_text:
            linhas.append(f"# HELP {name} {help_text}")
        linhas.append(f"# TYPE {name} {metric_type}")

    def _labels_dict(self, labels: tuple[tuple[str, str], ...]) -> dict[str, str]:
        return {chave: valor for chave, valor in labels}

    def _format_labels(self, labels: dict[str, Any] | tuple[tuple[str, str], ...]) -> str:
        if not labels:
            return ""

        if isinstance(labels, tuple):
            items = labels
        else:
            items = tuple(sorted((str(chave), str(valor)) for chave, valor in labels.items()))

        partes = []
        for chave, valor in items:
            valor_formatado = str(valor).replace("\\", "\\\\").replace('"', '\\"')
            partes.append(f'{chave}="{valor_formatado}"')
        return "{" + ",".join(partes) + "}"

    def _format_value(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.6f}".rstrip("0").rstrip(".")

    def _format_bucket(self, bucket: float) -> str:
        if bucket.is_integer():
            return str(int(bucket))
        return f"{bucket:.6f}".rstrip("0").rstrip(".")


metrics = MetricsRegistry()


def registro_http_request(
    metodo: str,
    rota: str,
    status_code: int,
    duracao_segundos: float,
) -> None:
    labels = {"method": metodo, "route": rota, "status": str(status_code)}
    metrics.increment_counter("http_requests_total", labels=labels)
    metrics.observe_histogram(
        "http_request_duration_seconds",
        duracao_segundos,
        labels={"method": metodo, "route": rota},
    )


def registrar_request_em_andamento() -> None:
    metrics.increment_gauge("http_requests_in_flight")


def liberar_request_em_andamento() -> None:
    metrics.decrement_gauge("http_requests_in_flight")


def registrar_job_execucao(
    job: str,
    status: str,
    duracao_segundos: float,
) -> None:
    labels = {"job": job, "status": status}
    metrics.increment_counter("job_executions_total", labels=labels)
    metrics.observe_histogram("job_execution_duration_seconds", duracao_segundos, labels={"job": job})


def registrar_envio_email(
    tipo: str,
    status: str,
    duracao_segundos: float,
) -> None:
    labels = {"type": tipo, "status": status}
    metrics.increment_counter("email_send_total", labels=labels)
    metrics.observe_histogram("email_send_duration_seconds", duracao_segundos, labels={"type": tipo})


def render_metrics() -> str:
    return metrics.render()
