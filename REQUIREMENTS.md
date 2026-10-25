# PetGarden · 班级宠物园
## 产品与技术需求文档（v1.0）

| 项目 | 内容 |
|---|---|
| 文档状态 | 已定稿，可直接进入实现 |
| 日期 | 2026-10-25 |
| 产品代号 | PetGarden |
| 中文名 | 班级宠物园 |
| 目标平台 | Windows 10/11 本地 Web 应用；可选局域网访问 |
| 技术基线 | Python 3.12 + uv + FastAPI + SQLite；Vue 3 + TypeScript + Vite |
| 交付标准 | P0 全部完成，验收清单全部通过 |

---

## 0. 文档定位

本文档是新项目 **PetGarden** 的唯一需求来源。它同时服务于三类读者：

1. **产品/设计**：第 1–11 章定义产品、规则、页面和视觉。
2. **实现 Agent**：第 12–16 章定义技术架构、数据模型、API 和质量门槛。
3. **验收者**：第 17–18 章定义可逐条执行的验收步骤。

需求已经做完取舍。实现时遇到文档未覆盖的细节，按「更简单、更本地、更少依赖」的原则选择，不要引入文档之外的大型框架或服务。

---

## 1. 产品定义

**一句话**：PetGarden 是一个给小学教师用的本地课堂宠物养成工具。老师给学生的课堂表现加减分，学生的宠物随之成长、进化、解锁新伙伴；同一个班级可以投到大屏上，让全班看到自己的宠物。

**它是什么**：

- 课堂上 3 秒内完成的加减分工具
- 一个适合投影展示的「全班宠物园」
- 一个本地、离线、数据完全属于老师的桌面 Web 应用
- 一个把课堂反馈变成可见成长的小型激励系统

**它不是什么**：

- 不是成绩录入、教务管理、家校沟通系统
- 不是学生自己登录玩的游戏
- 不是多教师协作 SaaS
- 不是排行榜或竞争工具

**核心循环**：

```
课堂表现 → 老师 +1 / -1 → 宠物表情与等级变化 → 大屏可见
        → 学生获得即时反馈 → 更愿意参与课堂 → 回到第一步
```

---

## 2. 项目背景与设计目标

小学课堂里，老师需要一种不打断教学节奏、又能让学生马上看见反馈的激励方式。口头表扬、小红花和积分表都有效，但缺少持续性和可见的成长感。

PetGarden 用「宠物养成」承载课堂反馈：

- 学生每次课堂表现被老师记录为积分；
- 积分决定宠物的等级、形态和心情；
- 全班宠物可以投到教室大屏上，让成长被看见；
- 所有数据留在本机，老师不需要配置服务器。

### 2.1 设计目标

| 目标 | 具体做法 |
|---|---|
| 课堂节奏优先 | ±1 操作 ≤ 2 次点击；100ms 内出现视觉反馈 |
| 投影优先 | 大字号、高对比、无操作按钮的大屏模式 |
| 本地优先 | SQLite 单文件；uv 管理 Python；运行时零外部请求 |
| 宠物有生命感 | 内联 SVG + CSS 动画；呼吸、眨眼、摇尾、心情、进化 |
| 可逆与可追溯 | 每次积分写事件；最近一次可撤销 |
| 数据可迁移 | JSON 导出/导入；导入前自动备份 |
| 不羞辱学生 | 不排名、不标红，低分用「需要鼓励」表达 |
| 动效可关闭 | 尊重 `prefers-reduced-motion`，并提供应用内开关 |

### 2.2 设计取舍

- 单教师、本地工作区，不做多教师协作或云同步。
- 6 种宠物 × 5 个阶段，用程序化 SVG 绘制，不依赖静态图片。
- 积分范围 0–100，等级由积分实时派生，不冗余存储。
- 大屏用 3 秒轮询保持同步，P1 再考虑 SSE。

---

## 3. 用户与场景

### 3.1 主用户：小学教师

- 使用设备：Windows 教室电脑 / 笔记本，外接投影或大屏
- 使用时刻：课前 1 分钟、课堂间隙、课后整理
- 注意力：被学生和教学节奏切得很碎，不能学习复杂界面
- 技术水平：会使用浏览器、微信、PPT；不一定会配置数据库
- 核心诉求：**快、稳、别出错、投影好看**

### 3.2 次用户：学生

- 不登录、不操作
- 通过投影看到自己的宠物、名字、积分、阶段
- 需要「被看见」而不是「被排名」；低分不应被公开羞辱

### 3.3 典型场景

| 场景 | 行为 | 设计含义 |
|---|---|---|
| 课前 | 打开电脑，启动 PetGarden，投影 | 一条命令启动；默认进入上次班级 |
| 课堂提问 | 随机点名 | 全屏浮层，Space 重抽，Esc 关闭 |
| 学生回答得好 | 点 +1 | 两次点击内完成；宠物立即欢呼 |
| 学生走神 | 点 -1 | 温和反馈；不刺眼、不羞辱 |
| 小组活动 | 连续给多人加分 | 卡片网格；P1 支持批量 |
| 课间 | 查看谁快满级、换宠物 | 图鉴/换宠对话框 |
| 家长会 | 投影全班宠物 | 大屏模式，字号大、无操作按钮 |
| 换电脑 | 导出 JSON，在新电脑导入 | 数据可迁移，不绑机器 |

---

## 4. 产品原则

1. **课堂节奏优先**：任何高频操作不超过 2 次点击，视觉反馈在 100ms 内出现。
2. **投影是第一界面**：大屏不是附属页面，而是产品最常被看到的样子；先保证远距离可读，再谈精致。
3. **温暖但不幼稚**：像一间用心布置的教室，不像儿童游乐场；老师用不尴尬，学生看会开心。
4. **宠物是反馈，不是装饰**：每一次动画都对应一个状态变化（加分、减分、升级、换宠），不做无意义的循环特效。
5. **本地优先、离线可用**：运行时不请求任何外部资源；数据只在本机。
6. **不公开排名、不公开羞辱**：默认按座位/姓名排序；低分宠物是「需要鼓励」，不是「最后一名」。
7. **可逆**：误点 +1/-1 可以撤销；删除班级需要输入班级名确认。
8. **动效可关闭**：尊重 `prefers-reduced-motion`，并提供「减少动效」设置。

---

## 5. 成功标准

### 5.1 用户体验

- 新用户从双击 `start.bat` 到完成 PIN 设置、创建班级、给第一个学生加分，**≤ 3 分钟**。
- 高频加分操作 **≤ 2 次点击**，点击后 100ms 内看到数字和宠物反应。
- 40 人班级在大屏上无需滚动即可看到全班（1920×1080）。
- 在 8 米距离、普通教室投影环境下，学生姓名和积分清晰可读。
- 断网后刷新页面，所有 P0 功能正常。

### 5.2 工程质量

- `uv run pytest` 全部通过；领域规则测试覆盖 ≥ 90%。
- `uv run ruff check` 无错误。
- `npm run typecheck` 无错误；`npm run build` 成功。
- 浏览器控制台无 error；Network 面板无外部域名请求。
- 50 人班级、工作台滚动时，CSS 动画不引起明显掉帧（集成显卡目标 50–60fps）。
- 除首次 `uv sync` / `npm install` 外，运行时不依赖网络。

---

## 6. 范围

### 6.1 P0（必须完成）

| 模块 | 内容 |
|---|---|
| 首次启动 | 教师姓名 + 4–6 位 PIN 设置；登录/登出；7 天签名 Cookie |
| 班级 | 创建、重命名、改颜色/年级、删除（输入班级名确认） |
| 学生 | 单个添加、批量粘贴导入、编辑、删除、搜索、按座位/姓名/积分排序 |
| 课堂工作台 | 学生卡片网格、±1 快捷评分、原因选择、最近一次撤销 |
| 宠物系统 | 5 普通 + 1 神兽 × 5 阶段；SVG 动画；3 种心情；升级/减分反应 |
| 换宠与图鉴 | 满级换宠、神兽解锁、图鉴进度、换宠确认 |
| 随机点名 | 公平模式、排除缺席、全屏浮层、Space/Esc |
| 大屏展示 | 独立路由、全班网格、3 秒轮询、投影可读 |
| 数据 | JSON 导出/导入（替换式）、导入前自动备份、示例数据 |
| 设置 | 教师名、改 PIN、动效偏好、数据路径、版本 |
| 工程 | uv + SQLite + 一条命令启动、测试、README、start.bat |

### 6.2 P1（P0 完成后再做）

- 批量评分（多选卡片，一次 ±1）
- 学生「缺席」开关（只影响随机点名）
- 学生积分历史抽屉（最近 20 条，可撤销最近一条）
- 大屏「投影增强」模式（更大字号、更高对比）
- 自动备份（每天首次启动，保留 7 份）
- SSE 实时推送（替代或补充轮询）
- 键盘快捷键（`+` / `-` / `Space` / `Esc`）
- 合成音效（默认关闭，无音频文件，WebAudio 生成）
- 第二只神兽「朱雀」

### 6.3 P2（未来）

- sprite-sheet 高质量宠物美术替换
- 班级归档、学期重置
- 家长会展示模式
- PWA / 安装到桌面
- 多设备大屏 token
- 数据统计图表
- 英文界面

### 6.4 明确不做

- 多教师账号、学生账号、家长账号
- 云同步、远程数据库、账号体系
- 成绩、考勤、作业、家校沟通
- 排行榜、公开倒计时、惩罚性特效
- 上传宠物图片、用户自定义美术
- 聊天、AI 对话、支付
- Docker、Redis、Celery、微服务、Alembic
- 自动更新器、Windows 安装包（P2 再议）

---

## 7. 核心概念与规则

### 7.1 实体

| 实体 | 说明 |
|---|---|
| 工作区 Workspace | 单教师工作区；没有多租户概念 |
| 班级 Class | 一个学生分组，拥有名称、年级、颜色 |
| 学生 Student | 班级成员，拥有姓名、学号、座位号、积分、当前宠物 |
| 宠物物种 Species | 6 种之一：cat / dog / rabbit / panda / fox / dragon |
| 积分 Score | 0–100 整数，决定等级与心情 |
| 等级 Level | 1–5，由积分实时计算，不单独存储 |
| 阶段 Stage | 等级的展示名：初遇 / 相伴 / 默契 / 蜕变 / 传说 |
| 养宠进度 Progress | 学生对每个物种达到过的最高等级，只升不降 |
| 积分事件 ScoreEvent | 一次加减分的审计记录，支持撤销 |

### 7.2 积分规则

- 积分范围：**0–100（含端点）**。
- 快捷操作：**+1 / -1**。
- API 接受整数 `delta`，范围 `[-5, 5]` 且不能为 0；UI P0 只发送 ±1。
- 结果夹紧到 0–100。若夹紧后分数没有变化（例如 100 分再 +1），**不创建事件**，返回 `409 SCORE_AT_LIMIT`，前端提示「已经满 100 分啦」。
- 每次有效加减分创建一条 `score_events`：
  - `delta`、`score_before`、`score_after`、`reason`（可空，≤ 60 字）、`created_at`
  - 同时同步 `pet_progress.best_level`
- 积分不因日期、课程、刷新而重置。只有「换宠」会把当前积分重置为 0。
- 撤销规则：
  - 只能撤销某学生**最新一条、未撤销**的积分事件。
  - 且该学生当前积分必须等于事件的 `score_after`；否则说明之后还有操作，返回 `409 EVENT_NOT_LATEST`。
  - 撤销后：学生积分恢复为 `score_before`；事件写入 `undone_at`；**不降低** `pet_progress.best_level`（图鉴记录的是「曾经达到」，不是当前等级）。
  - 撤销不会删除事件，历史仍可追溯。

