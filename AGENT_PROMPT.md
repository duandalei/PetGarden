# 给实现 Agent 的提示词

> **使用方法**：把本文件全文复制给另一个 Agent；工作目录设为 `C:\Users\段大磊\Desktop\PetGarden`。如果该 Agent 能读文件，先让它读 `REQUIREMENTS.md` 和 `reference/pet-sprite-demo.html`。

---

你是一名资深全栈工程师 + 交互设计师。请从零实现一个名为 **PetGarden（班级宠物园）** 的本地课堂宠物养成系统。新项目只以本提示词和 `REQUIREMENTS.md` 为准，从零实现。直接开始实现，不要只输出计划。

## 0. 工作目录与先读材料

工作目录：

```text
C:\Users\段大磊\Desktop\PetGarden
```

先读：

1. `REQUIREMENTS.md` —— 完整需求、规则、数据模型、API、验收清单。它是唯一需求来源。
2. `reference/pet-sprite-demo.html` —— 动态 SVG 宠物的技术原型。浏览器打开看效果，读源码看动画实现。
3. `README.md` —— 交接说明。

如果文件不存在，按本提示词实现，并在项目内补齐 README。

**所有实现都在本项目内完成**，只使用本提示词、`REQUIREMENTS.md` 和 `reference/` 中的材料。

---

## 1. 产品目标

做一个小学教师能在课堂上用的本地 Web 应用：

- 老师给学生加减分（P0 只有 ±1），学生的宠物实时成长、变表情、升级、进化。
- 同一班级可以投到大屏，全班看到自己的宠物。
- 有随机点名、班级管理、学生管理、宠物图鉴/换宠、数据导出导入。
- 本地优先、完全离线、数据只存在本机。
- 一条命令启动，不需要安装数据库服务。

核心原则：**课堂节奏优先、投影优先、温暖不幼稚、低分不羞辱、动画可关闭、误操作可撤销。**

---

## 2. 不可妥协的技术约束

1. **Python 环境用 uv 管理**，`.venv` 必须创建在项目根目录，不依赖其他 Python 环境管理器，不污染全局 Python。
2. **数据库只能用 SQLite**，文件在 `data/petgarden.db`，启用 WAL 和外键。
3. **宠物必须用内联 SVG 程序化绘制 + CSS 动画**，不得使用 `<img>`、PNG/WebP、外部图片、emoji 当宠物。
4. **运行时不请求任何外部资源**：无 CDN、无 Google Fonts、无远程图标/图片、无 telemetry。
5. **前端不引入大型 UI 组件库、Tailwind、Axios**。用 Vue 3 + TypeScript + 原生 CSS + 自建设计 token。
6. **不引入其他数据库、Docker、Redis、Celery、Alembic、JWT。** 单教师、本地、PIN + HttpOnly 签名 Cookie。
7. **规则只有一份实现**：等级、阶段、心情、换宠、神兽解锁、随机点名规则放在后端领域层；前端只负责展示，不复制阈值。
8. **每次有效加减分必须写 `score_events`，最近一次必须可撤销。**
9. **所有宠物动画必须支持 `prefers-reduced-motion` 和应用内「减少动效」开关。**
10. **P0 全部完成**，不要留下占位页面、假按钮、TODO。

---

## 3. 技术栈

| 层 | 选择 |
|---|---|
| Python | 3.12（uv 安装） |
| 环境 | uv，项目内 `.venv`，`pyproject.toml` + `uv.lock` |
| 后端 | FastAPI + SQLAlchemy 2.0（同步）+ Pydantic v2 |
| 数据库 | SQLite（WAL、外键、busy_timeout） |
| 认证 | PIN（scrypt）+ itsdangerous 签名 Cookie |
| 前端 | Vue 3 + TypeScript strict + Vite |
| 路由/状态 | Vue Router 4 + Pinia |
| 样式 | 原生 CSS + design tokens，不用 UI 框架 |
| 宠物 | 内联 SVG + CSS keyframes |
| 测试 | pytest + httpx；Vitest + @vue/test-utils |
| 代码质量 | ruff、vue-tsc、npm run build |

