const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

// 加载同目录的自包含网页（图片与音效已内嵌，完全离线可用）
const HTML = path.join(__dirname, "index.html");

app.setName("迎财神");
const STATE = () => path.join(app.getPath("userData"), "window-state.json");

function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE(), "utf8")); } catch (e) { return null; }
}

let win = null;

function createWindow() {
  const st = loadState() || {};
  win = new BrowserWindow({
    width: st.width || 420,
    height: st.height || 800,
    x: st.x,
    y: st.y,
    minWidth: 320,
    minHeight: 520,
    alwaysOnTop: st.onTop !== false, // 默认浮在桌面最上层
    autoHideMenuBar: true,
    title: "迎财神",
    backgroundColor: "#f2f4f8",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.setMenuBarVisibility(false);
  win.loadFile(HTML);

  const save = () => {
    if (!win || win.isDestroyed()) return;
    const b = win.getBounds();
    try {
      fs.writeFileSync(STATE(), JSON.stringify({ ...b, onTop: win.isAlwaysOnTop() }));
    } catch (e) {}
  };
  win.on("resize", save);
  win.on("move", save);
  win.on("close", save);
}

ipcMain.handle("toggle-on-top", () => {
  const next = !win.isAlwaysOnTop();
  win.setAlwaysOnTop(next);
  return next;
});

// ===== 桌面摆件模式：无边框透明小窗，只显示敲木鱼的财神 =====
let ornamentWin = null;

function createOrnament() {
  if (ornamentWin && !ornamentWin.isDestroyed()) return;
  const b = win && !win.isDestroyed() ? win.getBounds() : null;
  ornamentWin = new BrowserWindow({
    width: 185,
    height: 175,
    x: b ? Math.max(0, b.x + b.width - 185) : undefined,
    y: b ? b.y : undefined,
    frame: false,          // 无边框：没有标题栏
    transparent: true,     // 背景透明：只剩财神本体
    hasShadow: false,
    resizable: false,
    alwaysOnTop: true,
    title: "迎财神",
    backgroundColor: "#00000000",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  ornamentWin.setMenuBarVisibility(false);
  ornamentWin.loadFile(HTML, { search: "mode=ornament" });
  ornamentWin.on("closed", () => { ornamentWin = null; });
}

ipcMain.handle("enter-ornament", () => {
  if (win && !win.isDestroyed()) win.hide(); // 隐藏主窗口（进程保留，状态不丢）
  createOrnament();
  return true;
});

ipcMain.handle("exit-ornament", () => {
  if (ornamentWin && !ornamentWin.isDestroyed()) ornamentWin.close();
  if (win && !win.isDestroyed()) { win.show(); win.focus(); }
  return true;
});

// 手动拖动摆件窗口：渲染进程上报鼠标屏幕坐标，主进程按位移移动窗口
let dragOffset = null;
ipcMain.on("ornament-drag-start", () => { dragOffset = null; });
ipcMain.on("ornament-drag-move", (e, sx, sy) => {
  const w = ornamentWin;
  if (!w || w.isDestroyed()) return;
  const b = w.getBounds();
  if (!dragOffset) dragOffset = { dx: sx - b.x, dy: sy - b.y };
  w.setPosition(sx - dragOffset.dx, sy - dragOffset.dy);
});

app.whenReady().then(() => {
  // 调试用：CAISHEN_ORNAMENT=1 时直接以摆件模式启动
  if (process.env.CAISHEN_ORNAMENT === "1") { createOrnament(); return; }
  createWindow();
});
app.on("window-all-closed", () => app.quit());
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