### 7.3 等级与阶段

| 积分 | 等级 | 阶段名 | 视觉关键词 |
|---|---|---|---|
| 0–19 | L1 | 初遇 | 幼小、圆头、淡色、无饰品 |
| 20–39 | L2 | 相伴 | 稍大、围巾/项圈 |
| 40–59 | L3 | 默契 | 徽章/背包、脸颊纹样 |
| 60–79 | L4 | 蜕变 | 光环、额头纹样、色彩更饱和 |
| 80–100 | L5 | 传说 | 皇冠/翅膀、粒子环、体型最大 |

- `level = 1 if score < 20; 2 if < 40; 3 if < 60; 4 if < 80; else 5`
- 等级由积分实时计算，数据库**不存** `level` 字段。
- `best_level` 存在 `pet_progress`，只增不减。

### 7.4 心情

| 心情 | 条件 | 表现 |
|---|---|---|
| happy | score ≥ 60 | 弯弯眼、微笑、腮红、尾巴快 |
| neutral | 20 ≤ score < 60 | 圆眼、小微笑、正常尾巴 |
| sad | score < 20 | 垂眼、耳朵下垂、尾巴慢而低；**不流泪、不红色警示** |

瞬时反应（不持久化，由前端控制时长）：

| 反应 | 触发 | 时长 | 表现 |
|---|---|---|---|
| cheer | 加分成功 | 900ms | 闭眼笑、向上弹跳、6 个火花 |
| comfort | 减分成功 | 700ms | 耳朵下垂、头部微倾、身体轻微下沉（不抖动） |
| evolve | 等级上升 | 1100ms | 光环扩散、缩放、8 片叶子/花瓣粒子、阶段徽章弹入 |

### 7.5 宠物物种

| id | 名称 | 类型 | 剪影特征 | 主色 |
|---|---|---|---|---|
| cat | 小猫 | 普通 | 三角耳、卷尾、胡须 | 奶油橘 |
| dog | 小狗 | 普通 | 垂耳、口鼻、摇尾 | 蜜糖棕 |
| rabbit | 小兔 | 普通 | 长耳、圆尾、粉内耳 | 云朵白粉 |
| panda | 熊猫 | 普通 | 圆耳、黑眼斑、竹叶 | 墨白 |
| fox | 小狐 | 普通 | 尖耳、大尾巴、奶油口鼻 | 晚霞橙 |
| dragon | 青龙 | 神兽 | 龙角、龙须、翅膀、盘尾 | 青绿 |

- 新建学生：默认从 5 种普通宠物中随机分配；添加表单可选指定普通物种。
- 神兽不能直接分配，必须解锁后通过换宠获得。

### 7.6 换宠与神兽解锁

- 换宠条件：当前宠物达到 **L5（score ≥ 80）**。
- 目标物种不能等于当前物种。
- 目标为神兽时，必须已解锁神兽。
- 神兽解锁条件：**任意普通物种的 `best_level` 达到 5**（历史上达到过即可）。
- 换宠成功后：
  - 当前物种切换为目标物种；
  - 当前积分重置为 0；
  - 目标物种 `pet_progress` 至少为 L1；
  - 旧物种进度保留；
  - 返回一个「毕业/迎新」结果，前端播放换宠动画。
- 已满级（best_level=5）的物种仍可再次选择，但视觉上标记「已毕业」，不阻止。
- 除换宠外，不提供直接修改宠物物种的入口。

### 7.7 随机点名

- 默认「公平模式」：
  - 排除缺席学生（默认开启）。
  - 按 `last_picked_at` 升序（NULL 最前）排序。
  - 取前 `max(1, ceil(n / 3))` 人作为候选池。
  - 在候选池中随机选 1 人。
  - 若班级人数 > 1 且候选池包含上一次被抽中的学生，则排除该学生后再随机。
  - 更新 `last_picked_at`。
- 可选「纯随机模式」：在全部符合条件的学生中等概率抽取。
- 没有学生或全部缺席：返回 `409 NO_STUDENTS`，前端提示。
- 点名结果写入 `last_picked_at` 即可；P1 再增加点名历史表。

### 7.8 数据与删除

- 删除学生：级联删除其 `pet_progress` 和 `score_events`；前端二次确认。
- 删除班级：级联删除学生、进度、事件；必须输入班级名确认，并提示先导出备份。
- 导入备份：**替换全部数据**；请求必须带 `confirm: "REPLACE"`；导入前自动写一份 `data/backups/pre-import-*.json`；整个导入在一个事务内完成，任一校验失败则全部回滚。
- 积分在换宠时重置；不提供「一键清零全班」P0 入口（P1 可加，必须二次确认）。
- 刷新页面、重启服务、换电脑导入后，所有数据保持一致。

### 7.9 边界情况

| 情况 | 行为 |
|---|---|
| 100 分继续 +1 | 409，提示已满，不写事件 |
| 0 分继续 -1 | 409，提示已到最低，不写事件 |
| 撤销后再次撤销 | 409 `EVENT_ALREADY_UNDONE` |
| 撤销一条之后又有新事件 | 409 `EVENT_NOT_LATEST` |
| 换宠后撤销换宠前的加分 | 409（当前积分已变） |
| 同班学号重复 | 409 `DUPLICATE_STUDENT_NO`；批量导入预览中标注并跳过 |
| 同班同名 | 允许；界面显示学号/座位号辅助区分 |
| 空班级 | 工作台显示空状态和「添加学生」按钮 |
| 全部学生缺席时点名 | 409 `NO_STUDENTS` |
| 导入文件格式错误 | 422，整个导入回滚，原数据不变 |
| 数据库文件损坏/缺失 | 启动时自动建库；损坏时给出明确错误和数据路径，不静默删库 |
| 两个标签页同时操作 | 每次积分是独立事务；撤销用 `score_after` 校验避免覆盖；大屏轮询刷新 |
| 浏览器不支持 CSS 动画 | 静态 SVG 仍正确显示，功能不受影响 |

---

## 8. 功能需求

### F1. 首次启动、登录与设置

**目标**：老师第一次打开就知道要做什么；之后每次打开快速进入课堂。

**流程**：

1. 首次访问任意页面 → 检查 `/api/auth/status`。
2. 若 `needs_setup=true` → 跳转 `/setup`。
3. Setup 页：教师显示名（默认「老师」，可改）、4–6 位数字 PIN、确认 PIN、可勾选「创建示例班级」。
4. 提交后：创建 PIN 哈希、写入默认设置、建立会话、跳转首页。
5. 之后访问：未登录 → `/login`；输入 PIN → 进入首页。
6. 登录页提供数字键盘（触屏友好），也支持键盘输入、Enter 提交。
7. 连续 5 次错误 → 锁定 30 秒（服务端内存计数 + 前端倒计时）。
8. 已登录时访问 `/login` 或 `/setup` → 跳转首页。

**验收**：

- 首次启动 3 分钟内可完成 setup 并加分。
- 错误 PIN 不会创建会话；提示不泄露「PIN 是几位/对不对」以外的信息。
- 刷新后保持登录（7 天 Cookie）。
- 登出后访问工作台跳转登录页。

### F2. 班级管理

- 首页 `/` 展示班级卡片列表。
- 每张卡片：班级名、年级、学生数、平均分、最近使用的班级标记、3 个学生宠物的缩略图（若有人）。
- 新建班级：名称必填（1–30 字），年级可选，颜色从 6 个预设中选一个。
- 编辑：名称、年级、颜色。
- 删除：输入班级名确认；提示先导出。
- 点击卡片进入工作台 `/class/:id`。
- 记住上次进入的班级；下次打开首页时该卡片高亮，但**不自动跳转**（避免误入）。
- 空状态：插画 + 「创建第一个班级」。

**验收**：创建/重命名/删除均生效；删除后学生、事件、进度一并消失；同名班级允许但前端提示。

### F3. 学生管理

- 工作台顶部「添加学生」打开对话框。
- 单个添加字段：
  - 姓名（必填，1–20 字）
  - 学号（可选，≤ 20 字，同班唯一）
  - 座位号（可选，整数 1–99）
  - 宠物（可选，普通物种；默认「随机」）
- 批量导入：
  - 文本域，每行一个学生。
  - 支持格式：`姓名`、`姓名,学号`、`姓名，学号`、`姓名<TAB>学号<TAB>座位号`。
  - 先「预览」：显示将新增、将跳过（学号重复/空行）、格式错误行。
  - 确认后只新增；不覆盖已有学生。
  - 最多一次 200 行。
- 学生卡片点击 → 详情抽屉：
  - 宠物大图、当前积分/等级/阶段、物种、学号、座位号
  - 最近积分事件（P1；P0 至少显示最近一条与撤销入口）
  - 「查看图鉴 / 换宠」按钮
  - 编辑姓名/学号/座位号
  - 删除
- 排序：座位号 → 姓名 → 积分从高到低；选择记忆在 `localStorage`。
- 搜索：姓名或学号，200ms 防抖。
- 缺席开关（P1）：只影响随机点名，不影响积分。

**验收**：同班重复学号被拒绝；批量导入预览准确；排序/搜索即时；刷新后顺序保持。

### F4. 课堂工作台与积分

**定位**：老师最常用的页面，也是默认首页之一（从班级卡片进入）。

**布局**：

- 顶部栏：返回、班级名、学生数、搜索、排序、随机点名、大屏展示、添加学生、更多菜单。
- 主区域：学生卡片网格。
- 底部/顶部：最近一次操作提示条（含「撤销」），6 秒后自动消失。

**学生卡片**：

- 宠物 SVG（默认 96–120px，随卡片宽度缩放）
- 姓名（≥ 16px，加粗）
- 学号/座位号（次要）
- 积分数字（大号衬线数字，≥ 28px）
- 等级徽章（L1–L5）与阶段名
- 进度条（0–100）
- 快捷按钮 `+1` / `-1`
- 心情与瞬时反应由积分/操作驱动
- 卡片有物种色细边或顶部色条，但**不依赖颜色区分状态**

**交互**：

- 点击 `+1`：乐观更新数字和宠物反应 → 调用 API → 用响应校准；失败回滚并提示。
- 点击 `-1`：同上，心情变低；不抖动、不闪红。
- 点击卡片空白处：打开详情抽屉。
- 点击「评分」或长按卡片（P1）：打开原因面板，选择预设原因后执行 ±1。
- 原因预设（P0 至少各 4 个）：
  - 加分：课堂积极、朗读优秀、作业优秀、帮助同学、进步明显
  - 减分：作业未完成、课堂分心、未准备学具、需要改进
- 最近一次撤销：顶部提示条 + 详情抽屉均可触发。
- 键盘（P1）：聚焦卡片后 `+` / `-` 操作。
- 评分进行中按钮禁用 200ms，防止连点重复；但快速连续点击不同学生不受影响。

**验收**：

- 40 人班级滚动流畅；每张卡片宠物都在呼吸/眨眼，但不同步。
- 加分后 100ms 内看到数字变化和 cheer；升级时播放 evolve。
- 撤销后数字回退，提示「已撤销」。
- 100 分继续加分提示友好，不产生事件。
- 刷新后积分、等级、阶段、心情一致。

### F5. 宠物养成与动画

