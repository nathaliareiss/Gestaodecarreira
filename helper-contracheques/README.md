# Helper local de contracheques

App Python + Playwright para abrir navegador, esperar login manual no gov.br, baixar PDFs de contracheques e enviar para o backend com token temporário.

## Configuração por ambiente

O helper lê ambiente automaticamente:

- `HELPER_ENV=development` usa desenvolvimento;
- `HELPER_ENV=production` usa produção;
- se `HELPER_ENV` não vier, o helper tenta inferir pelo `BACKEND_URL`.

### Variáveis

- `BACKEND_URL`: URL do backend usada pelo helper;
- `DEV_BACKEND_URL`: URL usada em desenvolvimento;
- `PRODUCTION_BACKEND_URL`: alternativa para produção;
- `PORTAL_URL`: página inicial do portal;
- `UPLOAD_ENDPOINT`: rota de upload, padrão `/api/financeiro/importacao-temporaria/upload-lote`;
- `DOWNLOAD_SELECTORS`: seletores CSS separados por vírgula;
- `DOWNLOAD_ROOT`: pasta base dos downloads temporários.

### Regras

- `localhost` só vale em desenvolvimento;
- em produção, o helper exige `BACKEND_URL` ou `PRODUCTION_BACKEND_URL`;
- o helper também aceita `--backend-url` para sobrescrever a URL na linha de comando.

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
- `config.py`: resolve ambiente e URLs;
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
copy .env.development.example .env.development
python main.py --token "SEU_TOKEN_TEMPORARIO"
```

## Produção

No release Windows, coloque um `.env.production` ao lado do `.exe` com:

```env
HELPER_ENV=production
BACKEND_URL=https://SEU-BACKEND-REAL-AQUI
PORTAL_URL=https://www.gov.br/
```

## Gerar `.exe`

### Script pronto

```powershell
.\build_helper.ps1
```

Isso gera build em pasta `dist\helper-contracheques`.

Para gerar `onefile`:

```powershell
.\build_helper.ps1 -OneFile
```

### Manual

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
