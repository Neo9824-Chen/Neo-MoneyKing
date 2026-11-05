# 个性化调整指南

所有改动都在**安装目录**里进行，技能根目录里的模板保持不动。安装目录与技能根目录都是**平铺结构**：所有文件同一层，没有子目录（所有文件同一层，无子目录）。改完不需要构建：Electron 直接加载 `index.html`，重启应用或 Ctrl+R 生效。

## 1. 窗口与摆件（main.js）

| 项目 | 位置 | 默认值 |
| --- | --- | --- |
| 主窗口尺寸 / 最小尺寸 | `createWindow()` 的 `width/height/minWidth/minHeight` | 420×800 / 320×520 |
| 主窗口默认置顶 | `alwaysOnTop: st.onTop !== false` | 开 |
| 摆件窗口尺寸 | `createOrnament()` 的 `width/height` | 185×175 |
| 摆件初始位置 | `createOrnament()` 的 `x/y` | 贴主窗口右上角 |
| 透明无边框 | `frame:false` / `transparent:true` / `hasShadow:false` | 不可删，见排障文档 |
| 应用名 / 任务栏标题 | `app.setName("迎财神")`、两个窗口的 `title` | 迎财神 |
| 窗口位置记忆 | `window-state.json`（Electron userData） | 自动保存 |

调整摆件尺寸时同步检查 `index.html` 中 `body.ornament .mini .mini-art { width: 100% }` 和 SVG `viewBox="0 0 119 112"`，让财神比例不被拉伸。

## 2. 页面与交互（index.html）

- 顶部 `.topbar`：logo、标题、「缩小 / 设置」按钮。
- 插画 `.scene`：SVG 财神 + 木槌；木槌动画 `@keyframes malletTap`，敲击落点在 24% 关键帧；`tap()` 里 260ms 延时让计数/音效/飘字与落点同步。
- 设置弹窗 `#timeModal`：`inStart/inEnd`（上下班时间）、`inAutoSound`（普通窗口自动敲击音效）、`inMiniSound`（缩小后摆件音效）、`inVolume`（0-100）。
- 声音逻辑：`KNOCK_SRC` 是同目录相对路径 `muyu_knock.mp3`，`KNOCK_INLINE` 是内嵌 mp3 的 data URI 兜底；加载失败时 `error` 事件自动切回内嵌并继续可用。`knockSound()` 优先播放 `knockAudio`，WebAudio 合成音只作最后的兜底；`sound = {vol, autoOn, miniAutoOn}` 存在 `nmgdq_sound`。
- 敲击门控：`!fromAuto || (inMini ? sound.miniAutoOn : sound.autoOn)`；`inMini` 由 `body.minimode` / `body.ornament` 判断；手动敲击永远发声。
- 署名行：`<div class="credit">Neo-MoneyKing · 创作者 Neo · 联系 Neo9824</div>`，样式 `.credit`。保留或按需求替换，不要删除创作者标识而不说明。
- 默认上下班时间：`getTimes()` 返回 `{s:"09:00", e:"18:00"}`；进度条与倒计时支持跨零点。

## 3. 替换贴纸 / 音效（相对路径，不用改 HTML）

素材是**与 `index.html` 同层的独立文件**（无子目录），页面全部用同目录相对路径引用，直接覆盖同名文件即可，改完重启应用或 Ctrl+R 生效：

| 文件（相对 `index.html`） | 作用 | 建议尺寸 |
| --- | --- | --- |
| `caishen.png` | 顶部 logo | 约 96×90，透明底 |
| `monk.png` | 财神主体（主场景与摆件共用） | 约 380×357，透明底 |
| `mallet.png` | 木槌（主场景与摆件共用） | 约 40×56，透明底 |
| `muyu_knock.mp3` | 单次木鱼敲击 | 0.5–1s，非静音 |

```bash
# 例：换成自己的财神图（保持 PNG 透明通道，文件名不变）
cp 我的财神.png ~/Documents/Neo-MoneyKing/monk.png
```

**三条约束**

1. **只能用相对路径**，别把 `src`/`href`/`KNOCK_SRC` 改成 `D:\...`、`C:\Users\...`、`/Users/...` 之类的绝对路径或 `file://` 绝对路径——换台电脑路径就失效了。也别改回 http 外链，否则离线白图。
2. 文件名与目录结构保持不变，替换内容即可；要增删文件才需要同步改 `index.html` 的 `data-inline` 标记和 `INLINE_IMG`。
3. 每个素材在 `index.html` 里都保留一份内嵌 base64 兜底：图片由末尾脚本用 `new Image()` 探测，失败自动把 `src`/`href` 换回 `INLINE_IMG[key]`；音效由 `knockAudio` 的 `error` 事件切回 `KNOCK_INLINE`。所以删掉这些 png/mp3 也能跑，只是显示的是默认素材，**你替换的文件不再生效**。

若要连兜底素材一起换，用 Python 生成 data URI 后替换 `INLINE_IMG` / `KNOCK_INLINE`：

```python
import base64
uri = "data:image/png;base64," + base64.b64encode(open("new.png","rb").read()).decode("ascii")
```

音效从长录音剪单次敲击时，ffmpeg 只做裁剪，淡出/增益用 Python 手工处理并回读验证非静音（见 `troubleshooting.md`）。

## 4. 默认值与数据

| 键 | 内容 |
| --- | --- |
| `nmgdq_merit` | 今日财富数 |
| `nmgdq_week` | 本周累计，按自然周（周一）清零 |
| `nmgdq_times` | 上下班时间 `{s,e}` |
| `nmgdq_auto` | 自动赚钱开关（跨窗口同步，隐藏窗口暂停） |
| `nmgdq_sound` | `{vol:80, autoOn:true, miniAutoOn:true}` |

改默认值时同时改 `let sound = ...`、`getTimes()` 与弹窗 `value` 属性，避免 UI 与实际值不一致。旧数据缺少 `miniAutoOn` 字段时按 `!== false` 兜底为开启。

## 5. 重新打包分发

把安装目录里改好的全部文件（`index.html`、`main.js`、`preload.js`、`package.json`、`start.cmd`、`start.sh`、`README.md`、4 个 png/mp3 素材）复制回**仓库根目录**，保持平铺、不要新建任何子目录。确认 `deploy.py --check` 的 `offline_self_contained=true`、`no_absolute_path=true`、`missing=[]`，再提交到 GitHub 重新分发。打包自检：路径层级 ≤ 1、无反斜杠、含 4 个素材文件；用 `grep` 扫一遍盘符路径确认没有写死本机位置。
