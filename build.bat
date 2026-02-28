@echo off
echo Activating Virtual Environment...
call venv\Scripts\activate.bat

echo Installing PyInstaller if not installed...
pip install pyinstaller

echo Building Smart POS...
pyinstaller smart_pos.spec --noconfirm

echo Copying additional resources...
if not exist dist\SmartPOS\database mkdir dist\SmartPOS\database
copy database\schema.py dist\SmartPOS\database\
copy database\seed.py dist\SmartPOS\database\

echo Build Complete! Output is in dist\SmartPOS\
pause