- 每张学生卡片、详情抽屉、图鉴、点名浮层、大屏都使用同一个 `PetSprite` 组件。
- 宠物外观由 `species + level + mood + reaction` 决定，**不读取任何图片文件**。
- 等级变化时播放 `evolve`；初次渲染不播放。
- 加分播放 `cheer`；减分播放 `comfort`。
- 心情由服务端返回的 `mood` 决定；瞬时反应由前端覆盖，结束后回到基础心情。
- 「减少动效」开启时：
  - 停止呼吸、摇尾、眨眼、光环旋转、粒子；
  - 保留表情、数字、颜色、阶段饰品的变化；
  - `evolve` 降级为 200ms 的透明度闪烁或直接切换。
- 同一屏 40–60 只宠物时，只使用 CSS 动画，不跑 `requestAnimationFrame` 循环。
- 每只宠物的眨眼/摇尾相位由其学生 `id` 派生，避免整齐划一。

**验收**：6 种 × 5 阶段全部能正确渲染；无 `<img>`、无 404、无外部资源；减少动效生效；动画不引起明显掉帧。

### F6. 图鉴、换宠与神兽解锁

- 学生详情抽屉中打开「宠物图鉴」。
- 图鉴展示 6 个物种卡片：
  - 物种名、SVG 预览（按 `best_level` 展示形态；未养过显示 L1 轮廓/灰度）
  - `best_level`：L1–L5 小圆点
  - 当前物种标记
  - 神兽未解锁时显示锁与解锁条件
  - 可换宠时显示「换宠」按钮
- 换宠对话框：
  - 说明当前是否满足条件（L5）
  - 选择目标物种
  - 神兽未解锁时禁用并说明「任意普通宠物达到 L5 后解锁」
  - 二次确认：「换宠后当前积分会归零，确定吗？」
  - 成功后播放毕业/迎新动画，积分归零，卡片更新
- 图鉴进度只增不减；撤销积分不会降低图鉴等级。

**验收**：L4 不能换宠；L5 可以；神兽在无普通 L5 时锁定；解锁后可换；换宠后积分 0、新宠物 L1、旧进度保留。

### F7. 随机点名

- 工作台顶部「随机点名」打开全屏浮层。
- 浮层内容：大宠物（随机选中的学生的宠物）、姓名（超大）、班级名、候选人数。
- 抽取过程：
  - 减少动效关闭：0.9 秒滚动/缩放后定格。
  - 减少动效开启：直接显示结果。
- 操作：
  - Space / Enter：再抽一次
  - Esc / 关闭按钮：退出
  - 触屏：大的「再抽一次」按钮
- 焦点进入浮层并锁定；关闭后焦点回到触发按钮。
- 结果通过 `aria-live="polite"` 播报「抽中了 林小满」。
- 公平模式：见 7.7。
- 不显示「已抽过的人」列表（P1 可加）。

**验收**：连续抽取不出现明显连续重复；缺席学生不被抽中；全班缺席时提示；键盘可完成全部操作。

### F8. 大屏展示

- 路由：`/display/:classId`
- 无应用侧栏；全屏铺满。
- 顶部细栏（鼠标移动/触摸时出现，3 秒后淡出）：
  - 班级名、学生数、当前时间（可选）、排序切换、投影增强（P1）、退出
- 主区域：
  - 学生网格，每格：宠物（96–160px，随人数缩放）、姓名（≥ 24px）、积分（≥ 32px）、阶段徽章
  - 默认按座位号排序；可切换积分排序；不显示名次数字
  - 低分不标红、不显示「最后一名」
- 数据刷新：
  - 每 3 秒轮询 `GET /api/classes/{id}/display`
  - 页面隐藏时暂停轮询，恢复时立即拉取
  - 积分变化时数字平滑过渡；等级上升时播放 evolve；不重新挂载整个网格
- 投影适配：
  - 1920×1080：40 人 8 列 × 5 行或 7 列 × 6 行
  - 1366×768：适当减少列数，允许滚动
  - 文字与背景对比度满足 WCAG AA 大字标准
- 键盘：`F` 进入/退出浏览器全屏（可选），`Esc` 退出全屏。
- 断线提示：轮询失败时顶部显示「连接中断，正在重试」，不弹窗。

**验收**：在大屏路由下加分（另一个标签页/另一台同源设备），3 秒内更新；等级上升有动画；页面无操作按钮；8 米可读。

### F9. 设置与数据

- `/settings`：
  - 教师显示名
  - 修改 PIN（旧 PIN + 新 PIN + 确认）
  - 动效：跟随系统 / 减少动效
  - 数据路径展示（只读）
  - 导出 JSON
  - 导入 JSON（替换式，输入 `REPLACE` 确认）
  - 创建示例班级
  - 版本号与构建时间
  - 关于/隐私说明：数据仅在本机，无网络请求
- 导出：
  - 文件名 `petgarden-backup-YYYYMMDD-HHmmss.json`
  - 包含 classes、students、pet_progress、score_events、必要的 settings（不含 PIN 哈希、不含 secret key）
  - `format: "petgarden-backup"`、`version: 1`
- 导入：
  - 校验 format/version/字段类型/外键完整性
  - 文件 ≤ 5MB
  - 导入前写 `data/backups/pre-import-*.json`
  - 成功后前端清空缓存并刷新
- 示例数据：
  - 首次 setup 可勾选创建，或设置页手动创建
  - 1 个班级「三年级二班」，12 名学生
  - 覆盖 5 种普通宠物和 1 只神兽（需先手动解锁或示例中已解锁）
  - 积分覆盖 8、18、25、38、45、58、65、72、80、88、96、100，便于验收所有阶段
  - 至少 1 名学生图鉴中有普通 L5，便于测试神兽解锁

**验收**：导出后清空/换库导入，数据完整恢复；坏文件被拒绝且原数据不变；PIN 修改后旧 PIN 失效；示例班级可重复创建但名称自动加后缀。

### F10. 响应式、离线与错误状态

- 断点：
  - ≥ 1200px：完整侧栏 + 网格
  - 900–1199px：窄侧栏
  - 600–899px：顶部栏 + 抽屉导航
  - < 600px：单列/双列卡片，按钮 ≥ 44px
- 所有页面有 loading skeleton、空状态、错误状态与重试按钮。
- 离线：
  - 构建后不加载任何 CDN、外部字体、外部图标、远程图片。
  - 图标全部内联 SVG。
  - 音效（P1）用 WebAudio 合成，无音频文件。
- 错误文案用中文，避免堆栈暴露；开发模式可在控制台输出详细错误。
- 404 页面：友好的空状态 + 返回首页。

---

## 9. 信息架构与路由

| 路由 | 页面 | 权限 | 说明 |
|---|---|---|---|
| `/setup` | SetupView | 未初始化 | 教师名 + PIN + 可选示例数据 |
| `/login` | LoginView | 未登录 | 数字键盘/PIN 输入 |
| `/` | ClassesView | 已登录 | 班级卡片列表 |
| `/class/:id` | ClassView | 已登录 | 课堂工作台（核心页面） |
| `/class/:id/collection/:studentId` | CollectionView 或抽屉 | 已登录 | 学生图鉴/换宠；也可用抽屉实现 |
| `/display/:id` | DisplayView | 已登录 | 投影大屏，无应用外壳 |
| `/settings` | SettingsView | 已登录 | 设置与数据 |
| `/:pathMatch(.*)*` | NotFoundView | 任意 | 404 |

**导航结构**：

- 桌面侧栏：Logo、班级列表、设置、登出。
- 移动端：顶栏 + 抽屉。
- 大屏路由完全隐藏侧栏和底栏。

**状态保留**：

- 上次班级（`localStorage`）
- 排序方式（按班级存储）
- 减少动效（服务端 settings + 本地缓存，服务端为准）
- 不把 PIN、会话 token 写入 `localStorage`

---

## 10. 视觉与交互设计

### 10.1 设计方向

**关键词**：温暖的教室、纸感、手作、克制的活泼、清晰的远距离阅读。

参考气质：一间有木质书架、绿植、手写标签和动物角的小学教室；不是企业后台，也不是儿童游戏大厅。

**三个视觉支柱**：

1. **纸与木的底色**：米白纸面、深墨绿文字、陶土与蜂蜜色点缀，避免纯白 + 蓝色渐变。
2. **手作感而非卡通堆砌**：1px 描边、轻微不规则、圆角但不糖果化；宠物是唯一的高饱和焦点。
3. **投影优先的层级**：大数字、大名字、大宠物；控制按钮退到次要层级。

### 10.2 色彩 Token

```css
:root {
  /* 底色 */
  --paper: #FAF6EC;          /* 页面背景 */
  --surface: #FFFDF7;        /* 卡片/面板 */
  --surface-sunken: #F1E9DA; /* 次级背景 */
  --line: #DED3BF;           /* 分隔线/描边 */
  --line-strong: #C9BBA3;

  /* 文字 */
  --ink: #252A26;            /* 主文字 */
  --ink-soft: #5F665D;       /* 次要文字 */
  --ink-faint: #8A8F86;      /* 辅助说明 */

  /* 主色 */
  --moss: #4F6F52;           /* 主按钮/选中 */
  --moss-deep: #3E5A42;
  --moss-soft: #E3EBDD;

  /* 强调色（大面积/图标/大字；小字需校验对比度） */
  --clay: #B85C3E;
  --honey: #D99B2B;
  --sky: #6BA6BC;
  --rose: #B45F72;
  --plum: #7B5E7B;

  /* 状态 */
  --success: #3F7A5A;
  --warning: #A66A1F;
  --danger: #A94438;
  --focus: #2F6FB3;

  /* 宠物物种色（前端 visuals.ts 中同步） */
  --pet-cat: #D98A4F;
  --pet-dog: #9A6236;
  --pet-rabbit: #D88FA4;
  --pet-panda: #3B413C;
  --pet-fox: #E18A4F;
  --pet-dragon: #2E6E68;

  /* 形状 */
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-pill: 999px;

  /* 阴影 */
  --shadow-card: 0 8px 24px rgba(63, 52, 35, 0.07);
  --shadow-pop: 0 16px 48px rgba(63, 52, 35, 0.16);

  /* 字体 */
  --font-ui: "Microsoft YaHei UI", "PingFang SC", "Noto Sans SC",
             "Source Han Sans SC", system-ui, sans-serif;
  --font-display: "Georgia", "Songti SC", "SimSun", serif;
}
```

**使用规则**：

- 正文和按钮文字优先用 `--ink` / `--moss-deep` / `--ink-soft`；强调色只用于大面积、图标或 ≥ 24px 的粗体。
- 所有文字/背景组合必须实测对比度：正文 ≥ 4.5:1，大字 ≥ 3:1。
- 低分状态不使用 `--danger` 大面积铺色；用宠物的耳朵、表情和文案表达。
- 不允许紫色/蓝色渐变、玻璃拟态、霓虹发光、纯白卡片 + 蓝按钮的 SaaS 模板感。

### 10.3 字体

- UI：系统中文字体（微软雅黑/PingFang/Noto Sans SC），保证离线与 Windows 兼容。
- 展示数字与班级名：`--font-display`（Georgia / 宋体），形成「教室标签」的温度；数字使用 `font-variant-numeric: tabular-nums`。
- 字号阶梯：12 / 14 / 16 / 18 / 22 / 28 / 36 / 48 / 64。
- 字重：正文 400，姓名/标题 600–700；避免 300 细字（投影看不清）。
- 行高：正文 1.6；大数字 1.0；标题 1.2。

