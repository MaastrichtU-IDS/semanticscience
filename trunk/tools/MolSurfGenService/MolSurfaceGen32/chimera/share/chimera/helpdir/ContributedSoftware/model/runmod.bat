@echo off
rem Change VERSION below to update script for different version of Modeller
rem If necessary, change xxxxxx to be your Modeller license key and uncomment
rem 
set VERSION=9v2
rem set KEY_MODELLER%VERSION%=xxxxxx
set DIR=C:\Program Files\Modeller%VERSION%
set MODINSTALL%VERSION%=%DIR%
set PYTHONPATH=%DIR%\modlib;
set LIB_ASGL=%DIR%\asgl
set BIN_ASGL=%DIR%\bin
set PATH=%DIR%/bin;%PATH%
mod%VERSION%.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
