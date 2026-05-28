# Downloads

Place the public Windows installer here as:

`GestaoDeCarreira-Setup-1.0.9.exe`

The build also copies the same file to:

`GestaoDeCarreira-Setup-latest.exe`

For compatibility, the backend also redirects the legacy paths
`/downloads/GestaoDeCarreira-Setup-1.0.4.exe`,
`/downloads/GestaoDeCarreira-Setup-1.0.5.exe`,
`/downloads/GestaoDeCarreira-Setup-1.0.6.exe`, and
`/downloads/GestaoDeCarreira-Setup-1.0.7.exe` to the latest installer.

The backend mounts this folder at `/downloads`, so the frontend can fetch:

`/downloads/GestaoDeCarreira-Setup-latest.exe`

The installer bundles the assistant executable, installs it under the current user profile, and registers the `gestaodecarreira://` protocol.

Do not publish the raw assistant executable here. The site should expose only the setup file.

If you prefer object storage or a CDN, keep the same public path and update the backend proxy to point to that storage location.
