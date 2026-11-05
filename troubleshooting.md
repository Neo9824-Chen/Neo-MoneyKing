# 部署与运行排障

按症状定位，先做最小验证再改动文件。所有路径均指**用户安装目录**里的副本，不要改技能模板。

## 1. 安装 / 启动

| 症状 | 原因与处理 |
| --- | --- |
| `npm start` 一闪而过或没有窗口，控制台像在跑 Node | 环境变量 `ELECTRON_RUN_AS_NODE=1` 让 Electron 以 Node 模式启动。启动脚本已清除它；手动运行时先 `set "ELECTRON_RUN_AS_NODE="`（Windows）或 `unset ELECTRON_RUN_AS_NODE`（macOS/Linux） |
| `npm install` 卡在下载 Electron | Electron 二进制走独立镜像：`ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/`。npm 包源用 `--registry=https://registry.npmmirror.com`，失败会自动回退官方源。换网络或手动设置代理后重试 |
| 提示 `'npm' 不是内部或外部命令` | 未安装 Node.js。装 Node.js LTS 后重开终端（请先安装 Node.js LTS：https://nodejs.org 后重试） |
| `node_modules/electron` 存在但启动报缺少 exe | 安装被中断，删除 `node_modules/electron` 后重新执行 `npm install`；不要删整个 `node_modules` |
| macOS 提示应用已损坏 / 无法打开 | 未签名的 Electron 被 Gatekeeper 拦截：`xattr -cr ./node_modules`，或在「系统设置 → 隐私与安全性」点「仍要打开」 |

最小验证：`node -v && npm -v`；`npm start` 直接观察控制台输出；`deploy.py --check` 看 `electron_installed`。

## 2. 窗口 / 摆件

| 症状 | 原因与处理 |
| --- | --- |
| 摆件有白色/黑色底板，不透明 | `main.js` 的 `createOrnament()` 必须保留 `frame:false`、`transparent:true`、`hasShadow:false`、`backgroundColor:"#00000000"`。Linux 无合成器时可能需给 `app.commandLine.appendSwitch("disable-gpu")` 后再测 |
| 摆件右侧出现白色竖条 | 滚动条。`body.ornament` 的 `overflow:hidden` 不能删 |
| 悬停不出现「放大」、点击无反应 | 不要给摆件加 `-webkit-app-region: drag`：拖拽区会把 hover/click 交给系统，事件全部失效。项目用 `mousedown/mousemove` 上报 `screenX/screenY` 经 IPC 手动移动窗口 |
| 拖动摆件后自动弹回主窗口 | 设计如此：位移 < 4px 视为单击恢复。按住并移动超过 4px 即正常拖动 |
| 缩小后财富数翻倍 | 主窗口与摆件窗共用 `nmgdq_auto` + `visibilitychange` 同步（隐藏窗口暂停自动敲击）。不要移除这段同步，也不要同时开两个主窗口 |

## 3. 声音

| 症状 | 原因与处理 |
| --- | --- |
| 完全没有声音 | 浏览器/Electron 的自动播放策略要求先有一次用户交互：点一下财神再听。仍无声则在 DevTools 里执行 `new Audio(KNOCK_INLINE).play()` 验证内嵌 mp3 是否可播（能播说明是外部文件加载问题） |
| 换成自己的 `muyu_knock.mp3` 后还是原声 | 文件名必须完全一致、与 `index.html` 同处一层；编辑器/浏览器有缓存，重启应用或 Ctrl+R 强制刷新。若文件被删，页面会静默回退到内嵌默认音效，看起来就像「替换没生效」 |
| 替换音效后静音 | 用 ffmpeg 的 `afade` 滤镜处理音频可能输出全静音；改用「ffmpeg 只裁剪 + Python 手工淡出/增益」，编码后解码回读校验峰值非 0。文件损坏时 `error` 事件会回退内嵌音效，不会一直没声 |
| 缩小后还在响 | 设置里「缩小后背景音效（摆件）」控制摆件/迷你模式的自动敲击；普通窗口由「背景音效（自动敲击）」控制。手动敲击音效常开，不受开关影响 |
| 音量调了没变化 | 音量走 `sound.vol`（0-100），播放前 `knockAudio.volume = vol/100`；滑块 `input` 与开关 `change` 事件即时生效，点「取消」会回滚到打开弹窗时的快照 |

## 4. 数据与设置

- localStorage 键：`nmgdq_merit`（今日财富）、`nmgdq_week`（本周累计，周一清零）、`nmgdq_times`（上下班时间）、`nmgdq_auto`（自动赚钱开关）、`nmgdq_sound`（`{vol, autoOn, miniAutoOn}`）。
- Electron 用户数据目录：Windows `%APPDATA%\迎财神`，macOS `~/Library/Application Support/迎财神`，Linux `~/.config/迎财神`；窗口位置尺寸存在 `window-state.json`。
- 财富归零通常是因为清了浏览器数据或 Electron 用户数据；重装应用本身不会清零。

## 5. 文件与编码

- `start.cmd` 内容必须保持纯 ASCII + CRLF；中文路径/中文命令在部分 Windows 控制台会乱码，安装目录也建议用 ASCII 路径。
- **路径必须可移植**：`index.html` 里素材一律写 `caishen.png`、`muyu_knock.mp3` 这类同目录相对路径，`main.js` 用 `path.join(__dirname, "index.html")`，启动脚本用 `%~dp0` / `dirname "$0"`。模板里出现写死的盘符路径，换台电脑必然白图/无声——打包前用 grep 扫一遍盘符与用户主目录硬编码。
- 素材与 `index.html` **平铺在同一层**：3 张 PNG + 1 个 mp3，没有子目录。文件缺失时页面自动回退内嵌 base64（图片由 `data-inline` + `INLINE_IMG` 探测，音效由 `error` 事件切 `KNOCK_INLINE`），所以只拷 `index.html` 也能跑，但替换素材就无效了。
- 检查外部依赖用 `grep -o 'https\?://[^" ]*' index.html`，只允许出现 `http://www.w3.org/2000/svg` 这类 SVG 命名空间常量；`data:` 内嵌不算外链。
- 改动 HTML 时保留原有行尾（CRLF）；用会把整个文件行尾统一成 LF 的编辑器保存，会让 diff 变成全文件差异。
- 定制请先复制到安装目录再改；改完无需构建，Electron 直接 `loadFile`，重启或 Ctrl+R 生效。
