# PetGarden · 班级宠物园

给小学教师用的本地课堂宠物养成工具：老师给学生的课堂表现加减分，学生的宠物实时成长、变表情、升级、进化；全班宠物可以投到教室大屏上。**本地优先、完全离线、无登录、数据只存在本机。**

本项目定位为**个人本地使用**：`git clone` 到本机、装好依赖即可运行，无需注册账号或任何云端服务。

技术栈：Python 3.12 + uv + FastAPI + SQLite；Vue 3 + TypeScript + Vite；宠物为内联 SVG + CSS 动画，无图片资源。

## 环境要求

- Windows 10/11（macOS/Linux 也可运行）
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- Node.js 20+ 与 npm 10+（仅首次构建前端需要）

## 首次配置（clone 后只需做一次）

```powershell
git clone <仓库地址> PetGarden
cd PetGarden

# 1. 安装后端依赖（自动创建项目内 .venv）
uv sync

# 2. 安装前端依赖并构建静态页面
cd frontend
npm install
npm run build
cd ..
```

配置完成。项目内会多出 `.venv/`、`frontend/dist/` 两个目录（均已被 `.gitignore` 忽略）。

## 启动

双击 `start.bat`，或手动执行：

```powershell
uv run petgarden serve           # 默认 http://127.0.0.1:8000
```

浏览器打开 `http://127.0.0.1:8000` 即可直接使用，进入班级列表页，手动创建你的第一个班级。

`start.bat` 会自动检测：缺少 `.venv` 时先 `uv sync`，缺少 `frontend/dist` 时先构建前端，然后启动服务并打开浏览器。

## 开发模式

双击 `dev.bat`（后端 8000 热重载 + 前端 5173 热更新），或手动开两个终端：

```powershell
uv run uvicorn petgarden.main:app --reload --port 8000
cd frontend && npm run dev
```

## 常用命令

```powershell
uv run petgarden serve [--host 127.0.0.1] [--port 8000]   # 启动
uv run pytest -q                                          # 后端测试
uv run ruff check .                                       # Python 静态检查
cd frontend && npm run typecheck && npx vitest run && npm run build   # 前端检查/测试/构建
```

## 数据位置与备份

- 数据库：`data/petgarden.db`（SQLite，WAL + 外键）
- 设置页可**导出 JSON 备份**（含班级/学生/积分/图鉴；文件含学生姓名，请妥善保管）。
- 导入备份为**替换式**：需在设置页输入 `REPLACE` 确认；导入前自动写一份 `data/backups/pre-import-*.json`。
- 换电脑：复制 `data/` 目录，或在新机器上导入导出的 JSON。

## 局域网访问（可选）

默认只监听本机 `127.0.0.1`。如需同网段设备（如教室大屏盒）访问：

```powershell
uv run petgarden serve --host 0.0.0.0 --port 8000
```

**注意**：本系统没有登录机制，监听 `0.0.0.0` 意味着同网段任何设备都能访问并修改数据，请仅在可信网络中临时使用。

## 故障排查

| 症状 | 处理 |
|---|---|
| 端口被占用 | `uv run petgarden serve --port 8001` 换端口 |
| 前端白屏提示未构建 | `cd frontend && npm run build` 后重启 |
| 数据库损坏 | 删除 `data/petgarden.db` 会丢失数据；先从 `data/backups/` 或导出文件恢复 |
| 升级依赖后异常 | `uv sync --reinstall` 重建 `.venv` |

## 质量门禁

```powershell
uv run ruff check .
uv run pytest -q
cd frontend
npm run typecheck
npx vitest run
npm run build
```

## 隐私

运行时不发起任何外部网络请求（无 CDN、无字体、无统计上报）。所有数据保存在本机 `data/` 目录。