Python 依赖（运行时）：

```text
fastapi
uvicorn[standard]
sqlalchemy>=2.0
pydantic-settings
itsdangerous
```

开发依赖：

```text
pytest
httpx
ruff
```

前端依赖：

```text
vue
vue-router
pinia
```

开发依赖：

```text
vite
@vitejs/plugin-vue
typescript
vue-tsc
vitest
@vue/test-utils
jsdom
```

---

## 4. 初始化命令（必须实际执行）

在项目根目录执行：

```powershell
cd C:\Users\段大磊\Desktop\PetGarden
uv python install 3.12
uv python pin 3.12
uv init --package --name petgarden .
uv add fastapi "uvicorn[standard]" sqlalchemy pydantic-settings itsdangerous
uv add --dev pytest httpx ruff
uv sync
```

然后创建前端：

```powershell
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install vue-router pinia
npm install -D vitest @vue/test-utils jsdom
cd ..
```

验证：

```powershell
uv run python -c "import sys; print(sys.executable)"
# 必须指向 C:\Users\段大磊\Desktop\PetGarden\.venv\Scripts\python.exe

uv run uvicorn petgarden.main:app --port 8000
```

如果 `uv init --package` 的目录和下面的结构不一致，以本节的结构为准手工调整，但必须保留 `pyproject.toml`、`src/petgarden/`、`[project.scripts] petgarden = "petgarden.__main__:main"`、`uv.lock`。

---

## 5. 目录结构

```text
PetGarden/
├─ pyproject.toml
├─ uv.lock
├─ .python-version
├─ .gitignore
├─ README.md
├─ REQUIREMENTS.md
├─ AGENT_PROMPT.md
├─ start.bat
├─ dev.bat
├─ src/petgarden/
│  ├─ __init__.py
│  ├─ __main__.py          # CLI: serve / seed / reset-pin
│  ├─ main.py              # create_app()
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ security.py
│  ├─ deps.py
│  ├─ errors.py
│  ├─ domain/
│  │  ├─ pets.py
│  │  ├─ scoring.py
│  │  └─ rollcall.py
│  ├─ services/
│  │  ├─ roster.py
│  │  ├─ scoring.py
│  │  ├─ pet_progress.py
│  │  └─ backup.py
│  ├─ api/
│  │  ├─ auth.py
│  │  ├─ classes.py
│  │  ├─ students.py
│  │  ├─ scoring.py
│  │  ├─ pets.py
│  │  ├─ rollcall.py
│  │  ├─ data.py
│  │  └─ settings.py
│  ├─ seed.py
│  └─ static.py
├─ tests/
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.ts
│  ├─ index.html
│  └─ src/
│     ├─ main.ts
│     ├─ App.vue
│     ├─ router.ts
│     ├─ api/client.ts
│     ├─ api/types.ts
│     ├─ stores/
│     ├─ views/
│     │  ├─ SetupView.vue
│     │  ├─ LoginView.vue
│     │  ├─ ClassesView.vue
│     │  ├─ ClassView.vue
│     │  ├─ DisplayView.vue
│     │  ├─ SettingsView.vue
│     │  └─ NotFoundView.vue
│     ├─ components/
│     │  ├─ AppShell.vue
│     │  ├─ StudentCard.vue
│     │  ├─ StudentDrawer.vue
│     │  ├─ ScoreButtons.vue
│     │  ├─ ReasonSheet.vue
│     │  ├─ RollcallOverlay.vue
│     │  ├─ PetCollection.vue
│     │  ├─ ConfirmDialog.vue
│     │  ├─ ToastHost.vue
│     │  ├─ EmptyState.vue
│     │  └─ pets/
│     │     ├─ types.ts
│     │     ├─ visuals.ts
│     │     ├─ PetSprite.vue
│     │     ├─ PetFace.vue
│     │     ├─ StageAccessories.vue
│     │     ├─ CatPet.vue
│     │     ├─ DogPet.vue
│     │     ├─ RabbitPet.vue
│     │     ├─ PandaPet.vue
│     │     ├─ FoxPet.vue
│     │     ├─ DragonPet.vue
│     │     ├─ usePetMotion.ts
│     │     └─ pet.css
│     ├─ composables/
│     │  ├─ useScoring.ts
│     │  ├─ usePolling.ts
│     │  └─ useReducedMotion.ts
│     ├─ styles/
│     │  ├─ tokens.css
│     │  ├─ base.css
│     │  └─ components.css
│     └─ utils/
├─ data/                   # 运行时生成，gitignore
└─ reference/
   └─ pet-sprite-demo.html
```

