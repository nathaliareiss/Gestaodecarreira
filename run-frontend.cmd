@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%frontend"
npm run dev
popd
