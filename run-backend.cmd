@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"
py -m backend
popd