### 10.4 布局与组件

**应用外壳**：

- 桌面：左侧 232px 侧栏 + 主区域；侧栏背景 `--surface-sunken`，右侧 1px `--line`。
- 移动：顶栏 56px + 抽屉。

**班级卡片**：

- 24px 圆角，纸面底，1px 描边，轻阴影。
- 顶部 4px 班级色条；班级名用 display 字体；底部显示学生数和平均分。
- 右下角可叠 3 个 40px 宠物头像（SVG），形成「这个班有谁」的直觉。

**学生卡片**：

- 默认 168–220px 宽，最小 160px；24px 圆角。
- 顶部/左侧 3px 物种色条；背景 `--surface`。
- 宠物区域 120–140px 高，浅色圆形/拱形背景（`--surface-sunken` + 物种色 8% 叠加）。
- 姓名 16–18px/700；学号 12px/`--ink-faint`。
- 积分用 display 字体 32–40px；旁边小字「分」或 `/100`。
- 进度条 6px，圆角，moss 色；数字始终可见。
- 底部 `-1` 和 `+1`：44px 高，`-1` 为描边按钮，`+1` 为 moss 实心；点击区域不重叠。
- 升级瞬间卡片边框短暂变亮，播放 evolve；不使用全屏闪烁。

**按钮**：

- 主：moss 底、纸白字；次：透明底 + 1px 描边；危险：仅删除类操作，陶土红描边/实心。
- 圆角 12px（普通）/ pill（标签）；高度 40–44px。
- hover 上浮 1px；active 下压 1px；disabled 40% 透明。
- 焦点环 2px `--focus` + 2px offset。

**对话框/抽屉**：

- 桌面用居中对话框（max-width 560px）或右侧抽屉（详情 420px）。
- 移动用底部 sheet。
- 遮罩 `rgba(37,42,38,.38)` + 4px 模糊（可选，低配设备可关闭）。
- 关闭按钮 44px；Esc 关闭；点击遮罩关闭（表单未保存时二次确认）。

**Toast**：

- 底部居中，纸面底 + 深色文字 + 左侧状态点；圆角 14px。
- 成功/信息 3 秒；带撤销 6 秒。
- 最多同时 3 条；不遮挡底部操作按钮。

**空状态**：

- 简单内联 SVG（一盆植物、一个空宠物窝），配一句温暖文案和一个主按钮。
- 不使用大型位图插画。

**图标**：

- 全部内联 SVG，1.5px 描边、圆角线帽，尺寸 20/24px。
- 不引入图标库也能完成；若引入，必须打包本地、不可 CDN。

### 10.5 动效

| 场景 | 时长 | 曲线/说明 |
|---|---|---|
| 按钮 hover/active | 120–160ms | `cubic-bezier(.2,.8,.2,1)` |
| 对话框进入 | 180ms | 透明度 + 8px 上移 |
| 卡片出现 | 240ms stagger 20ms | 首次加载可用 |
| 积分数字变化 | 220ms | 数字滚动或淡入；不要弹跳 |
| 宠物 cheer | 900ms | 见 11.5 |
| 宠物 comfort | 700ms | 缓慢下沉，不抖动 |
| 宠物 evolve | 1100ms | 光环 + 缩放 + 粒子 |
| 点名定格 | 900ms | 快速滚动 → 减速 → 放大定格 |
| Toast | 200ms in / 160ms out | |

- 所有动效必须支持 `prefers-reduced-motion: reduce`。
- 不使用持续闪烁、频闪、超过 3 次的循环强调。
- 动画只改 `transform` / `opacity`；不动画化 `width/height/top/left`。

### 10.6 投影模式

- 默认浅色，不跟随系统深色（教室环境通常明亮）。
- 学生姓名 ≥ 24px，积分 ≥ 32px，宠物 ≥ 96px。
- 对比度按大字标准 ≥ 3:1，正文 ≥ 4.5:1。
- 网格不显示名次、不显示红/绿排名色。
- P1「投影增强」：姓名 +4px、积分 +8px、宠物 +16px，背景更接近纯白，描边加深。

### 10.7 文案语气

| 场景 | 文案 |
|---|---|
| 加分到 100 | 已经满 100 分啦，可以准备换一位新伙伴了。 |
| 0 分继续减 | 现在是 0 分，先给一个鼓励吧。 |
| 撤销成功 | 已撤销：林小满 +1 |
| 空班级 | 这个班级还没有学生，先请第一位小伙伴进来吧。 |
| 点名标题 | 今天会是谁呢？ |
| 换宠成功 | 满级毕业！新伙伴已经入住。 |
| 神兽锁定 | 任意一只普通宠物达到 L5，就能解锁神兽。 |
| 导入确认 | 导入会替换当前全部数据，建议先导出备份。 |
| 删除班级 | 输入班级名以确认删除，此操作不可恢复。 |

**语气规则**：短句、具体、温和；不用「惩罚」「倒数」「落后」；感叹号每屏最多 1 个；不卖萌过度。

### 10.8 反模式（禁止）

- 企业蓝白渐变、玻璃卡片、发光按钮、通用 SaaS 仪表盘
- 用 emoji 当宠物（不同系统渲染不一致，且不够可控）
- 满屏彩色渐变、贴纸、闪光
- 公开排行榜、名次、红绿分数、倒计时压力
- 低分宠物流泪、发抖、变灰、被打叉
- 自动播放音效
- 把重要操作藏在 hover 里
- 依赖颜色区分状态而没有文字/数字
- 使用外部 CDN 字体/图片/图标

---

## 11. 宠物视觉与动画系统

### 11.1 技术结论

**宠物用内联 SVG 程序化绘制，CSS 关键帧驱动，不加载任何图片。**

理由：

- 动态：呼吸、眨眼、摇尾、耳朵、表情、光环、粒子都可以实时变化。
- 清晰：矢量在投影和任意 DPI 下都锐利。
- 离线：无图片文件、无网络请求、无版权素材风险。
- 一致：同一套描边、色彩、几何语言，6 种宠物不会出现风格漂移。
- 可维护：颜色、阶段饰品、表情都是代码配置，改规则即可全局生效。
- 性能：40–60 个实例只用 CSS transform/opacity，避免 Canvas 每帧重绘。

不采用 Canvas 的原因：这个规模不需要逐帧循环；SVG 更易做可访问性、响应式、主题化和组件复用。若未来单屏超过 150 只或需要复杂骨骼动画，再换 Canvas/sprite-sheet，`PetSprite` 接口保持不变。

### 11.2 组件架构

```
frontend/src/pets/
├─ types.ts               # SpeciesId, PetLevel, PetMood, PetReaction
├─ visuals.ts             # 物种配色、体型、耳型、尾巴类型、阶段饰品配置
├─ PetSprite.vue          # 对外唯一入口：species/level/mood/reaction/seed/size
├─ PetFace.vue            # 共享眼睛/嘴/腮红/眉，按 mood 切换
├─ StageAccessories.vue   # 围巾/徽章/光环/皇冠/翅膀
├─ CatPet.vue
├─ DogPet.vue
├─ RabbitPet.vue
├─ PandaPet.vue
├─ FoxPet.vue
├─ DragonPet.vue
├─ usePetMotion.ts        # 由 seed 生成眨眼/摇尾 jitter 的 CSS 变量
└─ pet.css                # 所有宠物 keyframes 与 reduced-motion 规则
```

**对外 props**：

```ts
interface PetSpriteProps {
  species: 'cat' | 'dog' | 'rabbit' | 'panda' | 'fox' | 'dragon'
  level: 1 | 2 | 3 | 4 | 5
  mood: 'happy' | 'neutral' | 'sad'
  reaction?: { type: 'cheer' | 'comfort' | 'evolve'; nonce: number } | null
  seed: number | string      // 学生 id；用于相位抖动
  size?: number              // CSS px，默认 120
  label?: string             // 无障碍标签；默认由物种/等级/心情生成
  decorative?: boolean       // 卡片内可设为 true，外层已有文字
}
```

**约束**：

- 组件内部不得使用 `<img>`、`<image>`、base64 图片、外部 URL、emoji。
- 所有颜色来自 `visuals.ts` + CSS 变量，不写死到每个物种组件里。
- `PetSprite` 是纯展示组件，不发请求、不读 store。
- 父组件负责把服务端返回的 `level`/`mood` 传进来；组件不根据 score 自行计算规则。
- 同一页面所有宠物共用一套 `<defs>` 可选优化，但不得依赖全局 ID 冲突。

### 11.3 SVG 几何规范

- 统一 `viewBox="0 0 200 200"`，`width/height` 由 `size` 控制，`overflow: visible`。
- 地面阴影：`<ellipse cx="100" cy="178" rx="52" ry="8" fill="#252A26" opacity=".08" />`。
- 身体中心约 `(100, 140)`，头中心约 `(100, 92)`；耳朵、尾巴可超出。
- 描边：主轮廓 `#252A26`，宽度 2–2.5，`stroke-linejoin="round"`、`stroke-linecap="round"`。
- 每种宠物 3–4 个主色：body、belly、accent、inner ear/cheek。
- 不使用 SVG `filter`（模糊/投影）、渐变网格、foreignObject；避免 40 个实例时 GPU 压力。
- 高光/阴影用低透明度纯色形状，不用滤镜。
- 体型随等级缩放：L1 `0.88`、L2 `0.94`、L3 `1.0`、L4 `1.05`、L5 `1.12`；头身比随等级略微降低（L1 头更大）。
- 阶段饰品必须改变剪影，保证 80px 大小也能看出来：
  - L2：围巾/项圈（色块 + 结）
  - L3：胸前徽章/小背包（圆形或方形）
  - L4：背后光环（虚线圆环，缓慢旋转）+ 额头纹样
  - L5：皇冠/角饰 + 更亮的光环 + 粒子环（青龙额外展开翅膀）

### 11.4 物种剪影

| 物种 | 必须可辨认的特征 | 尾巴 | 耳朵 |
|---|---|---|---|
| cat | 三角耳、胡须、卷尾 | 细长卷曲，端点圆 | 三角，内耳粉色 |
| dog | 垂耳、突出吻部、舌头 | 上翘摇摆 | 椭圆下垂 |
| rabbit | 长耳、圆尾、粉内耳 | 小圆球 | 长椭圆，可轻微摆动 |
| panda | 圆耳、黑眼斑、竹叶 | 小圆尾 | 圆形黑耳 |
| fox | 尖耳、奶油色吻部、大尾巴 | 蓬松大尾，尖端浅色 | 尖三角，内耳深色 |
| dragon | 龙角、龙须、翅膀、盘尾 | 粗长盘曲，带鳍 | 角 + 鳍状耳 |

**避免**：

- 6 种宠物只是换颜色、剪影相同。必须保留上表的轮廓差异。
- 过度拟人化（穿校服、站立、人手）。保持动物比例，饰品只做点缀。
- 眼睛过大且无高光，产生恐怖谷。

### 11.5 表情与动画清单

