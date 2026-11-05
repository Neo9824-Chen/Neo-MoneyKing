const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("widgetAPI", {
  // 切换「始终置顶」，返回切换后的状态
  toggleOnTop: () => ipcRenderer.invoke("toggle-on-top"),
  // 进入桌面摆件模式：无边框透明小窗，只显示财神（主窗口隐藏）
  enterOrnament: () => ipcRenderer.invoke("enter-ornament"),
  // 退出摆件模式：关闭小窗，恢复主窗口
  exitOrnament: () => ipcRenderer.invoke("exit-ornament"),
  // 手动拖动摆件窗口（渲染进程上报鼠标屏幕坐标）
  startOrnamentDrag: () => ipcRenderer.send("ornament-drag-start"),
  moveOrnamentDrag: (x, y) => ipcRenderer.send("ornament-drag-move", x, y),
  // 当前是否在桌面版窗口里
  isDesktop: true
});
