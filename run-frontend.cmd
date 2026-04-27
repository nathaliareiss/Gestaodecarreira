@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%frontend"
call npm run dev
popd
