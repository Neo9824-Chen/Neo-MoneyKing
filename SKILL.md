---
name: neo-moneyking
description: 一键部署「迎财神 / Neo-MoneyKing」完整桌面摆件版（Electron 无边框透明摆件）。当用户说「部署迎财神」「安装 Neo-MoneyKing」「装个财神桌面摆件」「把财神放到我电脑上」「一键安装摆件」「把这个摆件复制到本机」，或要求启动、排障、个性化调整已安装的迎财神摆件时，应使用本技能。本仓库通过 GitHub 分享，网友 clone 后由豆包 PC 客户端或 WorkBuddy 安装本目录作为技能。
agent_created: true
display_name: Neo-MoneyKing
author: Neo
contact: Neo9824
version: 2.0.0
---

# Neo-MoneyKing · 迎财神桌面摆件

创作者 **Neo** · 联系 **Neo9824** · 仓库/技能标识 `neo-moneyking`。

## 概述

把「迎财神」**完整桌面摆件版**部署到用户自己的电脑：主窗口是上班倒计时 + 自动敲木鱼攒财富的小应用，点「缩小」后变成可拖动、无边框、背景透明的财神桌面摆件；悬停出现「放大」，原地单击摆件也可恢复。

**分享方式**：本目录即一个 Git 仓库，放在 GitHub 上分享。网友把仓库 clone / 下载后，让豆包（PC 客户端）或 WorkBuddy 把本目录当作「技能」安装，对话里说一句「部署迎财神」即可自动调用 `deploy.py` 把完整版装到本机。

**零子目录平铺结构**：所有文件平铺在仓库根目录，没有任何子目录；素材用同目录相对路径引用（`caishen.png`、`muyu_knock.mp3` 等），`main.js` 用 `path.join(__dirname, "index.html")`，启动脚本用 `%~dp0` / `dirname "$0"`，部署脚本用 `__file__` 推导。模板里**没有任何写死的本机绝对路径**，装到任何电脑、任何用户目录都能跑。

每份素材在页面里仍保留一份 base64 内嵌数据兜底：素材文件缺失（例如只拷走了 `index.html`）时自动回退，照样有图有声。不依赖任何图床、CDN 或账号。

## 触发场景

- 部署 / 安装 / 复制迎财神、Neo-MoneyKing、财神桌面摆件到本机
- 启动、重启、验证已部署的摆件
- 部署失败排障（Electron 装不上、窗口不透明、没有声音、拖拽失效）
- 个性化调整（窗口尺寸、上下班时间、音量、图片、音效、署名）

## 资源（全部在仓库根目录，无子目录）

| 文件 | 用途 |
| --- | --- |
| `index.html` | 应用主页面，素材用同目录相对路径引用 |
| `caishen.png` / `monk.png` / `mallet.png` | 3 张贴纸，可直接替换同名文件 |
| `muyu_knock.mp3` | 真实木鱼单次敲击音效，可直接替换同名文件 |
| `main.js` / `preload.js` / `package.json` | Electron 双窗口（主窗口 + 透明摆件窗） |
| `start.cmd` / `start.sh` | 一键启动（首次自动装 Electron） |
| `deploy.py` | 一键部署：复制文件 →（可选）安装 Electron →（可选）启动 → 输出 JSON 校验结果 |
| `README.md` | 面向网友：通过 GitHub + 豆包 / WorkBuddy 部署、手动启动、替换素材 |
| `troubleshooting.md` | 部署与运行排障：环境、镜像、透明窗、静音、拖拽 |
| `customization.md` | 改窗口尺寸、时间/音量默认值、替换贴纸音效、localStorage 键 |

## 工作流

### 第 1 步：确定安装目录

默认 `~/Documents/Neo-MoneyKing`（纯 ASCII 路径，避开中文路径在 Windows 命令行里的编码问题）。用户明确指定目录时以用户为准；用户没说时直接用默认值，不要停下来追问。

### 第 2 步：执行部署

在仓库目录下执行（脚本路径是仓库内相对路径；`--target` 填网友自己电脑上的目录，由脚本按 `Path.home()` 或参数解析，不要写死任何盘符）：

```bash
# 完整版（首次会下载 Electron，约 100MB）
python3 deploy.py --target "<目录>" --install

# 部署并立即启动（仅当用户要求「直接打开/启动」时加 --launch）
python3 deploy.py --target "<目录>" --install --launch

# 校验已部署目录
python3 deploy.py --check --target "<目录>"
```

`--install` 优先走 npmmirror 镜像，失败自动回退官方源；脚本会清除 `ELECTRON_RUN_AS_NODE` 并设置 `ELECTRON_MIRROR`。若返回 `install.ok=false`，把 `message` 转成自然语言告知用户，并读 `troubleshooting.md` 处理，不要反复重试同一条命令。

### 第 3 步：验证与交付

用 `--check` 确认 `files_ok=true`、`offline_self_contained=true`、`no_absolute_path=true`、`electron_installed=true`。`missing` 里若列出某个 png/mp3，说明素材没带全（页面会自动回退内嵌数据，但网友无法替换贴纸），应重新部署补齐。向用户报告：安装目录、启动方式（Windows 双击 `start.cmd`，macOS/Linux 终端 `./start.sh`）、「缩小 → 摆件 → 悬停放大/单击恢复」的操作方式，以及数据存在本机、清除用户数据会归零。

## 关键约束

- **绝不在模板里写死本机绝对路径**（如 `D:\...`、`C:\Users\...`、`/Users/neo/...`）：所有文件引用一律用相对路径或 `__dirname` / `__file__` / `%~dp0` 推导，否则换台电脑就找不到素材。
- 贴纸与音效与 `index.html` 同处一层，用 `caishen.png` 这类相对路径引用，并保留内嵌 base64 兜底；不要改回外链，也不要改成绝对路径（见 `customization.md`）。
- 部署脚本复制素材时只补缺失文件，不覆盖网友已替换过的贴纸/音效；不要改成整目录覆盖。
- 不要修改仓库根目录里的模板来适配某次部署；需要定制时，先复制到目标目录再改目标目录里的文件。
- 启动 GUI 属于显式动作：只在用户要求启动、或用户已明确要求「部署并打开」时加 `--launch`。
- 不要删除用户安装目录里的 `node_modules` 或 Electron 用户数据；财富数与设置存在本机，重装应用本身不会清零，清除用户数据才会。
- 部署失败或症状不明时，先读 `troubleshooting.md`，再按其中的定位顺序处理。