---

## 6. 核心业务规则（必须精确实现）

### 6.1 积分

- 范围 0–100。
- P0 UI 只有 +1 / -1；API `delta` 允许 `[-5,5]` 的非零整数。
- 结果夹紧。夹紧后没有变化 → 409 `SCORE_AT_LIMIT`，不写事件。
- 每次有效操作写 `score_events`：`delta`、`score_before`、`score_after`、`reason`、`created_at`。
- 同步 `pet_progress.best_level`（只升不降）。

### 6.2 等级 / 阶段 / 心情

| score | level | stage | mood |
|---|---|---|---|
| 0–19 | 1 | 初遇 | sad |
| 20–39 | 2 | 相伴 | neutral |
| 40–59 | 3 | 默契 | neutral |
| 60–79 | 4 | 蜕变 | happy |
| 80–100 | 5 | 传说 | happy |

- 等级、阶段、心情全部由 score 派生，不存 students 表。
- `best_level` 存 `pet_progress`，历史最高，不随撤销/换宠下降。

### 6.3 撤销

- `POST /api/score-events/{id}/undo`
- 只能撤销该学生最新一条、未撤销事件。
- 当前分数必须等于事件 `score_after`；否则 409 `EVENT_NOT_LATEST`。
- 恢复 `score_before`，写 `undone_at`。
- 不降低 `best_level`。

### 6.4 换宠 / 神兽

- 当前等级 === 5（score ≥ 80）才能换。
- 目标不能是当前物种。
- 普通物种：cat / dog / rabbit / panda / fox；神兽：dragon。
- 神兽解锁：任意**普通**物种 `best_level === 5`。
- 换宠成功：species 改为目标；score = 0；目标 `pet_progress` 至少 L1；旧进度保留；播放毕业/迎新动画。
- 除换宠外，不提供直接改物种的入口。

### 6.5 随机点名

- 公平模式：排除缺席；按 `last_picked_at` 升序（NULL 最前）；取前 `max(1, ceil(n/3))`；随机 1 人；如果 >1 人且包含上次抽中者，排除后再抽；更新 `last_picked_at`。
- 可切换纯随机。
- 无学生 → 409 `NO_STUDENTS`。

### 6.6 教学语气

- 低分不标红、不排名、不流泪、不发抖。
- 减分反应是「耳朵下垂、头部微倾、身体轻微下沉」，不是惩罚性抖动。
- 大屏默认按座位排序；不显示名次。

---

## 7. 宠物 SVG 与动画（重点）

### 7.1 组件接口

`PetSprite.vue` 是唯一对外入口：

```ts
interface PetSpriteProps {
  species: 'cat' | 'dog' | 'rabbit' | 'panda' | 'fox' | 'dragon'
  level: 1 | 2 | 3 | 4 | 5
  mood: 'happy' | 'neutral' | 'sad'
  reaction?: { type: 'cheer' | 'comfort' | 'evolve'; nonce: number } | null
  seed: number | string
  size?: number
  label?: string
  decorative?: boolean
}
```

- 组件是纯展示，不发请求、不读 store。
- 不使用 `<img>`、`<image>`、base64、外部 URL、emoji。
- 所有颜色来自 `visuals.ts` + CSS 变量。
- 物种组件只负责剪影；`PetFace.vue` 负责表情；`StageAccessories.vue` 负责阶段饰品。

