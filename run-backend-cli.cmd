@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%backend"
"%ROOT%venv\Scripts\python.exe" controllers\carreira_controller.py
popd