| 名称 | 目标元素 | 时长/循环 | 关键帧要点 |
|---|---|---|---|
| `pet-breathe` | 身体组 | 3.2s infinite | `scale(1,1) → scale(1.02,.985) → scale(1,1)` |
| `pet-bob` | 头部组 | 2.8s infinite | `translateY(0 → -2px → 0)` |
| `pet-sway` | 尾巴组 | 2.4–3.4s infinite | `rotate(-4deg → 5deg → -4deg)`；开心时 1.4s |
| `pet-ear` | 耳朵组 | 4.6s infinite | `rotate(-2deg → 2deg → -2deg)`，错峰 |
| `pet-blink` | 眼睛组 | 4–7s infinite | 0–92% 正常；94–96% `scaleY(.08)`；100% 恢复 |
| `pet-cheer` | 根组 + 粒子 | 900ms once | 下蹲 → 上跳 8px + 放大 1.08 → 回落 |
| `pet-comfort` | 根组 + 耳朵 | 700ms once | 整体下沉 2px、耳朵下垂、头部倾斜 4deg |
| `pet-evolve` | 根组 + 光环 | 1100ms once | 光环从小扩大到 1.6 倍并淡出；宠物 0.92→1.12→1；阶段徽章弹入 |
| `pet-aura-spin` | L4/L5 光环 | 24s linear infinite | 旋转 360°，虚线 |
| `pet-particle` | L5 粒子 | 3s infinite | 8 个粒子沿环缓慢上浮/淡出，错峰 |

**相位抖动**：

```ts
function hash(seed: number | string) {
  const s = String(seed)
  let h = 2166136261
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

const h = hash(seed)
const style = {
  '--blink-duration': `${4 + (h % 30) / 10}s`,   // 4.0–6.9s
  '--blink-delay': `-${(h % 50) / 10}s`,         // 负延迟，错峰
  '--sway-duration': `${2.2 + (h % 12) / 10}s`,
  '--sway-delay': `-${(h % 20) / 10}s`,
}
```

**实现要点**：

- 用 `transform-box: fill-box` + `transform-origin` 精确控制耳朵/尾巴/眼睛的旋转中心；对尾巴等需要相对于整个 viewBox 定位的组，用 `transform-box: view-box`。
- 眼睛闪烁用 `scaleY` 作用于整个眼睛组（含高光），不要单独缩放瞳孔。
- cheer/comfort/evolve 由 `reaction.nonce` 变化触发：`watch` 到 nonce 改变 → 添加 class → `setTimeout` 移除。不要用 `setInterval` 轮询。
- 初次渲染绝不播放 evolve；只在 `level` 从旧值变为更高值时播放。
- 减少动效时：`animation: none`；保留表情/饰品/数字；evolve 可直接切换阶段。

### 11.6 可访问性

- 宠物 SVG 默认 `role="img"` + `aria-label`，例如「小猫，第 3 阶段，心情很好」。
- 卡片中若姓名/积分已由文本提供，宠物可设 `aria-hidden="true"`，避免重复播报。
- 动画不传递唯一信息：分数、等级、阶段都有文字。
- 减少动效：
  - 尊重 `prefers-reduced-motion: reduce`；
  - 设置页「减少动效」写入 `<html data-motion="reduced">`；
  - 两种方式都关闭循环动画与粒子。
- 不自动播放声音。

### 11.7 性能预算

- 单只宠物 DOM 节点 ≤ 70。
- 单屏 ≤ 60 只；40 只为常态。
- 只动画 `transform` / `opacity`；不给 SVG 加 `filter: drop-shadow`。
- 粒子每只 ≤ 8 个，且仅 L5/evolve 时出现。
- 不在滚动/轮询时重新创建 SVG；用 `v-for :key=student.id` 复用组件。
- 大屏轮询只更新数据，不重新挂载整个列表。
- 若性能不足，优先降级：关闭 L5 粒子 → 关闭光环旋转 → 关闭耳朵/尾巴动画，保留眨眼与表情。

### 11.8 参考原型

`reference/pet-sprite-demo.html` 是一个零依赖的单文件原型，演示：

- 6 种剪影：小猫、小狗、小兔、熊猫、小狐、青龙
- 5 个阶段的体型与饰品
- 3 种心情
- 呼吸、眨眼、摇尾、光环
- 加分 cheer、减分 comfort、升级 evolve
- 40 只宠物的网格预览
- 减少动效开关
- URL 参数直接预览：`?species=dragon&score=90&mood=happy`

它**不是最终代码**，只用于验证技术路线和动画手感。实现时应按本文件的组件架构重写，而不是直接把原型 HTML 塞进 Vue。

---

## 12. 技术架构

### 12.1 技术栈

| 层 | 选择 | 说明 |
|---|---|---|
| Python 运行时 | Python 3.12 | 由 uv 安装/管理 |
| 环境与依赖 | uv | `.venv` 在项目内；`pyproject.toml` + `uv.lock` |
| Web 框架 | FastAPI | 同步路由即可；自带 OpenAPI |
| ORM | SQLAlchemy 2.0（同步） | 类型化 `Mapped` 模型 |
| 数据校验 | Pydantic v2 | 请求/响应 schema |
| 数据库 | SQLite | WAL、外键、单文件 |
| 认证 | PIN + 签名 HttpOnly Cookie | `hashlib.scrypt` + `itsdangerous` |
| 前端 | Vue 3 + TypeScript + Vite | Strict TS |
| 路由 | Vue Router 4 | History 模式 |
| 状态 | Pinia | auth / classes / roster / settings |
| 样式 | 原生 CSS + design tokens | 不引入 UI 框架 |
| 宠物 | 内联 SVG + CSS 动画 | 无图片资源 |
| 后端测试 | pytest + httpx TestClient | 内存 SQLite |
| 前端测试 | Vitest + @vue/test-utils | 纯函数 + 组件冒烟 |
| 代码质量 | ruff + vue-tsc + ESLint（可选） | |

**明确不引入**：大型 UI 组件库、Tailwind、Axios、Lodash、图标库、ORM 迁移框架、Celery、Redis、Docker。

### 12.2 目录结构

```
PetGarden/
├─ pyproject.toml
├─ uv.lock
├─ .python-version              # 3.12
├─ .gitignore
├─ README.md
├─ REQUIREMENTS.md
├─ AGENT_PROMPT.md
├─ start.bat                    # 生产：构建前端 + 启动
├─ dev.bat                      # 开发：后端 + Vite 两个窗口
├─ src/
│  └─ petgarden/
│     ├─ __init__.py
│     ├─ __main__.py            # CLI: serve / seed / reset-pin
│     ├─ main.py                # create_app()
│     ├─ config.py              # 路径/端口/环境变量
│     ├─ db.py                  # engine/session/init_db
│     ├─ models.py              # SQLAlchemy 模型
│     ├─ schemas.py             # Pydantic 模型
│     ├─ security.py            # PIN 哈希、Cookie 签名、限流
│     ├─ deps.py                # get_db / require_teacher
│     ├─ errors.py              # AppError + 统一错误响应
│     ├─ domain/
│     │  ├─ pets.py             # 物种目录、等级/阶段/心情、解锁规则
│     │  ├─ scoring.py          # 积分计算纯函数
│     │  └─ rollcall.py         # 候选池/公平抽取纯函数
│     ├─ services/
│     │  ├─ roster.py           # 学生 CRUD、批量导入
│     │  ├─ scoring.py          # apply_score / undo_event
│     │  ├─ pet_progress.py     # 同步进度、换宠
│     │  └─ backup.py           # export/import
│     ├─ api/
│     │  ├─ auth.py
│     │  ├─ classes.py
│     │  ├─ students.py
│     │  ├─ scoring.py
│     │  ├─ pets.py
│     │  ├─ rollcall.py
│     │  ├─ data.py
│     │  └─ settings.py
│     ├─ seed.py                # 示例数据
│     └─ static.py              # 挂载 frontend/dist + SPA fallback
├─ tests/
│  ├─ conftest.py
│  ├─ test_domain_scoring.py
│  ├─ test_domain_pets.py
│  ├─ test_domain_rollcall.py
│  ├─ test_api_auth.py
│  ├─ test_api_roster.py
│  ├─ test_api_scoring.py
│  ├─ test_api_pets.py
│  └─ test_api_backup.py
├─ frontend/
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  ├─ index.html
│  └─ src/
│     ├─ main.ts
│     ├─ App.vue
│     ├─ router.ts
│     ├─ api/
│     │  ├─ client.ts           # fetch 封装、错误映射
│     │  └─ types.ts
│     ├─ stores/
│     │  ├─ auth.ts
│     │  ├─ classes.ts
│     │  └─ roster.ts
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
│     │  └─ pets/ ...           # 见 11.2
│     ├─ composables/
│     │  ├─ useScoring.ts       # 乐观更新/回滚/撤销
│     │  ├─ usePolling.ts       # 大屏轮询/页面隐藏暂停
│     │  └─ useReducedMotion.ts
│     ├─ styles/
│     │  ├─ tokens.css
│     │  ├─ base.css
│     │  └─ components.css
│     └─ utils/
│        ├─ format.ts
│        └─ constants.ts
├─ data/                        # 运行时生成，gitignore
│  ├─ petgarden.db
│  ├─ secret.key
│  └─ backups/
└─ reference/
   └─ pet-sprite-demo.html
```

### 12.3 uv 与环境

**要求**：

- `uv` 负责 Python 版本、虚拟环境、依赖锁定。
- `.venv` 必须在项目根目录（`PetGarden/.venv`），不创建全局环境。
- `pyproject.toml` 声明 `requires-python = ">=3.12"`，`[project.scripts] petgarden = "petgarden.__main__:main"`。
- 提交 `uv.lock`；`.venv/`、`__pycache__/`、`*.pyc` 加入 `.gitignore`。
- 使用 `uv run` 执行所有 Python 命令，不要求用户手动激活。

**初始化命令**（实现 Agent 执行）：

```powershell
cd C:\Users\段大磊\Desktop\PetGarden
uv python install 3.12
uv python pin 3.12
uv init --package --name petgarden .
uv add fastapi "uvicorn[standard]" sqlalchemy pydantic-settings itsdangerous
uv add --dev pytest httpx ruff
uv sync
```

如果 `uv init --package` 生成的目录与 12.2 冲突，以 12.2 为准手工调整；关键是 `pyproject.toml`、`src/petgarden/`、`[project.scripts]` 和 `uv.lock` 都存在。

**常用命令**：

```powershell
uv sync                                   # 创建/同步 .venv
uv run petgarden serve                    # 生产启动（默认 127.0.0.1:8000）
uv run petgarden seed --demo              # 创建示例班级
uv run petgarden reset-pin                # 忘记 PIN 时重置（需本机操作）
uv run uvicorn petgarden.main:app --reload --port 8000   # 后端热重载
uv run pytest -q                          # 测试
uv run ruff check .                       # 静态检查
uv run ruff format --check .              # 格式检查（可选）
```

**Python 依赖**：

```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
pydantic-settings
itsdangerous
# dev
pytest
httpx
ruff
```

不引入 Alembic。首版用 `Base.metadata.create_all()` + 幂等 seed；表结构版本写入 `settings.schema_version`。如果未来需要迁移，再单独引入。

### 12.4 SQLite 配置

- 数据目录：`<项目根>/data/`，启动时自动创建。
- 数据库文件：`data/petgarden.db`。
- 连接串：`sqlite:///.../data/petgarden.db`（绝对路径由代码计算，不依赖启动目录）。
- 连接参数：`check_same_thread=False`。
- 每个连接执行：
  ```sql
  PRAGMA foreign_keys = ON;
  PRAGMA journal_mode = WAL;
  PRAGMA synchronous = NORMAL;
  PRAGMA busy_timeout = 5000;
  ```
