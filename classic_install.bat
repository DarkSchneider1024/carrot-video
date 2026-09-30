@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import zipfile;zipfile.ZipFile('classic_update.zip').extractall('.');print('ok')" > _classic_install_log.txt 2>&1
