#!/usr/bin/env python3
"""HUD data collector — cross-platform (Windows/Linux) with ANSI colors."""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output to avoid GBK encoding issues on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

GIT_REPO_CACHE = {}
HUD_CACHE_FILE = str(Path.home() / ".claude" / "plugins" / "hud_cache.json")

# ANSI colors
C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[38;5;51m",   # bright cyan/teal
    "pink": "\033[38;5;213m",  # bright pink/magenta
    "green": "\033[38;5;46m",   # bright green
    "yellow": "\033[38;5;226m", # bright yellow
    "orange": "\033[38;5;214m", # orange
    "purple": "\033[38;5;135m", # purple
    "blue": "\033[38;5;39m",    # bright blue
    "white": "\033[38;5;255m",  # bright white
    "red": "\033[38;5;196m",    # bright red
    "dim": "\033[2m",
}


def run_cmd(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_system_info():
    is_win = platform.system() == "Windows"
    if is_win:
        os_name = "Windows"
        kernel = platform.version()
        # Windows version: major.minor.build (e.g. 10.0.26100 = Win11)
        ver = kernel.split(".")
        if len(ver) >= 3:
            major, build = int(ver[0]), int(ver[2])
            if major == 10 and build >= 22000:
                os_name = "Windows 11"
            elif major == 10:
                os_name = "Windows 10"
        arch = platform.machine()
        hostname = platform.node()
    else:
        hostname = run_cmd(["uname", "-n"]) or "unknown"
        kernel = run_cmd(["uname", "-r"]) or "unknown"
        arch = run_cmd(["uname", "-m"]) or "unknown"
        os_name = run_cmd(["sh", "-c", ". /etc/os-release 2>/dev/null && echo $NAME"]) or "Linux"
    uptime_str = run_cmd(["uptime", "-p"]) or "unknown"
    return {"hostname": hostname, "os": os_name, "kernel": kernel, "arch": arch, "uptime": uptime_str.replace("up ", "")}


def get_cpu_load():
    load = run_cmd(["cat", "/proc/loadavg"])
    if load:
        parts = load.split()
        return {"1min": parts[0], "5min": parts[1], "15min": parts[2]}
    return {"1min": "N/A", "5min": "N/A", "15min": "N/A"}


def get_cpu_temp():
    try:
        r = subprocess.run(["sensors", "-u"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=5)
        for line in r.stdout.splitlines():
            if "temp1_input" in line:
                val = float(line.split()[-1])
                if 0 < val < 200:
                    return f"{val:.1f}°C"
    except Exception:
        pass
    try:
        for z in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
            val = int(z.read_text().strip()) / 1000
            if 0 < val < 200:
                return f"{val:.1f}°C"
    except Exception:
        pass
    return "N/A"


def get_memory():
    # Try /proc/meminfo first (Linux, MSYS2, WSL)
    try:
        with open("/proc/meminfo") as f:
            data = {}
            for line in f:
                parts = line.split()
                k = parts[0].rstrip(":")
                if k in ("MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree"):
                    data[k] = int(parts[1]) // 1024
        total = data.get("MemTotal", 0)
        avail = data.get("MemAvailable", 0)
        used = total - avail
        if total > 0:
            return {"total_mb": total, "used_mb": used, "avail_mb": avail,
                    "used_pct": round(used / total * 100, 1)}
    except Exception:
        pass
    # Fallback: PowerShell (Windows native)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            total = int(d["TotalVisibleMemorySize"]) // 1024
            free = int(d["FreePhysicalMemory"]) // 1024
            used = total - free
            return {"total_mb": total, "used_mb": used, "avail_mb": free,
                    "used_pct": round(used / total * 100, 1) if total else 0}
    except Exception:
        pass
    return {"total_mb": 0, "used_mb": 0, "avail_mb": 0, "used_pct": 0}


def get_disk():
    try:
        r = subprocess.run(["df", "-BG", "/"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=5)
        lines = r.stdout.splitlines()
        if len(lines) >= 2:
            # Handle filesystem paths with spaces (e.g. "C:/Program Files/Git")
            parts = [p for p in lines[1].split() if p]
            # parts layout after filtering empties:
            # ["C:/Program", "Files/Git", "221G", "170G", "51G", "78%", "/"]
            # Find the G-pattern columns
            g_cols = [i for i, p in enumerate(parts) if p.endswith("G") and i > 0]
            pct_col = [i for i, p in enumerate(parts) if "%" in p]
            if len(g_cols) >= 2 and pct_col:
                total = int(parts[g_cols[0]].rstrip("G"))
                used = int(parts[g_cols[1] if len(g_cols) > 1 else g_cols[0]].rstrip("G"))
                avail = total - used
                pct = parts[pct_col[0]].rstrip("%")
                return {"total_gb": total, "used_gb": used, "free_gb": avail, "used_pct": pct}
    except Exception:
        pass
    return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "used_pct": 0}


def get_git_status(path=None):
    cwd = path or os.getcwd()
    if cwd in GIT_REPO_CACHE:
        return GIT_REPO_CACHE[cwd]
    try:
        branch = run_cmd(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"])
        if not branch:
            GIT_REPO_CACHE[cwd] = None
            return None
        dirty = run_cmd(["git", "-C", cwd, "status", "--porcelain"])
        ahead = run_cmd(["git", "-C", cwd, "rev-list", "--count", "@{upstream}..HEAD", "--"])
        behind = run_cmd(["git", "-C", cwd, "rev-list", "--count", "HEAD..@{upstream}", "--"])
        info = {
            "branch": branch,
            "dirty": bool(dirty),
            "dirty_count": len(dirty.splitlines()) if dirty else 0,
            "ahead": ahead or "0",
            "behind": behind or "0",
        }
        GIT_REPO_CACHE[cwd] = info
        return info
    except Exception:
        GIT_REPO_CACHE[cwd] = None
        return None


def get_weather():
    try:
        r = subprocess.run(
            ["curl", "-s", "wttr.in?format=%C|%t|%h|%w|%p"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split("|")
            cond = translate_weather(parts[0]) if len(parts) > 0 else "N/A"
            return {
                "condition": cond,
                "temp": parts[1].replace("+", "") if len(parts) > 1 else "N/A",
                "humidity": parts[2] if len(parts) > 2 and parts[2] else "N/A",
                "wind": parts[3] if len(parts) > 3 and parts[3] else "N/A",
                "precip": parts[4] if len(parts) > 4 and parts[4] else "N/A",
            }
    except Exception:
        pass
    return None


def translate_weather(cond):
    """Translate English weather condition to Chinese."""
    mapping = {
        "Clear": "晴", "Sunny": "晴", "Partly cloudy": "多云",
        "Cloudy": "阴", "Overcast": "阴", "Mist": "薄雾", "Fog": "雾",
        "Light rain": "小雨", "Moderate rain": "中雨", "Heavy rain": "大雨",
        "Light rain shower": "小阵雨", "Moderate or heavy rain shower": "阵雨",
        "Light drizzle": "毛毛雨", "Patchy rain possible": "可能有雨",
        "Light snow": "小雪", "Moderate snow": "中雪", "Heavy snow": "大雪",
        "Light snow shower": "小阵雪", "Moderate or heavy snow shower": "阵雪",
        "Thundery outbreaks possible": "雷阵雨", "Patchy light rain with thunder": "雷雨",
        "Haze": "霾", "Smoke": "烟霾",
    }
    for eng, chn in mapping.items():
        if eng.lower() in cond.lower():
            return chn
    return cond


def get_hitokoto():
    """Get a random Chinese quote from Hitokoto API (cached on disk 10 min)."""
    now = time.time()
    # Read cache from file
    try:
        cache = json.loads(Path(HUD_CACHE_FILE).read_text(encoding="utf-8"))
        if now - cache.get("q_time", 0) < 120 and cache.get("q_text", ""):
            return cache
    except Exception:
        cache = {}
    # Fetch new quote
    try:
        r = subprocess.run(
            ["curl", "-s", "https://v1.hitokoto.cn/?c=a&c=b&c=c&c=d&c=i&c=j"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10
        )
        if r.returncode == 0:
            d = json.loads(r.stdout)
            cache["q_text"] = d.get("hitokoto", "")
            cache["q_from"] = d.get("from", "")
            cache["q_who"] = d.get("from_who", "")
            cache["q_time"] = now
            # Write cache to disk
            try:
                Path(HUD_CACHE_FILE).parent.mkdir(parents=True, exist_ok=True)
                Path(HUD_CACHE_FILE).write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
    except Exception:
        pass
    return cache


def get_claude_model():
    """Read Claude Code model from settings."""
    settings_paths = [
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.local.json",
    ]
    for p in settings_paths:
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                return d.get("env", {}).get("ANTHROPIC_MODEL") or \
                       d.get("env", {}).get("ANTHROPIC_DEFAULT_SONNET_MODEL") or \
                       d.get("env", {}).get("ANTHROPIC_DEFAULT_OPUS_MODEL") or "unknown"
            except Exception:
                pass
    return "unknown"


def get_context_info():
    """Read context info + model name from stdin JSON (provided by Claude Code)."""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw.strip():
                d = json.loads(raw)
                # Real model name from the running session
                model = d.get("model", {}) or {}
                model_name = model.get("display_name", "")
                cw = d.get("context_window", {}) or {}
                # Use ready-made percentage if available
                pct = cw.get("used_percentage", 0)
                if pct == 0 and cw.get("context_window_size", 0) > 0:
                    # Fallback: calculate from tokens
                    used = cw.get("total_input_tokens", 0) or cw.get("total_output_tokens", 0)
                    pct = round(used / cw["context_window_size"] * 100)
                bars = 10
                filled = round(pct / 100 * bars)
                bar = "█" * filled + "░" * (bars - filled)
                color = C['red'] if pct > 85 else C['yellow'] if pct > 70 else C['green']
                return {"pct": pct, "bar": bar, "color": color, "model": model_name}
    except Exception:
        pass
    return None


def get_time():
    now = datetime.now(timezone.utc).astimezone()
    tz = time.tzname[0] if time.daylight and time.localtime().tm_isdst else time.tzname[0]
    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": ["一", "二", "三", "四", "五", "六", "日"][now.weekday()],
        "timezone": tz or "UTC",
    }


# ── StatusLine output ──────────────────────────────────────────────

def cmd_line(args):
    """Multi-line Chinese HUD output for Claude Code statusLine."""
    load = get_cpu_load()
    mem = get_memory()
    disk = get_disk()
    weather = get_weather()
    git = get_git_status()
    t = get_time()
    sysinfo = get_system_info()
    temp = get_cpu_temp()
    ctx = get_context_info()
    model = ctx.get("model", "") if ctx else ""
    if not model:
        model = get_claude_model()

    lines = []

    # ── Line 1: 模型 │ 上下文 │ 系统 ──
    l1_parts = [f"{C['cyan']}{model}{C['reset']}", f"{C['dim']}│{C['reset']}"]
    if ctx:
        l1_parts.append(f"{ctx['color']}{ctx['bar']} {ctx['pct']}%{C['reset']}")
        l1_parts.append(f"{C['dim']}│{C['reset']}")
    l1_parts.append(f"{C['pink']}{sysinfo['os']} {sysinfo['kernel']}{C['reset']}")
    lines.append(" ".join(l1_parts))

    # ── Line 2: 负载 内存 磁盘 温度 天气 Git 时间 ──
    l2_parts = []

    # CPU 负载
    l2_parts.append(f"{C['pink']}CPU {load['1min']}{C['reset']}")

    # 内存
    mem_str = f"{mem['used_mb']}M/{mem['total_mb']}M"
    mem_pct = mem['used_pct']
    mc = C['red'] if mem_pct > 90 else C['yellow'] if mem_pct > 75 else C['green']
    l2_parts.append(f"{mc}内存 {mem_str}{C['reset']}")

    # 磁盘
    disk_str = f"{disk['used_gb']}G/{disk['total_gb']}G"
    l2_parts.append(f"{C['yellow']}磁盘 {disk_str}{C['reset']}")

    # 温度
    if temp != "N/A":
        l2_parts.append(f"{C['orange']}{temp}{C['reset']}")

    # 天气
    if weather:
        l2_parts.append(f"{C['purple']}{weather['temp']} {weather['condition']}{C['reset']}")

    # Git
    if git:
        branch = git['branch']
        if git['dirty']:
            branch += f"*{git['dirty_count']}"
        l2_parts.append(f"{C['blue']}{branch}{C['reset']}")

    # 时间
    l2_parts.append(f"{C['cyan']}{t['time']}{C['reset']}")

    lines.append(" ".join(l2_parts))

    # ── Line 3: 随机语录 ──
    q = get_hitokoto()
    if q.get("q_text", ""):
        rainbow = [196, 202, 208, 214, 220, 226, 118, 82, 46, 51, 63, 129, 200]
        chars = list(q["q_text"])
        colored = []
        for i, ch in enumerate(chars):
            colored.append(f"\033[38;5;{rainbow[i % len(rainbow)]}m{ch}\033[0m")
        quote_str = "".join(colored)
        author = q.get("q_who") or q.get("q_from") or ""
        if author:
            lines.append(f"{quote_str}  {C['white']}——{author}{C['reset']}")
        else:
            lines.append(quote_str)

    print("\n".join(lines))


def cmd_status(args):
    """Legacy single-line plain status."""
    load = get_cpu_load()
    mem = get_memory()
    disk = get_disk()
    weather = get_weather()
    git = get_git_status()
    cpu_temp = get_cpu_temp()
    git_suffix = f" | {git['branch']}" if git else ""
    weather_str = f" | {weather['temp']} {weather['condition']}" if weather else ""
    print(f"CPU: {load['1min']} | MEM: {mem['used_mb']}M/{mem['total_mb']}M ({mem['used_pct']}%) | "
          f"DISK: {disk['used_gb']}G/{disk['total_gb']}G ({disk['used_pct']}%) | "
          f"TEMP: {cpu_temp}{weather_str}{git_suffix}")


def cmd_dashboard(args):
    """Full JSON dashboard."""
    data = {
        "system": get_system_info(),
        "cpu": get_cpu_load(),
        "cpu_temp": get_cpu_temp(),
        "memory": get_memory(),
        "disk": get_disk(),
        "time": get_time(),
        "weather": get_weather(),
        "git": get_git_status(),
        "model": get_claude_model(),
        "hitokoto": get_hitokoto(),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_quote(args):
    """Display a random quote with rainbow colors."""
    q = get_hitokoto()
    if q.get("q_text", ""):
        rainbow = [196, 202, 208, 214, 220, 226, 118, 82, 46, 51, 63, 129, 200]
        chars = list(q["q_text"])
        colored = []
        for i, ch in enumerate(chars):
            color = rainbow[i % len(rainbow)]
            colored.append(f"\033[38;5;{color}m{ch}\033[0m")
        quote_str = "".join(colored)
        author = q.get("q_who") or q.get("q_from") or ""
        if author:
            print(f"{quote_str}  {C['white']}——{author}{C['reset']}")
        else:
            print(quote_str)
    else:
        print(f"{C['dim']}暂未获取到语录{C['reset']}")


def cmd_show(args):
    """Show full HUD preview (3-line style)."""
    sysinfo = get_system_info()
    load = get_cpu_load()
    mem = get_memory()
    disk = get_disk()
    weather = get_weather()
    git = get_git_status()
    t = get_time()
    temp = get_cpu_temp()
    ctx = get_context_info()
    model = ctx.get("model", "") if ctx else ""
    if not model:
        model = get_claude_model()

    os_str = f"{sysinfo['os']} {sysinfo['kernel']}"
    model_str = f"{C['cyan']}{model}{C['reset']}"
    os_c = f"{C['pink']}{os_str}{C['reset']}"

    print(f"\n{C['bold']}{C['cyan']}┌─ HUD 状态面板 ─────────────────────────────{C['reset']}")
    header = f"{C['cyan']}│{C['reset']} {model_str}"
    if ctx:
        header += f"  {ctx['color']}{ctx['bar']} {ctx['pct']}%{C['reset']}"
    header += f"  {os_c}"
    print(header)

    cpu_str = f"{C['pink']}CPU {load['1min']}{C['reset']}"
    mem_pct = mem['used_pct']
    mc = C['red'] if mem_pct > 90 else C['yellow'] if mem_pct > 75 else C['green']
    mem_str = f"{mc}内存 {mem['used_mb']}M/{mem['total_mb']}M{C['reset']}"
    disk_str = f"{C['yellow']}磁盘 {disk['used_gb']}G/{disk['total_gb']}G{C['reset']}"
    temp_str = f"{C['orange']}{temp}{C['reset']}" if temp != "N/A" else ""
    weather_str = f"{C['purple']}{weather['temp']} {weather['condition']}{C['reset']}" if weather else ""
    git_str = f"{C['blue']}[{git['branch']}]{C['reset']}" if git else ""
    time_str = f"{C['cyan']}{t['time']}{C['reset']}"
    line1 = " ".join(filter(None, [cpu_str, mem_str, disk_str, temp_str, weather_str, git_str, time_str]))
    print(f"{C['cyan']}│{C['reset']} {line1}")

    # Quote
    q = get_hitokoto()
    if q.get("q_text", ""):
        chars = list(q["q_text"])
        rainbow = [196, 202, 208, 214, 220, 226, 118, 82, 46, 51, 63, 129, 200]
        colored = []
        for i, ch in enumerate(chars):
            colored.append(f"\033[38;5;{rainbow[i % len(rainbow)]}m{ch}\033[0m")
        print(f"{C['cyan']}│{C['reset']} " + "".join(colored))
        author = q.get("q_who") or q.get("q_from") or ""
        if author:
            print(f"{C['cyan']}│{C['reset']}   {C['white']}——{author}{C['reset']}")

    print(f"{C['cyan']}└───────────────────────────────────────────{C['reset']}\n")


def cmd_weather(args):
    weather = get_weather()
    if weather:
        print(json.dumps(weather, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps({"error": "无法获取天气信息"}, ensure_ascii=False))
        sys.exit(1)


def cmd_git(args):
    path = args[0] if args else None
    git = get_git_status(path)
    if git:
        print(json.dumps(git, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps({"error": f"不是 git 仓库: {path or os.getcwd()}"}, ensure_ascii=False))
        sys.exit(1)


def cmd_configure(args):
    print(json.dumps({
        "refresh_interval_seconds": 120,
        "show_weather": True,
        "show_git": True,
        "show_quote": True,
        "weather_location": "",
        "components": ["cpu", "memory", "disk", "temp", "weather", "git", "time", "quote"],
    }, ensure_ascii=False, indent=2))


def print_help():
    print(f"""用法: hud_collector.py <子命令>

子命令:
  line              单行彩色状态输出（用于 statusLine）
  show              三行 HUD 面板预览（带颜色）
  dashboard         完整 JSON 仪表盘
  status            一行纯文本状态
  quote             随机中文语录（彩虹色）
  monitor           系统监控信息
  weather           天气信息
  git [路径]        指定目录的 Git 状态
  configure         配置 HUD

示例:
  hud_collector.py line
  hud_collector.py show
  hud_collector.py quote""")


def main():
    subcommands = {
        "line": cmd_line,
        "show": cmd_show,
        "dashboard": cmd_dashboard,
        "status": cmd_status,
        "quote": cmd_quote,
        "monitor": cmd_dashboard,
        "weather": cmd_weather,
        "git": cmd_git,
        "configure": cmd_configure,
        "help": lambda _: print_help(),
        "--help": lambda _: print_help(),
        "-h": lambda _: print_help(),
    }
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "show"
    if cmd in subcommands:
        subcommands[cmd](sys.argv[2:])
    else:
        print(f"未知子命令: {cmd}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
