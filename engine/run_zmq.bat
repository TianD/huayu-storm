@echo off

pushd %~dp0
set PYTHONPATH=%cd%\venv\Lib;%cd%\venv\scripts;
set PATH=%cd%\venv\scripts;%PATH%
python zmq_server.py

@echo on