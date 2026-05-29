# Claude Code Skills

个人收集的 [Claude Code](https://claude.ai/code) Skills，按来源分组管理。

> 共 12 个 Skill · 安装位置: `~/.claude/skills/`

---

## 目录

- [一、Superpowers 工作流套件](#一superpowers-工作流套件)
- [二、Dynamous 技能工厂](#二dynamous-技能工厂)
- [三、其他独立 Skill](#三其他独立-skill)
- [四、缺失的 Superpowers 依赖](#四缺失的-superpowers-依赖)

---

## 一、Superpowers 工作流套件

来源: [obra/superpowers](https://github.com/obra/superpowers) · 210K ⭐

覆盖需求探索 → 写计划 → TDD 编码 → 计划执行 → 验证 → 调试的完整闭环。

### 工作流关系

```
brainstorming ──→ writing-plans ──→ test-driven-development
       │                                │
       │                                ▼
       │                      executing-plans
       │                         │   │   │
       │                         │   │   └─→ finishing-a-development-branch*
       │                         │   └─────→ using-git-worktrees*
       │                         └─────────→ subagent-driven-development*
       ▼
systematic-debugging ──→ test-driven-development
       │
       └───────────────→ verification-before-completion
```

> `*` 标记的为未安装的依赖 skill

---

### 1. brainstorming

| 项目 | 内容 |
|------|------|
| **调用** | `/brainstorming` 或自然语言 |
| **触发** | 任何创造性工作前自动触发 |
| **后继** | → `writing-plans` |

9 步流程：探索上下文 → 逐一澄清需求 → 提 2-3 方案 → 分块获批准 → 写设计文档 → 自审 → 用户审核 → 转 writing-plans

---

### 2. writing-plans

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（有 spec 需要实施时） |
| **后继** | → `executing-plans` / `subagent-driven-development` |

产出 bite-sized 实施计划：scope check → 文件结构映射 → 每步 2-5 分钟的任务分解。输出到 `docs/superpowers/plans/`。

---

### 3. test-driven-development

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（实现功能 / bugfix 前） |
| **配套** | `testing-anti-patterns.md` |

**Red-Green-Refactor 流程：**
1. **RED** — 写最小失败测试
2. **Verify RED** — 确认因"功能缺失"而失败
3. **GREEN** — 最简代码通过
4. **Verify GREEN** — 本测试 + 其他测试通过
5. **REFACTOR** — 保持绿色清理代码

**铁律:** `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`

---

### 4. executing-plans

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（有写好的计划要执行时） |
| **依赖** | `using-git-worktrees`* · `finishing-a-development-branch`* · `subagent-driven-development`* |

三步流程：加载审查计划 → 逐任务执行 → 调用收尾 skill。遇阻塞立即停止询问。

---

### 5. verification-before-completion

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（声称"做完了/修好了/通过了"时） |

**核心:** "Evidence before claims, always" — 任何完成/成功声明都强制先跑验证。

---

### 6. systematic-debugging

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（遇 bug / 测试失败 / 异常时） |
| **依赖** | `test-driven-development` · `verification-before-completion` |

4 阶段：根因分析 → 模式分析 → 假设验证 → 修复实现（≥3 次失败则质疑架构）。

配套: `root-cause-tracing.md` · `defense-in-depth.md` · `condition-based-waiting.md`

---

## 二、Dynamous 技能工厂

### agent-skill-creator

| 项目 | 内容 |
|------|------|
| **调用** | `/agent-skill-creator <描述>` |
| **来源** | [FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator) · 1.2K ⭐ |
| **依赖** | Python 3, git, curl |

Level 5 暗工厂 — 从原始素材自动产出跨平台 skill。5 阶段管线：Discovery → Design → Architecture → Detection → Implementation。

---

## 三、其他独立 Skill

### concise-response-skill

| 项目 | 内容 |
|------|------|
| **调用** | `/concise-response` |
| **来源** | 自建 |

极致省 token：无客套 · 无前缀 · 无元评论 · 不重复问题 · 最小 tool 调用

### find-skills

| 项目 | 内容 |
|------|------|
| **调用** | 自然语言（"找一个能做 X 的 skill"） |
| **来源** | [vercel-labs/skills](https://github.com/vercel-labs/skills) · 20.4K ⭐ |
| **依赖** | Node.js 18+ |

```bash
npx skills find <关键词>
```

### frontend-design

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（前端任务） |
| **来源** | anthropics/claude-code 内置 · 127K ⭐ |

追求独特美学方向，避免 AI 模板感。支持 HTML/CSS/JS、React、Vue 等。

### ui-ux-pro-max

| 项目 | 内容 |
|------|------|
| **调用** | 自然触发（UI/UX 设计任务） |
| **来源** | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) · 83.9K ⭐ |

50+ 样式 · 161 配色 · 57 字体 · 99 UX 指南 · 25 图表 · 10 技术栈

### hud-skill

| 项目 | 内容 |
|------|------|
| **调用** | `/hud-skill [show\|line\|quote]` |
| **来源** | 自建 |
| **依赖** | Python 3, git, curl, Git Bash(Win) |

底部 HUD 状态栏：CPU/内存/磁盘/温度/天气/Git/时间/中文语录

---

---

```bash
# 1. 从本仓库复制到全局
cp -r skills/<skill-name> ~/.claude/skills/

# 2. 或从 GitHub 直接安装
npx skills add https://github.com/zjy1020/claude-code-skills --skill <skill-name>
```

## License

MIT
