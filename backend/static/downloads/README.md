# Downloads

Place only the current public Windows installer here as:

`GestaoDeCarreira-Setup-1.0.9.exe`

The build also copies the same file to:

`GestaoDeCarreira-Setup-latest.exe`

The backend mounts this folder at `/downloads`, so the frontend can fetch:

`/downloads/GestaoDeCarreira-Setup-latest.exe`

The installer bundles the assistant executable, installs it under the current user profile, and registers the `gestaodecarreira://` protocol.

Do not publish older installer versions or the raw assistant executable here. The site should expose only the current setup file and the `latest` alias.

If you prefer object storage or a CDN, keep the same public path and update the backend proxy to point to that storage location.