- 时间统一存 UTC ISO8601 字符串（`2026-10-25T08:30:00Z`），前端转本地时区显示。
- 事务：每个请求一个 Session；成功 `commit`，异常 `rollback`。积分/撤销/换宠/导入必须在单事务内完成。
- 启动时若数据库不存在 → 建表 + 写入默认 settings + 标记 `needs_setup=true`。
- 并发：单教师、低写入量；WAL + busy_timeout 足够。不做连接池调优。

### 12.5 后端分层

```
HTTP 路由（api/）
  ├─ 解析参数、鉴权
  ├─ 调用 service / domain
  ├─ 捕获 AppError → 统一错误 JSON
  └─ commit / rollback
        ↓
服务层（services/）
  ├─ 事务内的业务编排
  ├─ 查询/写入 ORM
  └─ 调用纯函数规则
        ↓
领域层（domain/）
  ├─ 无数据库、无 IO、无 FastAPI
  ├─ 等级/阶段/心情/解锁/候选池
  └─ 100% 可单测
```

**规则**：

- 路由不写业务规则。
- 领域纯函数是等级、心情、换宠、点名规则的唯一来源。
- 服务层不返回 ORM 对象给路由之外；路由用 Pydantic schema 序列化。
- 统一错误类型 `AppError(code, message, status_code)`，全局异常处理器输出 `{"error":{"code","message"}}`。
- 禁止在响应中泄露堆栈、SQL、文件绝对路径（错误日志除外）。

### 12.6 前端结构

- Vue 3 `<script setup lang="ts">`，TypeScript strict。
- Pinia stores 只存跨页面状态；页面局部状态留在组件。
- API 客户端用原生 `fetch`，统一：
  - `credentials: 'same-origin'`
  - JSON 解析
  - 401 → 清 auth store → 跳转 `/login?next=...`
  - 错误码 → 中文文案映射
- 不在 `localStorage` 存会话 token/PIN；只存 UI 偏好（排序、上次班级）。
- 路由守卫：
  - 启动时请求 `/api/auth/status`；
  - `needs_setup` → `/setup`；
  - 未登录且访问受保护页 → `/login`；
  - 已登录访问 `/login`/`/setup` → `/`。
- 乐观更新：
  - 点击 ±1 立即改本地分数/心情；
  - 请求成功用服务端响应校准（等级、阶段、心情、事件 id）；
  - 失败回滚并 toast；
  - 同一学生请求未返回时禁用该学生按钮 200ms。
- 大屏轮询：
  - `usePolling` 支持间隔、页面隐藏暂停、失败退避（3s → 5s → 10s，恢复后重置）。
  - 只更新数据，不重新创建组件。
- CSS：全局 tokens/base + 组件 scoped；不使用 `!important`（reduced-motion 规则除外）。

### 12.7 构建与静态服务

**开发**：

```powershell
# 终端 1
uv run uvicorn petgarden.main:app --reload --port 8000
# 终端 2
cd frontend
npm install
npm run dev
```

- Vite 端口 5173，代理 `/api` → `http://127.0.0.1:8000`。
- 开发时后端不需要 CORS；Vite 代理保持同源。
- 不要把 CORS 设为 `allow_origins=["*"]`。

**生产**：

```powershell
cd frontend
npm run build          # 输出 frontend/dist
cd ..
uv run petgarden serve # FastAPI 同时提供 API 和 dist
```

- FastAPI 挂载 `frontend/dist/assets` 为静态资源。
- 非 `/api`、非 `/assets` 的 GET 请求返回 `frontend/dist/index.html`（SPA fallback）。
- `/api/*` 未匹配返回 JSON 404，不返回 HTML。
- 若 `frontend/dist` 不存在：返回一个清晰的 HTML 提示「请先执行 npm run build」，不要 500。

**start.bat**：

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

**dev.bat**：

```bat
@echo off
cd /d "%~dp0"
start "PetGarden API" cmd /k "uv run uvicorn petgarden.main:app --reload --port 8000"
start "PetGarden UI" cmd /k "cd frontend && npm run dev"
timeout /t 2 >nul
start "" http://127.0.0.1:5173
```

- 生产默认只绑定 `127.0.0.1`（本机）。
- 局域网访问需显式 `--host 0.0.0.0`，README 中说明风险：同网段设备可访问，PIN 是唯一保护。

### 12.8 认证与安全实现

**PIN**：

- 4–6 位数字，仅数字。
- 存储：`hashlib.scrypt(pin, salt=16字节随机, n=2**14, r=8, p=1, dklen=32)`；Base64 存 `pin_salt` / `pin_hash`。
- 校验用 `hmac.compare_digest`。
- 不在日志、响应、导出中出现 PIN 或哈希。

**会话**：

- `itsdangerous.URLSafeTimedSerializer` 签名 Cookie，内容 `{"v":1}`。
- Cookie 名：`petgarden_session`。
- 属性：`HttpOnly`、`SameSite=Lax`、`Path=/`、`Max-Age=604800`（7 天）；本地 HTTP 下 `Secure=False`，README 说明若用 HTTPS 应开启。
- 签名密钥：首次启动生成 `data/secret.key`（32 字节 URL-safe），文件权限尽量收紧；加入 `.gitignore`。
- 登出：删除 Cookie。
- 失效/篡改 Cookie → 401，前端跳登录。

**限流**：

- 登录失败：同一进程内，5 次/5 分钟（按客户端 IP）；成功后清零。
- 超限返回 429 `RATE_LIMITED`，前端显示倒计时。
- 这是本地应用，不引入 Redis；进程重启后计数清空可接受。

**同源与 CSRF**：

- 生产同源，不配置 CORS。
- 所有写操作使用 JSON `Content-Type: application/json`。
- 若请求带 `Origin` 且不等于当前 Host（开发时允许 `http://127.0.0.1:5173` / `http://localhost:5173`），拒绝写操作。
- 不使用 `allow_origins=["*"]`。

**其他**：

- 导入文件 ≤ 5MB；仅解析 JSON；不执行任何代码。
- 所有用户输入在 Vue 模板中转义；禁止 `v-html` 渲染姓名/原因/班级名。
- 错误响应不包含绝对路径和堆栈；服务端日志可记录。
- 导出文件含学生姓名，设置页提示「请妥善保管」。
- 运行时不发任何外部网络请求（包括字体、图标、telemetry）。

### 12.9 依赖与离线

- 首次安装需要网络：`uv sync`、`npm install`。
- 构建完成后，运行时不访问网络。
- 不使用 Google Fonts、cdnjs、jsDelivr、unpkg、远程图片。
- 图标全部内联 SVG。
- 若需要音效（P1），用 WebAudio 振荡器合成，不添加 mp3。

---

## 13. 数据模型

### 13.1 表结构

```sql
CREATE TABLE settings (
  key        TEXT PRIMARY KEY,
  value      TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE classes (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  grade      TEXT,
  color      TEXT NOT NULL DEFAULT 'moss',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE students (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  class_id       INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  name           TEXT NOT NULL,
  student_no     TEXT,
  seat_no        INTEGER,
  score          INTEGER NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
  species        TEXT NOT NULL CHECK (species IN ('cat','dog','rabbit','panda','fox','dragon')),
  is_present     INTEGER NOT NULL DEFAULT 1 CHECK (is_present IN (0,1)),
  last_picked_at TEXT,
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL
);

CREATE INDEX idx_students_class_score ON students(class_id, score);
CREATE INDEX idx_students_class_seat  ON students(class_id, seat_no);
CREATE UNIQUE INDEX uq_students_class_no
  ON students(class_id, student_no)
  WHERE student_no IS NOT NULL AND student_no <> '';

CREATE TABLE pet_progress (
  student_id      INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  species         TEXT NOT NULL CHECK (species IN ('cat','dog','rabbit','panda','fox','dragon')),
  best_level      INTEGER NOT NULL DEFAULT 1 CHECK (best_level BETWEEN 1 AND 5),
  first_reached_at TEXT NOT NULL,
  last_reached_at  TEXT NOT NULL,
  PRIMARY KEY (student_id, species)
);

CREATE TABLE score_events (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  class_id     INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  delta        INTEGER NOT NULL CHECK (delta BETWEEN -5 AND 5 AND delta <> 0),
  score_before INTEGER NOT NULL CHECK (score_before BETWEEN 0 AND 100),
  score_after  INTEGER NOT NULL CHECK (score_after BETWEEN 0 AND 100),
  reason       TEXT,
  created_at   TEXT NOT NULL,
  undone_at    TEXT
);

CREATE INDEX idx_events_class_id   ON score_events(class_id, id DESC);
CREATE INDEX idx_events_student_id ON score_events(student_id, id DESC);
```

### 13.2 settings 键

| key | 默认值 | 说明 |
|---|---|---|
| `schema_version` | `1` | 数据版本 |
| `teacher_name` | `老师` | 显示名 |
| `pin_salt` | — | Base64 盐 |
| `pin_hash` | — | Base64 scrypt 哈希 |
| `motion_pref` | `system` | `system` / `reduced` |
| `display_sort` | `seat` | `seat` / `score` |
| `created_at` | 当前 UTC | 首次初始化时间 |

- 教师姓名/PIN 虽然只在一条工作区使用，也放 settings，避免多一张表。
- `secret.key` 不放数据库，避免导出备份时泄露会话密钥。

### 13.3 关系

```
classes 1 ── n students 1 ── n pet_progress
                     └──── n score_events
classes 1 ── n score_events   (冗余 class_id，便于按班级撤销/查询)
```

- `students.species` 只存当前物种。
- 等级、阶段、心情、是否可换宠、神兽是否解锁均为派生值，不落库。
- `best_level` 是历史最高，不随撤销/换宠下降。
- 当前物种的 `pet_progress` 行必须在创建学生/加分/换宠时保证存在。

### 13.4 派生字段（API 返回时计算）

每个学生响应包含：

- `level`：由 score 计算
- `stage`：阶段名
- `mood`：由 score 计算
- `score_percent`：0–100
- `can_switch_pet`：level === 5
- `best_level`：当前物种的历史最高
- `divine_unlocked`：班级/学生图鉴中任意普通物种 best_level === 5

后端返回这些字段，前端不重复实现规则；前端只保留纯展示用的工具函数（如颜色、粒子位置）。

### 13.5 示例数据

`uv run petgarden seed --demo` 或 setup 勾选：

- 班级：三年级二班
- 12 名学生，学号 01–12，座位 1–12
- 物种覆盖 cat/dog/rabbit/panda/fox/dragon
- 分数：8、18、25、38、45、58、65、72、80、88、96、100
- 其中至少 1 名普通宠物 `best_level=5`，用于测试神兽解锁
- 至少 2 名学生有加分/减分事件，用于测试撤销
- 如果神兽已解锁，示例中可直接包含 dragon 学生；否则用普通物种，由验收者手动解锁

---

## 14. API 契约

### 14.1 约定

- Base：`/api`
- 请求/响应：JSON（导出除外）
- 认证：Cookie `petgarden_session`
- 时间：UTC ISO8601
- 成功：2xx；创建 201；删除 204
- 错误：

```json
{
  "error": {
    "code": "SCORE_AT_LIMIT",
    "message": "已经满 100 分啦，可以准备换一位新伙伴了。"
  }
}
```

- 校验错误统一 `VALIDATION_ERROR`，`message` 可读；不返回 Pydantic 原始结构给用户。
- 所有受保护接口未登录 → 401 `AUTH_REQUIRED`。

