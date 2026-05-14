# Downloads

Place the Windows installer here as:

`GestaoDeCarreira-Setup.exe`

The backend mounts this folder at `/downloads`, so the frontend can fetch:

`/downloads/GestaoDeCarreira-Setup.exe`

The installer bundles the assistant executable, installs it under the current user profile, and registers the `gestaodecarreira://` protocol.

If you prefer object storage or a CDN, keep the same public path and update the backend proxy to point to that storage location.
