# Helper de contracheques

App Python + Playwright para abrir o navegador, receber o token automaticamente via protocolo quando possivel, aguardar login manual no gov.br, baixar PDFs de contracheques e enviar os arquivos para o backend.

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
python main.py "gestaodecarreira://importar?token=SEU_TOKEN_TEMPORARIO"
```

When you open the executable by double-clicking, the helper first tries to receive the temporary token automatically. If that fails, it shows a clear message and then asks for the token manually.

## Gerar o exe

Use o script de build:

```powershell
.\build.bat
```

Ou rode o PyInstaller direto:

```powershell
pyinstaller --noconfirm helper.spec
```

O arquivo final fica em:

```text
dist\GestaoDeCarreira-Assistente\GestaoDeCarreira-Assistente.exe
```

## Gerar o instalador

Este projeto usa Inno Setup para empacotar o assistente em:

```text
backend\static\downloads\GestaoDeCarreira-Setup-1.0.4.exe
```

O instalador faz uma instalação por usuário em:

```text
%LOCALAPPDATA%\GestaoDeCarreira\Assistente
```

e registra o protocolo:

```text
gestaodecarreira://
```

Para publicar o instalador no frontend, copie o arquivo para:

```text
backend\static\downloads\GestaoDeCarreira-Setup-1.0.4.exe
```

## Dependencias

- `playwright`
- `requests`
- `python-dotenv`
- `pyinstaller`
- `Inno Setup` para gerar o instalador

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

Se quiser publicar o instalador como download do sistema, copie o arquivo para:

```text
backend/static/downloads/GestaoDeCarreira-Setup-1.0.4.exe
```

Esse caminho e exposto em:

```text
/downloads/GestaoDeCarreira-Setup-1.0.4.exe
```
