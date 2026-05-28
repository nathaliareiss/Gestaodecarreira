# Downloads

Place the public Windows installer here as:

`GestaoDeCarreira-Setup-1.0.6.exe`

The build also copies the same file to:

`GestaoDeCarreira-Setup-latest.exe`

For compatibility, the backend also redirects the legacy path
`/downloads/GestaoDeCarreira-Setup-1.0.4.exe` to the latest installer.

The backend mounts this folder at `/downloads`, so the frontend can fetch:

`/downloads/GestaoDeCarreira-Setup-latest.exe`

The installer bundles the assistant executable, installs it under the current user profile, and registers the `gestaodecarreira://` protocol.

Do not publish the raw assistant executable here. The site should expose only the setup file.

If you prefer object storage or a CDN, keep the same public path and update the backend proxy to point to that storage location.
