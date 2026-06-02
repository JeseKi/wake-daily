# 觉察日记

觉察日记是一个面向教学场景的学生觉察训练工具。产品帮助学生练习三件事：客观观察、情绪标记、回到当下。

它不是心理诊断或治疗工具，也不做公开排名、竞争打卡或社交广场。整体设计保持安静、克制、低刺激，使用树木、森林、水源作为视觉意象：学生的连续练习像一棵树缓慢生长，共振墙像一片匿名的林间空地。

## 核心功能

- 学生端班级绑定：学生输入教师下发的绑定码，加入对应班级。
- 每日三关觉察训练：
  - 第一关：客观记录，像照相机一样记录 1-3 件事。
  - 第二关：情绪标记，选择触动最大的事件，标记情绪和触发点。
  - 第三关：当下锚点，记录一个此刻观察到的细节。
- 客观性检测：检测“我”和主观词，给出温和提醒，不强制阻止提交。
- 我的觉察本：学生查看自己的历史三关内容和教师回应。
- 我的成长：用树的阶段展示连续练习状态：种子、幼苗、小树、大树、开花。
- 共振墙：教师匿名收录日记片段，学生只能点击“我也共鸣”。
- 教师端：
  - 创建班级和绑定码。
  - 查看、筛选、批阅学生三关日记。
  - 匿名收录片段到共振墙。
  - 查看提交率、累计日记、情绪分布等班级数据。

## 学生端使用方式

1. 打开网站并注册 / 登录学生账号。
2. 首次进入后，在“今日觉察”页面输入教师提供的班级绑定码。
3. 完成每日三关：
   - 客观记录：只写可观察事实，尽量避免评价、猜测和“我觉得”。
   - 情绪标记：选择最有触动的一件事，选择一个情绪词，并写下触发点。
   - 当下锚点：观察周围环境，写下一个之前忽略的细节。
4. 提交后，可在“我的觉察本”查看历史记录和教师评价。
5. 在“我的成长”查看连续练习形成的树木阶段和徽章。
6. 在“共振墙”查看教师匿名收录的片段，并可点击“我也共鸣”。

说明：

- 每个学生 V1 默认只能绑定一个班级。
- 每天只能提交一次三关觉察日记。
- 客观性检测只是提醒，不代表对错判断。
- 共振墙不显示作者、点赞人或排名。

## 教师端使用方式

教师端使用管理员账号进入“管理员面板”。

默认管理员：

- 用户名：`admin`
- 密码：`admin123`
- 邮箱：`admin@example.com`

### 1. 创建班级

进入：

```text
管理员面板 -> 觉察日记 -> 班级管理
```

操作：

- 输入班级名称。
- 创建班级。
- 将生成的绑定码发给学生。
- 如绑定码泄露或需要更新，可点击“重置绑定码”。
- 可停用班级，停用后新学生不能再用该绑定码加入。

### 2. 批阅日记

进入：

```text
管理员面板 -> 觉察日记 -> 日记批阅
```

教师可以：

- 按班级筛选学生提交。
- 展开查看三关完整内容。
- 填写评分、奖励标签和评价。
- 将合适片段匿名收录到共振墙。

批阅说明：

- 教师评价只展示给对应学生本人。
- 收录到共振墙的内容不显示学生身份。
- 共振墙只保留“我也共鸣”，不做公开评论和排行。

### 3. 查看数据看板

进入：

```text
管理员面板 -> 觉察日记 -> 数据看板
```

当前看板包含：

- 班级数
- 已绑定学生数
- 今日提交数
- 今日提交率
- 累计日记数
- 共振片段数
- 情绪分布

## 技术栈

- 后端：FastAPI、SQLAlchemy、Pydantic、Alembic、SQLite、JWT Auth、Loguru
- 前端：React 19、Vite、React Router、TypeScript、Ant Design、Tailwind CSS、Axios
- 测试：pytest、mypy、ESLint

## 快速开始

安装依赖：

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pnpm install
cp .env.example .env
```

初始化 / 升级数据库：

```bash
alembic upgrade head
```

启动后端：

```bash
.venv/bin/python run.py
```

启动前端：

```bash
pnpm dev
```

默认地址：

- 前端开发环境：`http://localhost:5173`
- 后端 API：`http://localhost:8000`
- 健康检查：`http://localhost:8000/api/health`

## 迁移说明

项目使用 Alembic 管理数据库结构。新增字段或表时，应优先编写迁移脚本，不要在业务代码中硬性补字段。

如果旧环境曾经通过 `Base.metadata.create_all()` 自动建过表，但没有 Alembic 版本记录，执行迁移时可能遇到类似错误：

```text
sqlite3.OperationalError: table daily_questions already exists
```

这说明数据库表已经存在，但 `alembic_version` 没有记录到对应版本。保留数据的处理方式是先备份数据库，然后确认旧表结构匹配初始迁移，再执行：

```bash
alembic stamp 20260517_0001
alembic upgrade head
```

如果是无数据的新环境，也可以删除旧 SQLite 数据库文件后重新执行：

```bash
alembic upgrade head
```

## 目录

```text
src/server/journal/                         # 觉察日记后端业务模块
src/server/journal/tests/                   # journal 后端测试
src/client/pages/journal/                   # 学生端页面
src/client/pages/admin/JournalV1ManagementPage.tsx
src/client/lib/journal.ts                   # journal 前端 API
alembic/versions/                           # 数据库迁移脚本
```

`src/server/example_module` 仍然保留，可作为后端 router / service / dao / tests 分层参考。

## 数据与隐私说明

当前版本会将学生日记内容保存到服务端 SQLite 数据库中。教师可在管理员面板中查看班级内学生提交，用于教学反馈。

当前版本不会把日记发送给第三方 AI，也不包含公开评论、公开排名、支付、推送或预约系统。若用于真实学校或高隐私场景，建议继续补充：

- 数据删除与导出
- 管理员访问审计
- 数据库备份策略
- 更细粒度的教师 / 班级权限
- 敏感内容处理流程

## 验证

后端测试：

```bash
.venv/bin/python -m pytest . -q
```

类型检查：

```bash
.venv/bin/mypy .
```

前端构建：

```bash
pnpm build
```

前端 lint：

```bash
pnpm lint
```