### 7.2 SVG 规范

- 统一 `viewBox="0 0 200 200"`，`overflow: visible`。
- 地面阴影：`ellipse cx=100 cy=178 rx=52 ry=8`，`#252A26`，`opacity .08`。
- 身体中心约 `(100,140)`，头中心约 `(100,92)`。
- 主轮廓描边 `#252A26`，2–2.5px，圆角线帽/连接。
- 每物种 3–4 个主色：body / belly / accent / inner ear。
- 不用 SVG `filter`、模糊、渐变网格、`foreignObject`。
- 高光/阴影用低透明度纯色形状。

### 7.3 阶段变化

| level | 整体缩放 | 新增视觉 |
|---|---|---|
| 1 | 0.88 | 幼小、头身比大、无饰品 |
| 2 | 0.94 | 围巾/项圈 |
| 3 | 1.00 | 胸前徽章/背包、脸颊纹样 |
| 4 | 1.05 | 背后虚线光环（旋转）、额头纹样 |
| 5 | 1.12 | 皇冠/角饰、亮光环、粒子环；青龙展开翅膀 |

饰品必须改变剪影，保证 80px 也能辨认。

### 7.4 表情

- happy：弯弯眼（弧线）、微笑、腮红、尾巴快。
- neutral：圆眼 + 高光、小微笑、正常尾巴。
- sad：垂眼、嘴角向下、耳朵下垂、尾巴慢而低；**不流泪、不变红**。
- cheer：闭眼笑、上跳 8px、放大 1.08、6 个火花，900ms。
- comfort：耳朵下垂、头部倾斜 4deg、整体下沉 2px，700ms。
- evolve：光环扩散到 1.6 倍并淡出、宠物 0.92→1.12→1、阶段徽章弹入，1100ms。

### 7.5 动画清单

| 名称 | 目标 | 时长 |
|---|---|---|
| `pet-breathe` | 身体组 | 3.2s infinite |
| `pet-bob` | 头部组 | 2.8s infinite |
| `pet-sway` | 尾巴组 | 2.4–3.4s infinite |
| `pet-ear` | 耳朵组 | 4.6s infinite |
| `pet-blink` | 眼睛组 | 4–7s infinite，scaleY 到 .08 |
| `pet-cheer` | 根组 | 900ms once |
| `pet-comfort` | 根组 | 700ms once |
| `pet-evolve` | 根组 + 光环 | 1100ms once |
| `pet-aura-spin` | L4/L5 光环 | 24s linear infinite |
| `pet-particle` | L5 粒子 | 3s infinite，≤ 8 个 |

**相位抖动**（每只宠物不同步）：

```ts
export function hash(seed: number | string) {
  const s = String(seed)
  let h = 2166136261
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

// 在 PetSprite 中
const h = hash(props.seed)
const motionStyle = {
  '--blink-duration': `${4 + (h % 30) / 10}s`,
  '--blink-delay': `-${(h % 50) / 10}s`,
  '--sway-duration': `${2.2 + (h % 12) / 10}s`,
  '--sway-delay': `-${(h % 20) / 10}s`,
}
```

### 7.6 反应触发

```ts
watch(
  () => props.reaction?.nonce,
  () => {
    if (!props.reaction) return
    reactionClass.value = `reaction-${props.reaction.type}`
    window.setTimeout(() => {
      reactionClass.value = ''
    }, props.reaction.type === 'evolve' ? 1100 : props.reaction.type === 'cheer' ? 900 : 700)
  },
)
```

- 初次渲染绝不播放 evolve。
- 父组件只在 `level` 从旧值升高时发 evolve；加分发 cheer；减分发 comfort。
- evolve 优先于 cheer。

### 7.7 减少动效

```css
@media (prefers-reduced-motion: reduce) {
  .pet-idle,
  .pet-aura,
  .pet-particle {
    animation: none !important;
  }
}

:root[data-motion="reduced"] .pet-idle,
:root[data-motion="reduced"] .pet-aura,
:root[data-motion="reduced"] .pet-particle {
  animation: none !important;
}

:root[data-motion="reduced"] .pet-reaction {
  animation-duration: 0.2s !important;
}
```

