@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%backend"
py controllers\carreira_controller.py
popd