### 14.2 认证

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 公开，`{"status":"ok","version":"..."}` |
| GET | `/api/auth/status` | 公开，`{"needs_setup":bool,"authenticated":bool,"teacher_name":str\|null}` |
| POST | `/api/auth/setup` | 公开且仅未初始化；`{teacher_name,pin}` |
| POST | `/api/auth/login` | `{pin}`；设置 Cookie |
| POST | `/api/auth/logout` | 清除 Cookie |
| GET | `/api/auth/me` | 当前教师信息 |
| POST | `/api/auth/change-pin` | `{old_pin,new_pin}` |

示例：

```json
// POST /api/auth/login
{ "pin": "1234" }

// 200
{ "teacher": { "name": "王老师" } }
```

### 14.3 班级

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/classes` | 列表，含 `student_count`、`average_score`、`preview_species` |
| POST | `/api/classes` | `{name, grade?, color?}` |
| GET | `/api/classes/{id}` | 详情 |
| PATCH | `/api/classes/{id}` | `{name?, grade?, color?, sort_order?}` |
| DELETE | `/api/classes/{id}` | body `{confirm_name}`；不匹配 409 |

### 14.4 学生

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/classes/{id}/students?sort=seat\|name\|score&q=` | 学生列表（含派生字段） |
| POST | `/api/classes/{id}/students` | `{name, student_no?, seat_no?, species?}` |
| POST | `/api/classes/{id}/students/bulk` | `{text, preview?:bool}` |
| GET | `/api/students/{id}` | 详情 + 最近事件 |
| PATCH | `/api/students/{id}` | `{name?, student_no?, seat_no?, is_present?}` |
| DELETE | `/api/students/{id}` | 删除；级联 |

学生响应：

```json
{
  "id": 12,
  "class_id": 1,
  "name": "林小满",
  "student_no": "03",
  "seat_no": 3,
  "score": 64,
  "level": 4,
  "stage": "蜕变",
  "mood": "happy",
  "score_percent": 64,
  "species": "cat",
  "species_name": "小猫",
  "best_level": 4,
  "can_switch_pet": false,
  "divine_unlocked": false,
  "is_present": true,
  "last_picked_at": null,
  "updated_at": "2026-10-25T08:30:00Z"
}
```

批量导入响应：

```json
{
  "preview": true,
  "created": [],
  "skipped": [
    { "line": 3, "reason": "DUPLICATE_STUDENT_NO", "text": "林小满,03" }
  ],
  "errors": [
    { "line": 5, "reason": "EMPTY_NAME", "text": ",05" }
  ]
}
```

### 14.5 积分与撤销

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/students/{id}/score` | `{delta, reason?}` |
| POST | `/api/score-events/{id}/undo` | 撤销 |
| GET | `/api/students/{id}/events?limit=20` | P1；P0 可在详情中返回最近 5 条 |

评分请求：

```json
{ "delta": 1, "reason": "课堂积极" }
```

评分响应：

```json
{
  "student": { "...": "同 14.4 学生响应" },
  "event": {
    "id": 99,
    "delta": 1,
    "score_before": 63,
    "score_after": 64,
    "reason": "课堂积极",
    "created_at": "2026-10-25T08:31:00Z",
    "undone_at": null
  },
  "level_up": false,
  "stage_changed": false,
  "can_undo": true
}
```

撤销响应：

```json
{
  "student": { "...": "更新后的学生" },
  "event": { "id": 99, "undone_at": "2026-10-25T08:32:00Z", "...": "..." }
}
```

### 14.6 宠物与图鉴

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/pets` | 物种目录、等级阈值、阶段名 |
| GET | `/api/students/{id}/collection` | 图鉴：6 物种 + best_level + 当前 + 锁定状态 |
| POST | `/api/students/{id}/switch-pet` | `{species}` |

目录响应：

```json
{
  "level_thresholds": [0, 20, 40, 60, 80],
  "stage_names": ["初遇", "相伴", "默契", "蜕变", "传说"],
  "species": [
    { "id": "cat", "name": "小猫", "type": "normal" },
    { "id": "dog", "name": "小狗", "type": "normal" },
    { "id": "rabbit", "name": "小兔", "type": "normal" },
    { "id": "panda", "name": "熊猫", "type": "normal" },
    { "id": "fox", "name": "小狐", "type": "normal" },
    { "id": "dragon", "name": "青龙", "type": "divine" }
  ]
}
```

图鉴响应：

```json
{
  "student_id": 12,
  "current_species": "cat",
  "can_switch_pet": true,
  "divine_unlocked": true,
  "items": [
    { "species": "cat", "name": "小猫", "type": "normal", "best_level": 5, "is_current": true, "unlocked": true },
    { "species": "dragon", "name": "青龙", "type": "divine", "best_level": 1, "is_current": false, "unlocked": true }
  ]
}
```

### 14.7 随机点名

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/classes/{id}/rollcall` | `{mode:"fair"\|"random", exclude_absent?:true}` |

响应：

```json
{
  "student": { "...": "学生响应" },
  "pool_size": 9,
  "mode": "fair"
}
```

### 14.8 大屏

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/classes/{id}/display` | 班级 + 全部学生 + 服务端时间 |

- 与 `GET /students` 返回相同的学生结构，另含 `class` 和 `server_time`。
- 前端每 3 秒轮询；页面隐藏时暂停。

### 14.9 设置与数据

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/settings` | 教师名、motion_pref、display_sort、版本、数据路径 |
| PATCH | `/api/settings` | `{teacher_name?, motion_pref?, display_sort?}` |
| GET | `/api/export` | 下载 JSON |
| POST | `/api/import` | `{confirm:"REPLACE", backup:{...}}` |
| POST | `/api/demo` | 创建示例班级 |

### 14.10 错误码

| code | HTTP | 含义 |
|---|---|---|
| `AUTH_REQUIRED` | 401 | 未登录/会话失效 |
| `INVALID_CREDENTIALS` | 401 | PIN 错误 |
| `RATE_LIMITED` | 429 | 登录尝试过多 |
| `SETUP_REQUIRED` | 409 | 尚未初始化 |
| `ALREADY_SETUP` | 409 | 已初始化，不能再次 setup |
| `CLASS_NOT_FOUND` | 404 | 班级不存在 |
| `STUDENT_NOT_FOUND` | 404 | 学生不存在 |
| `DUPLICATE_STUDENT_NO` | 409 | 同班学号重复 |
| `INVALID_SPECIES` | 422 | 物种不支持 |
| `SCORE_AT_LIMIT` | 409 | 已到 0/100 |
| `EVENT_NOT_FOUND` | 404 | 事件不存在 |
| `EVENT_ALREADY_UNDONE` | 409 | 已撤销 |
| `EVENT_NOT_LATEST` | 409 | 不是最新事件，不能撤销 |
| `PET_SWITCH_NOT_READY` | 409 | 当前宠物未满 L5 |
| `DIVINE_LOCKED` | 403 | 神兽未解锁 |
| `SAME_SPECIES` | 409 | 目标物种与当前相同 |
| `NO_STUDENTS` | 409 | 无可抽取学生 |
| `IMPORT_INVALID` | 422 | 备份格式/版本/数据无效 |
| `IMPORT_CONFIRM_REQUIRED` | 400 | 缺少 REPLACE 确认 |
| `VALIDATION_ERROR` | 422 | 字段校验失败 |

---

## 15. 非功能需求

### 15.1 性能

- 本地 API：50 人班级的读取/评分 p95 < 100ms。
- 首屏（本地、已构建）：< 1s 到可交互。
- 大屏 40–60 人：CSS 动画无明显掉帧；轮询不造成整页重绘。
- 前端 gzip 后主包 < 300KB（不含 Vue 运行时之外的第三方大库；不引 UI 框架）。
- 单次评分请求不查全表；按主键/索引查询。
- 不加载任何外部资源。

### 15.2 可访问性

- 目标 WCAG 2.1 AA。
- 所有交互可键盘操作；焦点可见；对话框焦点锁定与恢复。
- 表单有 label；错误信息与字段关联。
- 不依赖颜色传达状态；分数、等级、阶段均有文字。
- 动画尊重 `prefers-reduced-motion` 和应用内开关。
- 触控目标 ≥ 44×44px。
- 屏幕阅读器：宠物有合理标签；点名结果 `aria-live`；toast 可读。
- 投影场景按大字标准检查对比度。

### 15.3 安全与隐私

- PIN 只存 scrypt 哈希；Cookie 签名；HttpOnly + SameSite=Lax。
- 不使用 JWT，不在前端存 token。
- 登录限流。
- 同源、无 CORS 通配、写操作 Origin 校验。
- 导入校验格式/大小/外键；单事务回滚。
- 无 telemetry、无外部请求、无云同步。
- 导出文件含学生姓名，界面明确提示妥善保管。
- `data/` 与 `secret.key` 不进入 git。

### 15.4 可靠性

- SQLite WAL + 外键 + busy_timeout。
- 评分/撤销/换宠/导入使用事务。
- 服务启动时自动建目录/建库；数据库损坏时给出可操作错误，不静默删除。
- 失败请求返回结构化错误；前端有回滚和重试。
- 导入前自动备份。
- 日志：启动、初始化、导入/导出、异常；不记录 PIN、Cookie、完整学生数据。

### 15.5 兼容性

- 浏览器：Chrome/Edge 120+、Firefox 120+、Safari 17+。
- 系统：Windows 10/11（主）；macOS/Linux 可运行但不作为验收重点。
- 屏幕：1366×768、1920×1080、平板横屏、手机竖屏。
- Python 3.12；Node 20+；npm 10+。
- 中文界面；不引入 i18n 框架（P2 再考虑）。

### 15.6 代码质量

- Python：ruff（E/F/I/UP/B/SIM），类型标注，模块职责清晰。
- TypeScript：strict，禁止 `any`（确有必要时局部注释说明）。
- Vue：单文件组件，`<script setup>`，避免超大组件（> 400 行拆分）。
- 领域规则必须有测试；路由层薄。
- 不在组件里复制等级阈值/阶段名/心情规则。
- README 包含安装、启动、备份、忘记 PIN、局域网访问、故障排查。

---

## 16. 测试策略

### 16.1 后端

**纯函数单测**：

- `level_from_score` 边界：-1/0/19/20/39/40/59/60/79/80/100/101。
- 阶段名映射。
- `mood_from_score` 边界：0/19/20/59/60/100。
- 换宠条件：L4 否、L5 是、神兽锁定/解锁。
- 神兽解锁：任意普通 L5；神兽自身 L5 不解锁自己。
- 点名候选池：空班、1 人、全班缺席、上次被抽、公平排序。
- 撤销判定：最新/非最新/已撤销/分数不匹配。

**API 集成测试**（临时 SQLite 文件或内存 + StaticPool）：

- setup 只能一次；PIN 错误；登录/登出/改 PIN。
- 班级 CRUD、删除确认。
- 学生单加/批量预览/重复学号/搜索排序。
- 评分：+1/-1、边界、事件写入、等级、心情、best_level 同步。
- 撤销：成功、非最新、重复撤销。
- 换宠：未满级 409、神兽锁定 403、成功归零、进度保留。
- 点名：公平模式、排除缺席、无学生。
- 导出/导入：往返一致、坏文件回滚、确认字段。
- 未登录访问受保护接口 → 401。

**测试数据**：fixture 建 app + 临时 DB + 已登录客户端；不依赖真实 `data/petgarden.db`。

### 16.2 前端

**纯函数测试**：

- 前端错误码 → 文案映射。
- 排序、搜索、分数格式化。
- `usePolling` 的暂停/恢复逻辑（可用假计时器）。
- 宠物 `hash(seed)` 抖动稳定性。

**组件测试**：

- `PetSprite` 对 6 物种 × 5 等级 × 3 心情都能渲染 `<svg>`，且不含 `<img>`。
- reduced-motion 时根节点带对应属性/类。
- `StudentCard` 触发 +1/-1 事件。
- `RollcallOverlay` 的 Space/Esc 行为（可选）。
- 不做大量快照测试，避免脆弱。

**构建检查**：

```powershell
cd frontend
npm run typecheck
npm run build
npm run test -- --run
```

### 16.3 手工验收

按第 17 章逐条执行。必须包含：

- 断网运行；
- 40 人班级动画；
- 1920×1080 投影可读性；
- 减少动效；
- 撤销；
- 换宠/神兽；
- 导出/导入；
- 刷新后数据一致；
- 浏览器控制台无 error。

### 16.4 质量门禁

```powershell
uv run ruff check .
uv run pytest -q
cd frontend
npm run typecheck
npm run test -- --run
npm run build
```

全部通过才视为完成。

---

## 17. 验收清单

> 在一台干净的 Windows 电脑上，从项目根目录开始。若无法清空机器，至少使用全新的 `data/` 目录和浏览器无痕窗口。

### A. 安装与启动

1. `uv sync` 成功，项目根目录出现 `.venv`；`uv run python -c "import sys; print(sys.executable)"` 指向项目内 `.venv`。
2. `cd frontend && npm install && npm run build` 成功，生成 `frontend/dist/index.html`。
3. 回到根目录执行 `uv run petgarden serve`，浏览器打开 `http://127.0.0.1:8000`。
4. 首次访问跳转 `/setup`；设置教师名「王老师」和 PIN `1234`。
5. 勾选示例班级；进入首页，看到「三年级二班」。
6. 断开网络，刷新页面，功能正常；DevTools Network 中没有外部域名请求。
7. 控制台无 error。

