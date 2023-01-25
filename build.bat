@echo off

call venv\scripts\activate
venv\scripts\pyinstaller --add-data assets;assets ^
            --add-data venv\Lib\site-packages\wsdl;wsdl ^
            --icon "assets\favicon.ico" ^
            --name "Camera Controller" ^
            --noconsole ^
            --clean ^
            --windowed ^
            --log-level DEBUG ^
            controls.py

"C:\Program Files (x86)\NSIS\makensis.exe" install.nsi

RMDIR /Q/S build
rm "Camera Controller.spec"


echo Build completed.
pause