- 保留表情、数字、阶段饰品的变化。
- 粒子在 reduced 下不渲染。

### 7.8 性能

- 单只宠物 DOM ≤ 70 节点。
- 单屏 ≤ 60 只。
- 只动画 `transform` / `opacity`。
- 不在轮询时重新创建 SVG；用 `v-for :key="student.id"`。
- 粒子每只 ≤ 8 个，只在 L5/evolve 时出现。
- 若性能不足，按顺序降级：L5 粒子 → 光环旋转 → 耳朵/尾巴动画 → 只保留眨眼和表情。

### 7.9 参考原型

`reference/pet-sprite-demo.html` 可以直接打开。它演示了 6 种物种、5 阶段、3 心情、呼吸/眨眼/摇尾/光环、cheer/comfort/evolve、40 只宠物网格、减少动效。可以用 `?species=dragon&score=90&mood=happy` 直接预览指定状态。

**按上面的组件架构重写，不要直接把原型 HTML 塞进 Vue。** 原型中的路径/配色/动画手感可以复用，但要拆成 Vue 组件和共享 CSS。

---

## 8. 数据库

完整 SQL 见 `REQUIREMENTS.md` 第 13 章。必须包含：

- `settings`：key/value；`schema_version`、`teacher_name`、`pin_salt`、`pin_hash`、`motion_pref`、`display_sort`、`created_at`。
- `classes`：id、name、grade、color、sort_order、created_at、updated_at。
- `students`：id、class_id、name、student_no、seat_no、score 0–100、species、is_present、last_picked_at、created_at、updated_at。
- `pet_progress`：student_id + species 联合主键、best_level 1–5、first/last_reached_at。
- `score_events`：id、class_id、student_id、delta、score_before、score_after、reason、created_at、undone_at。

必须有的索引/约束：

```sql
CREATE INDEX idx_students_class_score ON students(class_id, score);
CREATE INDEX idx_students_class_seat  ON students(class_id, seat_no);
CREATE UNIQUE INDEX uq_students_class_no
  ON students(class_id, student_no)
  WHERE student_no IS NOT NULL AND student_no <> '';
CREATE INDEX idx_events_class_id   ON score_events(class_id, id DESC);
CREATE INDEX idx_events_student_id ON score_events(student_id, id DESC);
```

- 时间存 UTC ISO8601。
- 每个请求一个 Session；成功 commit，异常 rollback。
- 启动时自动建目录/建库/建表/写默认 settings。
- 不引入 Alembic；`settings.schema_version = "1"`。

---

## 9. API

完整契约见 `REQUIREMENTS.md` 第 14 章。P0 必须实现：

```text
GET    /api/health
GET    /api/auth/status
POST   /api/auth/setup
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/auth/change-pin

GET    /api/classes
POST   /api/classes
GET    /api/classes/{id}
PATCH  /api/classes/{id}
DELETE /api/classes/{id}

GET    /api/classes/{id}/students
POST   /api/classes/{id}/students
POST   /api/classes/{id}/students/bulk
GET    /api/students/{id}
PATCH  /api/students/{id}
DELETE /api/students/{id}

POST   /api/students/{id}/score
POST   /api/score-events/{id}/undo

GET    /api/pets
GET    /api/students/{id}/collection
POST   /api/students/{id}/switch-pet

POST   /api/classes/{id}/rollcall
GET    /api/classes/{id}/display

GET    /api/settings
PATCH  /api/settings
GET    /api/export
POST   /api/import
POST   /api/demo
```

要求：

- 统一错误：`{"error":{"code":"...","message":"中文可读"}}`。
- 未登录受保护接口 → 401 `AUTH_REQUIRED`。
- 校验错误 → 422 `VALIDATION_ERROR`。
- 学生响应包含派生字段：`level`、`stage`、`mood`、`score_percent`、`best_level`、`can_switch_pet`、`divine_unlocked`。
- 评分响应包含 `event`、`student`、`level_up`、`stage_changed`、`can_undo`。
- `/api/classes/{id}/display` 返回 class + students + server_time，供大屏 3 秒轮询。

