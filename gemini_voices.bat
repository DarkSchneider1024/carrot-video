@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo started %date% %time% > _gemini_voices_log.txt
set PY=python
py -3.11 -c "import playwright" >nul 2>&1 && set PY=py -3.11
%PY% -u live2d\run_gemini.py voices >> _gemini_voices_log.txt 2>&1
echo EXIT %errorlevel% %date% %time% >> _gemini_voices_log.txt
