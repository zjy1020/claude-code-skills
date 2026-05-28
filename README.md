# Claude Code Skills

个人收集和自建的 [Claude Code](https://claude.ai/code) Skills 合集。

## 什么是 Skill？

Skill 是 Claude Code 的扩展包，提供特定领域的专业知识、工作流和工具。安装后可通过 `/skill-name` 或自然语言自动触发。

## Skills 列表

| # | Skill | 类型 | 调用方式 | 来源 | Stars | 环境依赖 |
|---|-------|------|---------|------|-------|---------|
| 1 | **agent-skill-creator** | 第三方 | `/agent-skill-creator` | [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator) | 1.2K ⭐ | Python 3, git, curl |
| 2 | **brainstorming** | 第三方 | `/brainstorming` | [obra/superpowers](https://github.com/obra/superpowers) | 210K ⭐ | 无 |
| 3 | **concise-response-skill** | 自建 | `/concise-response` | — | — | 无 |
| 4 | **find-skills** | 官方 | 自然触发 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | 20.4K ⭐ | Node.js 18+ |
| 5 | **frontend-design** | 官方 | 自然触发 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | 127K ⭐ | 无（官方内置） |
| 6 | **ui-ux-pro-max** | 第三方 | 自然触发 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 83.9K ⭐ | Node.js |
| 7 | **hud-skill** | 自建 | `/hud-skill show`, statusLine | — | — | Python 3, git, curl, Git Bash（Win） |

## 各 Skill 详细介绍

### 1. agent-skill-creator — Skill 自动创建工厂

- **命令**: `/agent-skill-creator`
- **仓库**: [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)
- **环境依赖**: Python 3, git, curl（天气/语录 API）
- **安装**: 21K
- **说明**: 跨平台 agent skill 的"暗工厂"。输入工作流描述、文档、链接、代码等素材，自动产出完整的、生产可用的 skill。用户只需要提供原始材料，不需要写代码、填模板或了解 skill 规范。

**示例：**
```
/agent-skill-creator 我每周要拉销售数据、清洗、生成报表
/agent-skill-creator https://wiki.internal/deploy-runbook
```

---

### 2. brainstorming — 头脑风暴/设计探讨

- **命令**: `/brainstorming`
- **仓库**: [obra/superpowers](https://github.com/obra/superpowers)
- **环境依赖**: 无
- **安装**: 210K+
- **说明**: 在任何创造性工作之前触发。通过逐一提问帮你理清需求、约束和设计方案，形成设计文档并获得批准后才开始编码。

**核心流程：**
1. 探索项目上下文
2. 逐一提问澄清需求
3. 提出 2-3 种方案及推荐
4. 分块展示设计并获批准
5. 保存设计文档到 `docs/superpowers/specs/`

---

### 3. concise-response-skill — 精简回复

- **命令**: `/concise-response`
- **仓库**: 自建
- **环境依赖**: 无
- **说明**: 精简 Claude 的回复，减少 token 浪费。去除客套话、前缀废话、元评论、重复问题等冗余内容。

**核心规则：**
- 不说"好的、当然、不客气、我来、让我"等客套前缀
- 不重复用户问题
- 一句话能说完不说两句
- 最小化 tool 调用

---

### 4. find-skills — Skill 搜索工具

- **命令**: 自然触发（"找一个能 X 的 skill"）
- **仓库**: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- **环境依赖**: Node.js 18+
- **安装**: 20.4K+
- **说明**: 搜索和发现 open agent skills 生态中的可用 skill。当用户询问是否有某个功能的 skill 时自动触发。

**搜索方式：**
```bash
npx skills find <关键词>
```

**示例：**
```bash
npx skills find ppt
npx skills find git
npx skills find react testing
```

---

### 5. frontend-design — 前端界面设计

- **命令**: 自然触发（前端相关任务）
- **仓库**: [anthropics/claude-code](https://github.com/anthropics/claude-code)（官方内置）
- **环境依赖**: 无（官方内置）
- **说明**: 创建高质量、有独特美学风格的前端界面。避免千篇一律的 AI 风格，注重排版、配色、视觉细节。支持 HTML/CSS/JS、React、Vue 等框架。

**设计理念：**
- 先确定大胆的美学方向（极简/极繁/复古/未来等）
- 精选独特字体搭配，避免泛用字体
- 注重排版层次、留白、交互细节

---

### 6. ui-ux-pro-max — UI/UX 设计系统

- **命令**: 自然触发（UI/UX 设计相关任务）
- **仓库**: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- **环境依赖**: Node.js（可选 shadcn/ui MCP）
- **安装**: 83.9K+
- **说明**: 综合性 UI/UX 设计系统，内置大量设计资源和指南。

**覆盖范围：**
- 50+ 设计样式：glassmorphism, minimalism, brutalism, neumorphism, bento grid, dark mode 等
- 161 配色方案、57 字体配对、99 UX 指南、25 图表类型
- 10 种技术栈：React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, shadcn/ui 等

---

### 7. hud-skill — 系统状态 HUD 面板

- **命令**: `/hud-skill show`, `/hud-skill line`
- **仓库**: 自建
- **环境依赖**: Python 3, git, curl, Windows 需 Git Bash
- **说明**: Claude Code 底部的常驻 HUD 状态栏，显示系统信息（CPU、内存、磁盘、温度）、天气、Git 分支、随机中文语录。支持三行彩色面板和单行 statusLine 模式，所有数据实时刷新。

**显示内容：**
- 模型名、上下文进度条、系统信息
- CPU 负载、内存/磁盘使用率
- 天气状况（中文翻译）、Git 分支状态
- 随机中文语录（彩虹逐字着色，每 2 分钟刷新）
- 支持 Windows 和 Linux 双平台

## 安装方法

所有 skill 文件位于 `skills/` 目录下。安装方式：

### 方式一：直接复制
```bash
# Claude Code
cp -r skills/<skill-name> ~/.claude/skills/<skill-name>

# 全局安装（支持 Codex, Cursor, Kiro 等）
cp -r skills/<skill-name> ~/.agents/skills/<skill-name>
```

### 方式二：通过 npx skills 安装
```bash
# 从 GitHub 仓库安装
npx skills add <仓库地址> --skill <skill-name>
```

## License

MIT
