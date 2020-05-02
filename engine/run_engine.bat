@echo off

pushd %~dp0
call python\scripts\activate.bat
python engine.py

@echo on