---

## 10. 认证与安全

- PIN 4–6 位数字。
- 存储：`hashlib.scrypt(pin, salt=16字节, n=2**14, r=8, p=1, dklen=32)`，Base64 存 settings；用 `hmac.compare_digest` 校验。
- Cookie：`petgarden_session`，itsdangerous 签名，`HttpOnly`、`SameSite=Lax`、`Path=/`、`Max-Age=604800`。
- 签名密钥 `data/secret.key`，首次生成 32 字节 URL-safe 随机串；不提交 git；不放进导出。
- 登录失败 5 次/5 分钟限流，进程内即可。
- 生产同源，不配置 CORS，不使用 `allow_origins=["*"]`。
- 写操作若带 Origin，校验同源（开发允许 `http://127.0.0.1:5173` / `http://localhost:5173`）。
- 导入 ≤ 5MB、只解析 JSON、单事务、导入前自动备份。
- 不用 `v-html` 渲染用户输入。
- 不记录 PIN/Cookie/完整学生数据到日志。

---

## 11. 前端页面与交互

### 11.1 路由

```text
/setup                      首次设置
/login                      登录
/                           班级列表
/class/:id                  课堂工作台
/class/:id/collection/:sid  图鉴（也可用抽屉）
/display/:id                大屏展示
/settings                   设置
/:pathMatch(.*)*            404
```

### 11.2 页面

**Setup / Login**

- 首次启动检测 `/api/auth/status`。
- Setup：教师名、PIN、确认 PIN、可选创建示例班级。
- Login：数字键盘 + 键盘输入 + Enter；错误提示；5 次锁定倒计时。
- 登录后进入首页或 `next` 指定的页面。

**班级列表 `/`**

- 卡片：班级名、年级、学生数、平均分、3 个宠物缩略图、班级色条。
- 新建/编辑/删除；删除输入班级名确认。
- 空状态 + 创建按钮。
- 记住上次班级并高亮，但不自动跳转。

**工作台 `/class/:id`（核心）**

- 顶栏：返回、班级名、学生数、搜索、排序、随机点名、大屏、添加学生、更多。
- 网格：`repeat(auto-fill, minmax(168px, 1fr))`，间距 14–16px。
- 学生卡片：
  - 宠物 SVG 96–120px
  - 姓名 ≥16px/700
  - 学号/座位号
  - 积分大号衬线数字 ≥28px
  - 等级/阶段徽章
  - 进度条
  - `-1` / `+1` 44px 高
  - 物种色细边；不靠颜色区分状态
- 点击 +1/-1：
  - 乐观更新数字/心情
  - 调 API
  - 成功校准；失败回滚 + toast
  - 同一学生请求未返回时按钮禁用 200ms
  - 升级时播放 evolve；加分 cheer；减分 comfort
- 顶部提示条：最近一次操作 + 撤销，6 秒消失。
- 原因面板：加分/减分各至少 4 个预设，执行 ±1。
- 学生详情抽屉：宠物、分数、等级、阶段、学号/座位、最近事件、撤销、图鉴/换宠、编辑、删除。
- 空状态/加载 skeleton/错误重试。

**图鉴/换宠**

- 6 个物种卡片：SVG 预览、best_level 圆点、当前标记、神兽锁、换宠按钮。
- 换宠条件 L5；神兽需任意普通 L5；二次确认积分归零。
- 成功后播放毕业/迎新动画。
- 图鉴 best_level 只增不减。

**随机点名**

- 全屏浮层；大宠物 + 姓名 + 班级名 + 候选人数。
- Space/Enter 重抽；Esc 关闭；触屏大按钮。
- 焦点锁定与恢复；`aria-live` 播报结果。
- 减少动效时直接显示结果。

