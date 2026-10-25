@echo off
rem Ambessa's pose pack with League's own frames (tools/art/pack_ambessa_poses.py): double-click it in Explorer -
rem from tools\art in the clone, from the clone's top folder, or from anywhere (it then asks where the clone is).
rem It updates the branch, renders League's frame for every pose from the local client, writes the pack (and its zip)
rem and the check sheet (each skeleton beside League's frame), then opens the folder.
setlocal
set LOL=D:\WeGameApps\lol
set BRANCH=claude/nifty-hypatia-462gjk
set WORK=C:\t\am_work
set PYTHONUTF8=1
set REPO=%~dp0..\..
if not exist "%REPO%\.git" set REPO=%~dp0
if exist "%REPO%\.git" goto :repo
echo Paste or drag the folder of your TFM2-League-Heroes clone here and press Enter.
echo Just press Enter if you have none: it is cloned into C:\t\TFM2-League-Heroes.
set REPO=
set /p REPO=Folder: 
if defined REPO set REPO=%REPO:"=%
if not defined REPO set REPO=C:\t\TFM2-League-Heroes
if exist "%REPO%\.git" goto :repo
if exist "%REPO%" (
  echo Not a git clone: %REPO%
  goto :fail
)
echo === cloning the repository into %REPO% ===
git clone https://github.com/BoDUD/TFM2-League-Heroes.git "%REPO%" || goto :fail
:repo
cd /d "%REPO%"

echo === 1/3 updating the branch %BRANCH% ===
git fetch origin %BRANCH% || goto :fail
git checkout %BRANCH% || goto :fail
git pull --ff-only origin %BRANCH% || goto :fail

if not exist "%LOL%\Game\DATA\FINAL\Champions\Ambessa.wad.client" (
  echo League client not found at %LOL% - edit the LOL line at the top of this file.
  goto :fail
)

echo === 2/3 the pose pack with League's frames (a few minutes) ===
python tools\art\pack_ambessa_poses.py --out "%WORK%\ambessa_pose_pack" --lol "%LOL%" || goto :fail

echo === 3/3 the check sheet: skeletons beside League's frames ===
python tools\art\pack_ambessa_poses.py --check "%WORK%\ambessa_pose_check" --lol "%LOL%" || goto :fail

echo.
echo Done: %WORK%\ambessa_pose_pack.zip  (give it to Codex with POSE_PROMPTS.md)
echo       %WORK%\ambessa_pose_check\poses_check.png  (send it to Claude to fit the skeletons)
explorer "%WORK%"
pause
exit /b 0

:fail
echo.
echo Something failed - copy the messages above to Claude.
pause
exit /b 1
