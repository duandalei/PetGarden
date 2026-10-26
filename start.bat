@echo off
setlocal
cd /d "%~dp0"
if not exist .venv (
  uv sync
)
if not exist frontend\dist (
  pushd frontend
  call npm install
  call npm run build
  popd
)

rem 等 8000 端口真正可连接后再打开浏览器，避免浏览器先于服务启动而报“无法加载此网络”
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "for($i=0;$i -lt 240;$i++){try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('127.0.0.1',8000);$c.Close();Start-Process 'http://127.0.0.1:8000';exit}catch{Start-Sleep -Milliseconds 500}}"

uv run petgarden serve --host 127.0.0.1 --port 8000
