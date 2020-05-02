@echo off

pushd %~dp0
call python\scripts\activate.bat
python zmq_server.py

@echo on