**大屏 `/display/:id`**

- 无侧栏、无操作按钮。
- 顶部细栏鼠标移动出现、3 秒淡出：班级名、学生数、排序、退出。
- 网格：宠物 96–160px、姓名 ≥24px、积分 ≥32px、阶段徽章。
- 默认按座位排序，可切积分；不显示名次。
- 每 3 秒轮询 `/display`；页面隐藏暂停；恢复立即拉取。
- 积分变化平滑过渡；升级播放 evolve；不重新创建列表。
- 失败显示「连接中断，正在重试」，不弹窗。

**设置**

- 教师名、改 PIN、动效（跟随系统/减少）、数据路径、导出、导入（输入 REPLACE）、创建示例班级、版本/构建时间、隐私说明。
- 导出不含 PIN 哈希/secret。
- 导入前自动备份 `data/backups/pre-import-*.json`。

### 11.3 视觉

使用 `REQUIREMENTS.md` 第 10 章的 token。核心：

```css
--paper: #FAF6EC;
--surface: #FFFDF7;
--surface-sunken: #F1E9DA;
--line: #DED3BF;
--ink: #252A26;
--ink-soft: #5F665D;
--moss: #4F6F52;
--moss-deep: #3E5A42;
--clay: #B85C3E;
--honey: #D99B2B;
--sky: #6BA6BC;
--radius-md: 16px;
--radius-lg: 24px;
--shadow-card: 0 8px 24px rgba(63,52,35,.07);
--font-ui: "Microsoft YaHei UI", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
--font-display: "Georgia", "Songti SC", "SimSun", serif;
```

- 不用蓝白渐变、玻璃拟态、霓虹、通用 SaaS 仪表盘。
- 宠物是唯一高饱和焦点。
- 姓名/积分/宠物大小优先于装饰。
- 正文对比度 ≥4.5:1，大字 ≥3:1。
- 所有动画支持 reduced motion；触控目标 ≥44px。
- 不依赖颜色传达状态；分数/等级/阶段都有文字。

---

## 12. 开发顺序（必须按此推进）

1. **M0 脚手架**：uv、FastAPI、SQLite、health、Vite 骨架、start.bat。
2. **M1 数据与认证**：表、PIN、Cookie、setup/login、班级/学生 CRUD、批量导入。
3. **M2 积分引擎**：评分、事件、撤销、等级/心情、进度同步、领域测试。
4. **M3 宠物与工作台**：SVG 6×5、动画、学生卡片、详情、图鉴/换宠。
5. **M4 课堂场景**：随机点名、大屏轮询、设置/导出/导入/示例数据。
6. **M5 打磨**：响应式、空/错/加载态、减少动效、性能、README、全量验收。

每完成一个阶段，运行对应测试，不要等最后才跑。

---

## 13. 启动、构建与脚本

开发：

```powershell
uv run uvicorn petgarden.main:app --reload --port 8000
# 另一个终端
cd frontend
npm run dev
```

生产：

```powershell
cd frontend
npm run build
cd ..
uv run petgarden serve
```

`start.bat`：

```bat
@echo off
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
start "" http://127.0.0.1:8000
uv run petgarden serve --host 127.0.0.1 --port 8000
```

`dev.bat`：

```bat
@echo off
cd /d "%~dp0"
start "PetGarden API" cmd /k "uv run uvicorn petgarden.main:app --reload --port 8000"
start "PetGarden UI" cmd /k "cd frontend && npm run dev"
timeout /t 2 >nul
start "" http://127.0.0.1:5173
```

- 生产默认绑定 `127.0.0.1`。
- 局域网访问需显式 `--host 0.0.0.0`；README 说明风险。
- FastAPI 在生产模式下挂载 `frontend/dist`，非 `/api`、非 `/assets` 的 GET 返回 `index.html`。
- `dist` 不存在时返回清晰的构建提示，不 500。
- `/api/*` 未匹配返回 JSON 404，不返回 HTML。

---

## 14. 测试与质量门禁

必须写并跑通：

