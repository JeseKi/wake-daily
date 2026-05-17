# 觉知日记

一个移动端优先的私密觉察日记 Web Demo。它保留了模板项目里的注册、登录、管理员、数据库和前后端分层能力，但把第一屏和主流程改成每日一问、自由书写、最近回看和松动反馈。

这个 Demo 不是心理治疗工具，不做诊断、疗愈承诺、打卡排行或复杂统计。它适合用于早期产品验证，也适合继续学习 FastAPI + React 的业务模块开发方式。

## 功能

- 用户注册 / 登录
- 今日一问
- 自由书写并保存日记
- 查看最近 7 / 14 / 30 天日记
- 回看时高亮执着词：应该、必须、不甘心、非要、一定、不能、凭什么、早知道
- 每篇日记可记录一次“这个觉察让我松了一点”
- 管理员维护每日问题
- 保留个人资料、修改密码、设备管理和管理员用户管理能力

## 技术栈

- 后端：FastAPI、SQLAlchemy、Pydantic、Alembic、SQLite、JWT Auth、Loguru
- 前端：React 19、Vite、React Router、TypeScript、Ant Design、Tailwind CSS、Axios
- 测试：pytest

## 快速开始

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pnpm install
cp .env.example .env
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

首次初始化数据库会创建默认管理员：

- 用户名：`admin`
- 密码：`admin123`
- 邮箱：`admin@example.com`

## 目录

```text
src/server/journal/                 # 日记业务模块
src/server/journal/tests/           # journal 后端测试
src/client/pages/journal/           # 今日书写与最近回看
src/client/pages/admin/JournalQuestionManagementPage.tsx
src/client/lib/journal.ts           # journal 前端 API
alembic/versions/                   # 数据库迁移脚本
```

`src/server/example_module` 仍然保留，适合作为学习 router / service / dao / tests 分层的参考。

## 数据与隐私说明

第一版为了开发和学习简单，日记内容会保存到服务端 SQLite 数据库中。管理员页面当前只提供每日问题管理，不提供查看用户日记入口。

这个 Demo 不会把日记发送给第三方 AI，也不包含公开分享、日记广场、推送、支付或预约系统。若要用于真实高隐私场景，需要继续补充删除、导出、加密、备份和访问审计等能力。

## 验证

后端测试：

```bash
.venv/bin/python -m pytest . -q
```

前端构建：

```bash
pnpm build
```

## 继续学习

建议先从三个地方开始：

1. 改每日问题：看 `src/server/journal` 和管理员“每日问题”页面。
2. 改页面文案：看 `src/client/pages/landing` 和 `src/client/pages/journal`。
3. 改数据库字段：看 `src/server/journal/models.py`，并配合 Alembic 迁移。

不要一开始就加小程序、支付、AI 或推送。先让 2-3 个朋友连续用 7 天，看他们是否真的愿意回来写。

