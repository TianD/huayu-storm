@echo off

pushd %~dp0
call venv\scripts\activate.bat
python zmq_server.py

@echo on