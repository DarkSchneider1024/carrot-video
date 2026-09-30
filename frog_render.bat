@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo started %date% %time% > _frog_render_log.txt
python "..\.agents\skills\fairytale_video_generator\scripts\render_fairytale_video.py" --script 青蛙王子/story_script.json --output "青蛙王子/video/青蛙王子_1080p.mp4" >> _frog_render_log.txt 2>&1
echo EXIT %errorlevel% %date% %time% >> _frog_render_log.txt