### B. 登录与安全

8. 登出后访问 `/class/1` → 跳转 `/login`。
9. 错误 PIN 5 次 → 锁定提示；等待/重启后恢复。
10. 正确 PIN 登录 → 回到原页面或首页；Cookie 为 HttpOnly。
11. 修改 PIN 后，旧 PIN 失效，新 PIN 可登录。
12. 直接访问一个不存在的 `/api/...` → JSON 404，不是 HTML。

### C. 班级与学生

13. 新建班级「四年级一班」，选择颜色；首页出现卡片。
14. 添加学生「林小满，学号 03，座位 3」；卡片出现，宠物为普通物种。
15. 批量粘贴 10 行（含 1 行重复学号、1 行空行）→ 预览正确标注；确认后只新增有效行。
16. 搜索「林」只显示匹配；切换排序（座位/姓名/积分）立即生效，刷新后保持。
17. 重命名班级；删除另一个空班级需输入名称确认。
18. 同班添加重复学号 → 明确提示，不创建。

### D. 积分与撤销

19. 点击 +1 → 100ms 内数字 +1，宠物播放 cheer；顶部出现可撤销提示。
20. 点击 -1 → 数字 -1，宠物 comfort；不抖动、不闪红。
21. 连续点到 20/40/60/80 → 阶段依次变化，播放 evolve；阶段名和饰品变化。
22. 把某学生加到 100，再点 +1 → 友好提示，分数不变，无新事件。
23. 点撤销 → 分数回到上一步；提示「已撤销」；再次撤销同一事件 → 不可用。
24. 加分后立刻再加一次，然后尝试撤销第一条 → 被拒绝（非最新）。
25. 刷新页面 → 所有分数/等级/阶段/心情一致。
26. 打开两个标签页，分别给同一学生加分 → 不崩溃，大屏/另一页轮询后一致。

### E. 宠物与图鉴

27. 工作台中 6 种宠物（示例数据/手动换宠）都能正确显示，无裂图、无 `<img>`。
28. 宠物在空闲时有呼吸/眨眼/摇尾，且不同学生的节奏不同。
29. 开启「减少动效」→ 循环动画停止；表情、数字、阶段仍正确。
30. L4 学生打开图鉴 → 换宠按钮禁用，提示需要 L5。
31. 把学生加到 L5 → 图鉴可换宠；选择另一种普通宠物 → 二次确认 → 积分归零、新宠物 L1、旧物种进度保留。
32. 未解锁神兽时选择青龙 → 禁用并提示解锁条件。
33. 任意普通宠物达到 L5 → 青龙解锁；换青龙成功。
34. 撤销一条会降低当前等级的积分 → 当前等级下降，但图鉴 best_level 不下降。

### F. 随机点名

35. 点击随机点名 → 全屏浮层，显示宠物和姓名。
36. Space/Enter 再抽，Esc 关闭；连续抽取不明显重复。
37. 把一名学生设为缺席（P1）或手动排除 → 不被抽中。
38. 空班级/全部缺席 → 友好提示，不崩溃。
39. 使用键盘可完成打开、重抽、关闭；焦点正确恢复。

### G. 大屏

40. 打开 `/display/1` → 无侧栏、无评分按钮，全班网格铺满。
41. 在另一个标签页给某学生加分 → 3 秒内大屏数字更新；升级播放 evolve。
42. 1920×1080 下 40 人无需滚动；姓名/积分清晰。
43. 页面切到后台再回来 → 立即拉取最新数据。
44. 断开后端 → 顶部显示「连接中断」提示；恢复后自动继续。
45. 减少动效下大屏无循环动画，数据仍更新。

### H. 数据与设置

46. 设置页导出 JSON；文件包含班级、学生、进度、事件，不含 PIN 哈希/secret。
47. 修改教师名；刷新后保持。
48. 导入刚导出的 JSON → 输入 REPLACE → 数据恢复；`data/backups/` 出现导入前备份。
49. 导入一个损坏/版本不匹配的 JSON → 报错，原数据不变。
50. 删除一个学生 → 相关事件/进度消失；导出中不再出现。
51. 删除班级 → 输入正确名称才删除；取消则保留。
52. `uv run petgarden seed --demo` 可重复执行，不产生不可用的重复数据。

### I. 工程与质量

53. `uv run ruff check .` 通过。
54. `uv run pytest -q` 全部通过。
55. `npm run typecheck` 通过。
56. `npm run build` 通过。
57. `npm run test -- --run` 通过（若配置）。
58. `start.bat` 在缺少 dist 时能自动安装/构建并启动。
59. README 包含：安装、启动、开发、备份、忘记 PIN、局域网访问、故障排查。
60. `git status` 中没有 `data/`、`.venv/`、`secret.key`、`node_modules/`。

---

## 18. 里程碑

| 阶段 | 交付 | 退出条件 |
|---|---|---|
| M0 脚手架 | uv 项目、FastAPI 入口、SQLite、settings、health、start.bat、前端 Vite 骨架 | `uv run petgarden serve` 可启动；`/api/health` 返回 ok；前端能加载 |
| M1 数据与认证 | 表结构、PIN、Cookie、setup/login、班级/学生 CRUD、批量导入 | 对应 API 测试通过；可手动建班/加人 |
| M2 积分引擎 | 评分、事件、撤销、等级/心情、进度同步、领域测试 | 加减分/撤销/边界全部通过；数据刷新一致 |
| M3 宠物与工作台 | SVG 宠物 6×5、动画、学生卡片、详情抽屉、图鉴/换宠 | 6 物种 5 阶段可视；加减分有反应；换宠/神兽规则正确 |
| M4 课堂场景 | 随机点名、大屏轮询、设置/导出/导入/示例数据 | 点名公平；大屏 3s 更新；备份往返一致 |
| M5 打磨验收 | 响应式、空/错/加载态、减少动效、性能、README、全量验收 | 第 17 章全部通过；质量门禁全绿 |

实现顺序建议：M0 → M1 → M2（先把规则和 API 做对）→ M3（宠物视觉）→ M4 → M5。不要先做视觉再补规则。

---

## 19. 技术决策记录（ADR 摘要）

| 决策 | 选择 | 理由 | 代价 |
|---|---|---|---|
| 数据库 | SQLite | 零安装、单文件、备份简单、课堂单机足够 | 不适合多教师高并发（本项目不需要） |
| Python 环境 | uv + 项目内 `.venv` | 可复现、速度快、不污染全局 | 用户需安装 uv（已安装） |
| 宠物渲染 | 内联 SVG + CSS | 动态、离线、矢量、可访问、组件化 | 美术精致度不如手绘位图 |
| 是否用图片 | P0 不用 | 满足动态与离线；避免静态图片风格不一致 | 需要投入 SVG 造型设计 |
| 认证 | PIN + 签名 Cookie | 本地单教师，简单够用；无 JWT | 不适合多用户/公网 |
| UI 框架 | 不用大型 UI 组件库 | 避免通用后台感，控制视觉与包体 | 需要自己写基础组件 |
| 迁移 | P0 不用 Alembic | 单文件首版，`create_all` + 版本号足够 | 未来改表需补迁移 |
| 大屏更新 | 3s 轮询 | 实现简单、可靠、易调试 | 最多 3s 延迟；P1 可换 SSE |
| 撤销 | 事件表 + 最新校验 | 可审计、避免并发覆盖 | 不能撤销任意历史事件 |
| 多教师 | 不做 | 目标用户是单个老师；避免权限复杂度 | 一个工作区一个 PIN |
| 音效 | P1，默认关闭，WebAudio 合成 | 不打扰课堂、无音频文件 | 首版无声音 |
| 深色模式 | 不做 | 教室投影以浅色为主 | 夜间使用体验一般 |

---

## 20. 交付物与完成定义

### 20.1 必须交付

- 可运行的完整源码（后端 + 前端）
- `pyproject.toml`、`uv.lock`、`.python-version`
- `frontend/package.json`、`package-lock.json`
- `README.md`：安装、开发、生产启动、备份、忘记 PIN、局域网、故障排查
- `start.bat` / `dev.bat`
- 示例数据命令
- 后端测试、前端测试（至少纯函数/组件冒烟）
- `.gitignore`（`.venv/`、`data/`、`node_modules/`、`dist/`、`secret.key`、`__pycache__/`）
- 本需求文档与 Agent 提示词保留在根目录

### 20.2 完成定义（Definition of Done）

1. 第 17 章验收清单全部通过（P1 项可标注未做）。
2. 四个质量门禁全绿：ruff、pytest、typecheck、build。
3. 运行时无外部网络请求。
4. 新机器按 README 可从零启动。
5. 没有把 PIN、密钥、数据库提交进仓库。
6. 没有遗留占位页面、`TODO`、假数据按钮。
7. Agent 最终报告包含：实现的模块、运行命令、测试结果、已知限制、下一步建议。

---

## 附录 A：给实现者的十条硬约束

1. **所有实现都在本项目内完成，不依赖项目外的代码、数据库或图片。**
2. **不要引入其他数据库、大型 UI 组件库、Docker、Redis、Alembic。**
3. **宠物必须是内联 SVG + CSS，不得用 `<img>` 或外部图片。**
4. **数据库必须是项目内 SQLite 单文件。**
5. **Python 必须由 uv 管理，`.venv` 在项目根目录。**
6. **运行时不请求任何外部资源。**
7. **等级/阶段/心情/换宠/点名规则只能有一份实现（后端领域层）。**
8. **每次积分必须写事件，最近一次必须可撤销。**
9. **低分不羞辱、不排名、不红色警告。**
10. **所有动画必须支持减少动效。**
