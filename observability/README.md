# Observability local

Este diretório deixa o projeto pronto para coleta de métricas com Prometheus e visualização no Grafana.

## O que entra aqui

- `prometheus/prometheus.yml`: instrução de coleta do endpoint `/api/metrics`
- `grafana/provisioning/datasources/datasource.yml`: datasource do Grafana apontando para o Prometheus
- `docker-compose.observability.yml`: sobe Prometheus e Grafana em containers

## Como usar

1. Suba o backend normalmente.
2. Garanta que ele esteja acessível em `http://localhost:8000`.
3. Execute:

```powershell
.\run-observability.cmd
```

4. Abra:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

## Credenciais do Grafana

- usuário: `admin`
- senha: `admin`

## Fonte das métricas

O Prometheus coleta:

- `http://host.docker.internal:8000/api/metrics`

Se você mover isso para outro ambiente, ajuste o alvo em `observability/prometheus/prometheus.yml`.

## Consultas úteis no Grafana

- taxa de requests: `sum(rate(http_requests_total[5m])) by (route, status)`
- latência média: `sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))`
- jobs concluídos: `sum(rate(job_executions_total[5m])) by (job, status)`
- e-mails enviados: `sum(rate(email_send_total[5m])) by (type, status)`
