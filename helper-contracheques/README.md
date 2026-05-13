# Helper local de contracheques

App Python + Playwright para abrir navegador, esperar login manual no gov.br, baixar PDFs de contracheques e enviar para o backend com token temporário.

## O que ele faz

- abre navegador automaticamente;
- espera login manual;
- detecta botões de download;
- baixa PDFs em pasta temporária;
- envia PDFs para `POST /api/financeiro/importacao-temporaria/upload-lote`;
- mostra logs simples:
  - `aguardando login`
  - `baixando`
  - `enviando`
  - `concluído`

## O que ele não faz

- não pede senha do gov.br dentro do app;
- não salva senha;
- não usa usuário fixo.

## Arquivos

- `main.py`: fluxo principal;
- `config.py`: URLs, timeout e seletores;
- `upload_service.py`: envio dos PDFs;
- `requirements.txt`: dependências;
- `helper-contracheques.spec`: build do PyInstaller;
- `build_helper.ps1`: script de build;
- `README.md`: instruções.

## Rodar local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python main.py --token "SEU_TOKEN_TEMPORARIO"
```

## Variáveis úteis

- `BACKEND_URL`: URL do backend, exemplo `http://localhost:8000`;
- `PORTAL_URL`: página inicial do portal;
- `UPLOAD_ENDPOINT`: rota de upload, padrão `/api/financeiro/importacao-temporaria/upload-lote`;
- `DOWNLOAD_SELECTORS`: seletores CSS separados por vírgula;
- `DOWNLOAD_ROOT`: pasta base dos downloads temporários.

## Gerar `.exe`

### Opção 1: script pronto

```powershell
.\build_helper.ps1
```

Isso gera build em pasta `dist\helper-contracheques`.

Para gerar `onefile`:

```powershell
.\build_helper.ps1 -OneFile
```

### Opção 2: manual

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
pyinstaller --clean --noconfirm helper-contracheques.spec
```

## Ícone

Se existir `assets\helper-contracheques.ico`, o build usa esse ícone.
Se não existir, o build continua sem ícone.

## Navegador

O helper tenta abrir nesta ordem:

1. Chromium do Playwright;
2. Microsoft Edge;
3. Google Chrome.

Isso ajuda o `.exe` a rodar sem exigir instalação extra de navegador na máquina do usuário.

## Observação

O helper já fica sem Python para o usuário final depois do build.
Se você quiser um `.exe` totalmente isolado de navegador do sistema, o próximo passo é empacotar também os binários do Playwright junto do release.
