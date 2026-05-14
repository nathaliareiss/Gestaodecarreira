# Helper de contracheques

App Python + Playwright para abrir o navegador, aguardar login manual no gov.br, baixar PDFs de contracheques e enviar os arquivos para o backend.

## Rodar local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.development.example .env.development
python main.py
```

If you want to pass the token directly for internal tests:

```powershell
python main.py --token "SEU_TOKEN_TEMPORARIO"
```

You can also call the custom protocol used by the site:

```powershell
python main.py "gestaodecarreira://import?token=SEU_TOKEN_TEMPORARIO"
```

When you open the executable by double-clicking, the helper will ask for the temporary token in a simple interactive prompt.

## Gerar o exe

Use o script de build:

```powershell
.\build.bat
```

Ou rode o PyInstaller direto:

```powershell
pyinstaller --onefile --name GestaoDeCarreira-Assistente main.py
```

O arquivo final fica em:

```text
dist\GestaoDeCarreira-Assistente.exe
```

Para publicar no frontend, copie o exe para:

```text
backend\static\downloads\gestao-de-carreira-assistente.exe
```

## Dependencias

- `playwright`
- `requests`
- `python-dotenv`
- `pyinstaller`

## Playwright

Antes do build, instale os browsers:

```powershell
python -m playwright install chromium
```

O helper tenta abrir nesta ordem:

1. Chromium do Playwright;
2. Microsoft Edge;
3. Google Chrome.

## Arquivos principais

- `main.py`: fluxo principal
- `config.py`: ambiente e URLs
- `upload_service.py`: envio dos PDFs
- `helper.spec`: build one-file do PyInstaller
- `build.bat`: build automatizado

## Publicacao

O executavel gerado deve ser distribuido junto com:

- `.env.production` ao lado do `.exe`
- o backend disponivel para receber os uploads

Se quiser publicar o assistente como download do sistema, copie o arquivo para:

```text
backend/static/downloads/gestao-de-carreira-assistente.exe
```

Esse caminho e exposto em:

```text
/downloads/gestao-de-carreira-assistente.exe
```
