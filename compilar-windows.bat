@echo off
cd /d "%~dp0"
py -3.10 -m venv .venv
if errorlevel 1 goto error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install numpy pillow natsort "pyside6==6.5.3" pyqtdarktheme "psd-tools>=1.10.13" "pyinstaller==5.13.2"
if errorlevel 1 goto error
python -m PyInstaller --clean --noconfirm Build.spec
if errorlevel 1 goto error
echo Pronto: dist\SmartStitch\SmartStitch.exe
pause
exit /b 0
:error
echo Falha na compilacao. Leia a mensagem acima.
pause
exit /b 1
