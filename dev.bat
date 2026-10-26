@echo off
setlocal
cd /d "%~dp0"
start "PetGarden API" cmd /k "uv run uvicorn petgarden.main:app --reload --port 8000"
start "PetGarden UI" cmd /k "cd frontend && npm run dev"

rem 等 API 和 Vite 两个端口都就绪后再打开浏览器，避免刷新前出现错误页
call :waitport 8000
call :waitport 5173
start "" http://127.0.0.1:5173
exit /b 0

:waitport
powershell -NoProfile -Command "for($i=0;$i -lt 240;$i++){try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('127.0.0.1',%~1);$c.Close();exit 0}catch{Start-Sleep -Milliseconds 500}};exit 1"
if errorlevel 1 echo [警告] 端口 %~1 在 120 秒内未就绪。
exit /b 0
