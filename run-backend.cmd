@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%backend"
py main.py
popd
