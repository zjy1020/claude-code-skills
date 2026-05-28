---
name: hud-skill
activation: /hud-skill
description: >-
  配置和管理 Claude Code 底部常驻 HUD 状态栏。显示 CPU、内存、磁盘、温度、天气、Git 分支、时间、中文语录。支持彩色显示、自定义内容。关键词：hud、状态栏、statusline、底部显示、系统监控、语录、天气、彩色。
license: MIT
metadata:
  author: Claude Code
  version: 2.0.0
  created: 2026-05-28
  last_reviewed: 2026-05-28
  review_interval_days: 90
  dependencies:
    - url: https://wttr.in
      name: Weather API
      type: api
    - url: https://v1.hitokoto.cn
      name: Hitokoto API
      type: api
---
# /hud-skill — Claude Code 底部 HUD 状态栏

你是一个 HUD 配置管理技能。你的职责是帮助用户管理和自定义 Claude Code 聊天界面底部的常驻 HUD 状态栏，以及显示系统状态信息。

状态栏脚本位置: `~/.claude/plugins/claude-hud-status.sh`
采集脚本位置: `~/.claude/skills/hud-skill/scripts/hud_collector.py`

## 子命令

| 命令 | 功能 |
|------|------|
| `/hud-skill` | 显示完整 HUD 面板（三行彩色） |
| `/hud-skill show` | 显示完整 HUD 面板预览 |
| `/hud-skill line` | 单行彩色状态（用于 statusLine） |
| `/hud-skill quote` | 随机中文语录（彩虹色） |
| `/hud-skill weather` | 查看天气信息 |
| `/hud-skill customize` | 自定义 HUD 显示内容 |
| `/hud-skill status` | 检查 HUD 是否正常运行 |

## 显示效果

默认 HUD 面板（`/hud-skill show`）：
```
┌─ HUD 状态面板 ─────────────────────────────
│ deepseek-v4-flash  Windows 11 10.0.26100
│ CPU:0.32 MEM:2427M/7896M DISK:17G/98G 24°C 晴 [main] 20:14
│ 身是菩提树，心如明镜台，时时勤拂拭，勿使惹尘埃。 ——神秀
└───────────────────────────────────────────
```

状态栏单行（`statusLine`）：
```
deepseek-v4-flash CPU:0.32 MEM:2427M/7896M DISK:17G/98G 24°C 晴 [main] 20:14
```

各组件颜色：CPU 粉色、MEM 绿色/黄/红(阈值)、DISK 黄色、温度橙色、天气紫色、Git 蓝色、时间青色、语录彩虹逐字。

## 实现

配置位于 `~/.claude/settings.json` 的 `statusLine.command`：

```json
"statusLine": {
  "command": "bash ~/.claude/plugins/claude-hud-status.sh",
  "type": "command"
}
```

Windows 路径应使用正斜线：
```json
"statusLine": {
  "command": "bash /c/Users/YBY/.claude/plugins/claude-hud-status.sh",
  "type": "command"
}
```

## 依赖

- Python 3（核心采集脚本）
- Git（分支检测）
- curl（天气和语录 API）
- 网络连接（天气、语录需要联网）

## 来源

Linux 原版来自 Arch Linux 配置，经适配后支持 Windows/MSYS2/Git Bash。