```powershell
uv run ruff check .
uv run pytest -q
cd frontend
npm run typecheck
npm run test -- --run
npm run build
```

至少覆盖：

- 等级/阶段/心情边界（0/19/20/39/40/59/60/79/80/100）。
- 评分 +1/-1、0/100 边界、事件写入、best_level 同步。
- 撤销：成功、非最新、重复撤销。
- 换宠：L4 拒绝、L5 成功、神兽锁定/解锁、积分归零、旧进度保留。
- 随机点名：公平候选池、排除缺席、空班。
- 班级/学生 CRUD、重复学号、批量导入预览。
- 认证：setup 只能一次、错误 PIN、登录/登出/改 PIN、未登录 401。
- 导出/导入往返、坏文件回滚、REPLACE 确认。
- `PetSprite` 6 物种 × 5 等级 × 3 心情渲染 `<svg>` 且不含 `<img>`。
- reduced motion 类/属性生效。

---

## 15. 手工验收（完成前逐条执行）

1. 干净启动，首次设置 PIN，创建示例班级。
2. 断网刷新，全功能可用；Network 无外部请求。
3. 40 人班级工作台流畅；宠物不同步眨眼。
4. +1 100ms 内反馈，播放 cheer；-1 播放 comfort。
5. 加分到 20/40/60/80，阶段依次变化，播放 evolve。
6. 100 分继续 +1 友好提示；0 分继续 -1 友好提示。
7. 撤销成功；非最新撤销被拒绝；刷新后数据一致。
8. 图鉴 6 物种；L4 不能换；L5 能换；神兽锁定/解锁正确。
9. 换宠后积分归零、新宠物 L1、旧进度保留。
10. 随机点名公平、排除缺席、Space/Esc 可用。
11. 大屏 3 秒内更新；升级有动画；无操作按钮；1920×1080 可读。
12. 减少动效停止循环动画，数据和表情仍正确。
13. 导出/导入往返一致；坏文件不破坏数据；导入前备份存在。
14. 删除班级需输入名称；删除学生级联清理。
15. 浏览器控制台无 error；四个质量门禁全绿。

---

## 16. 最终报告格式

完成后用中文向用户汇报：

1. **已完成模块**：逐项列出 P0。
2. **启动方式**：`uv sync`、`npm install`、`npm run build`、`start.bat` 或 `uv run petgarden serve`。
3. **测试结果**：ruff、pytest、typecheck、vitest、build 的实际输出摘要。
4. **手动验收结果**：第 15 章逐条通过/未通过。
5. **已知限制**：只列真实存在的，不要隐瞒。
6. **数据位置与备份方式**。
7. **下一步建议**（P1 可选项）。

不要只说「完成了」而不给验证结果。

---

## 17. 明确不要做的事

- 不要引入其他数据库、静态 PNG 宠物图、大型 UI 组件库；宠物必须是 SVG。
- 不要用图片/emoji 代替 SVG 宠物。
- 不要引入 CDN 字体、图标、图片。
- 不要做多教师、学生登录、云同步。
- 不要做排行榜、公开倒数、红色失败警示、低分羞辱。
- 不要用 JWT、`allow_origins=["*"]`、把 PIN 存前端。
- 不要引入 Docker、Redis、Celery、Alembic。
- 不要把 `data/`、`.venv/`、`node_modules/`、`secret.key` 提交到 git。
- 不要留下占位页面、假按钮、TODO。
- 不要只输出计划而不实现。

---

## 18. 完成定义

- P0 全部功能可用。
- 第 15 章验收全部通过。
- 四个质量门禁全绿。
- 断网运行正常，无外部请求。
- 新机器按 README 可从零启动。
- 宠物是动态 SVG，6 物种 × 5 阶段，动画可关闭。
- 数据可导出/导入，误操作可撤销。
- 代码结构清晰，规则只有一份实现。

开始实现。先建立 uv + FastAPI + SQLite + Vite 骨架，然后按 M1 → M2 → M3 → M4 → M5 推进。
