# Gestao de Carreira

Projeto em Python para organizar dados funcionais de uma servidora publica e evoluir depois para FastAPI, banco de dados e relatorios.

## Estrutura inicial

- `gestao_carreira/domain/`: entidades do negocio
- `gestao_carreira/services/`: regras e calculos
- `gestao_carreira/presentation/`: interface de execucao
- `main.py`: ponto de entrada do projeto
- `src/`: arquivos de estudo e testes didaticos

## Como rodar

1. Ative o ambiente virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

2. Rode o projeto:

```powershell
python main.py
```

## O que o primeiro fluxo faz

- calcula a data em que a carreira completa 25 anos
- calcula a idade nessa data
- verifica se a idade minima de 50 anos ja foi atingida
- calcula uma data provavel de aposentadoria
- calcula grau e nivel aos 45 anos e na aposentadoria

## Regra mental para pensar como programadora

1. Entidade guarda dados.
2. Service calcula regras.
3. Presentation mostra resultado.

