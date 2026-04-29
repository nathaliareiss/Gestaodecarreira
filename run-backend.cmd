@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"
"%ROOT%venv\Scripts\python.exe" -m backend.main
popd
