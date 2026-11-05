#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Neo-MoneyKing 一键部署脚本（仅用标准库）。

把同目录下的「迎财神」完整桌面摆件版（Electron 无边框透明摆件）复制到目标目录，
按需安装 Electron、启动。

分享方式：本目录即 GitHub 仓库内容。网友把本仓库 clone / 下载后，
让豆包（PC 客户端）或 WorkBuddy 把本目录当作技能安装，对话一句「部署迎财神」即可调用本脚本。
所有路径都由 __file__ 推导或使用相对路径，没有任何写死的本机绝对路径，
因此装到任何电脑、任何用户目录都能正常部署。

用法：
    python3 deploy.py --target <目录> [--install] [--launch] [--check]
    python3 deploy.py --check --target <目录>          # 只校验已部署的目录

默认目标目录：~/Documents/Neo-MoneyKing
输出：单行 JSON（stdout），便于上层 Agent 直接解析。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

APP_FILES = ["index.html", "main.js", "preload.js", "package.json",
             "start.cmd", "start.sh", "README.md"]
# 贴纸与音效：index.html 里全部用同目录相对路径引用，可自由替换同名文件。
# 文件缺失时页面会自动回退到内嵌 base64，所以只拷 index.html 也能独立运行。
ASSET_FILES = ["caishen.png", "monk.png", "mallet.png", "muyu_knock.mp3"]
APP_SRC = Path(__file__).resolve().parent  # 所有模板文件与脚本同处仓库根目录
NPM_MIRROR = "https://registry.npmmirror.com"
ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"


def default_target():
    return Path.home() / "Documents" / "Neo-MoneyKing"


def emit(obj, code=0):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def copy_app(target):
    if not APP_SRC.is_dir():
        emit({"ok": False, "error": "仓库根目录缺失", "path": str(APP_SRC)}, 2)
    target.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in APP_FILES:
        src = APP_SRC / name
        if not src.exists():
            emit({"ok": False, "error": "模板文件缺失: " + name}, 2)
        shutil.copy2(src, target / name)
        copied.append(name)
    # 素材与应用文件平铺在同一层；只补缺失，不覆盖用户已替换过的贴纸/音效
    for name in ASSET_FILES:
        src = APP_SRC / name
        if not src.exists():
            emit({"ok": False, "error": "模板素材缺失: " + name}, 2)
        dst = target / name
        if not dst.exists():
            shutil.copy2(src, dst)
            copied.append(name)
    return copied


def npm_available():
    return shutil.which("npm") is not None


def install(target):
    if not npm_available():
        return False, "未检测到 npm；请先安装 Node.js LTS (https://nodejs.org)"
    env = dict(os.environ)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    env["ELECTRON_MIRROR"] = ELECTRON_MIRROR
    env["npm_config_registry"] = NPM_MIRROR
    cmds = [["npm", "install", "--registry=" + NPM_MIRROR, "--no-fund", "--no-audit"],
            ["npm", "install", "--no-fund", "--no-audit"]]  # 镜像失败时回退官方源
    last = ""
    for cmd in cmds:
        try:
            r = subprocess.run(cmd, cwd=str(target), env=env, shell=(os.name == "nt"),
                               capture_output=True, text=True, timeout=900)
            last = (r.stdout or "")[-600:] + (r.stderr or "")[-600:]
            if r.returncode == 0:
                return True, "Electron 安装完成"
        except Exception as e:  # noqa: BLE001
            last = str(e)
    return False, "npm install 失败: " + last.strip()


def launch(target):
    env = dict(os.environ)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/c", "start", "", str(target / "start.cmd")],
                             cwd=str(target), env=env)
        else:
            subprocess.Popen(["bash", str(target / "start.sh")],
                             cwd=str(target), env=env, start_new_session=True)
        return True, "已启动"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def check(target):
    missing = [f for f in APP_FILES if not (target / f).exists()]
    missing += [f for f in ASSET_FILES if not (target / f).exists()]
    offline = False
    no_absolute_path = False
    if (target / "index.html").exists():
        html = (target / "index.html").read_text(encoding="utf-8", errors="ignore")
        # SVG 命名空间是标准常量，不算外部依赖；其余 http(s) 链接才说明还依赖网络
        text = re.sub(r'https?://www\.w3\.org/[^\s"\')>]*', '', html)
        offline = re.search(r'https?://', text) is None
        # 剔除 URL 和内嵌 base64 后再找写死的绝对路径，避免把 https:// 误判成盘符
        clean = re.sub(r'https?://[^\s"\')>]*', '', html)
        clean = re.sub(r'data:[A-Za-z0-9+/=,;.-]+', '', clean)
        no_absolute_path = re.search(
            r'(?:[A-Za-z]:[\\/]|\\\\[\w.-]+[\\/]|/Users/|/home/[\w.-]+/)',
            clean) is None
    return {
        "target": str(target),
        "files_ok": not missing,
        "missing": missing,
        "offline_self_contained": offline,
        "no_absolute_path": no_absolute_path,
        "node_npm": npm_available(),
        "electron_installed": (target / "node_modules" / "electron").is_dir(),
        "launcher": str(target / ("start.cmd" if os.name == "nt" else "start.sh")),
        "index_html": str(target / "index.html"),
    }


def main():
    ap = argparse.ArgumentParser(description="部署 Neo-MoneyKing 迎财神桌面摆件")
    ap.add_argument("--target", default=str(default_target()), help="安装目录")
    ap.add_argument("--install", action="store_true", help="安装 Electron 依赖")
    ap.add_argument("--launch", action="store_true", help="启动桌面版")
    ap.add_argument("--check", action="store_true", help="只校验，不复制")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    if args.check:
        emit({"ok": True, "action": "check", **check(target)})

    copied = copy_app(target)
    result = {"ok": True, "target": str(target), "copied": copied}

    if args.install:
        ok, msg = install(target)
        result["install"] = {"ok": ok, "message": msg}
        result["ok"] = ok
    if args.launch:
        ok, msg = launch(target)
        result["launch"] = {"ok": ok, "message": msg}

    result.update({k: v for k, v in check(target).items() if k != "target"})
    emit(result, 0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
