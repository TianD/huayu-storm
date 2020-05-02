const { app, BrowserWindow, Menu, Tray } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

const server = require('http').createServer();
const io = require('socket.io')(server);
io.on('connection', client => {
  client.on('finish_job', data=> {
    client.broadcast.emit('refresh_ui', data)
  })
  client.on('disconnect', () => { /* … */ });
});
server.listen(8001);

let win;
let engineProc = null;
let zmqProc = null;

let tray = null;

function createSubProc() {
  // start zmq server
  let zmqcmd = path.resolve(__dirname, '../engine/run_zmq.bat')
  zmqProc = spawn(zmqcmd)
  if (zmqProc != null) {
    console.log('queue process success')
  }

  // start flask server
  let pycmd = path.resolve(__dirname, '../engine/run_engine.bat')
  engineProc = spawn(pycmd)
  if (engineProc != null) {
    console.log('python process success')
  }
}

function exitSubProc() {
  engineProc.kill()
  zmqProc.kill()
  engineProc = null
  zmqProc = null
}

function createWindow() {
  // 创建浏览器窗口
  win = new BrowserWindow({
    width: 1280,
    height: 720,
    webPreferences: {
      nodeIntegration: true,
    },
    icon: path.join(__dirname, './favicon.ico')
  })

  // 并且为你的应用加载index.html
  // win.loadFile('./build/index.html')
  win.loadURL('http://localhost:3000/');

  // 打开开发者工具
  win.webContents.openDevTools()

  Menu.setApplicationMenu(null)

}

// function clearData () {
//   win.send('clearData', {success:true, message: 'hello'})
// }

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// 部分 API 在 ready 事件触发后才能使用。
app.whenReady().then(createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // 在 macOS 上，除非用户用 Cmd + Q 确定地退出，
  // 否则绝大部分应用及其菜单栏会保持激活。
  // if (process.platform !== 'darwin') {
  //   app.quit()
  // }
})

app.on('activate', () => {
  // 在macOS上，当单击dock图标并且没有其他窗口打开时，
  // 通常在应用程序中重新创建一个窗口。
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('will-quit', exitSubProc)

app.on('ready', () => {
  tray = new Tray(path.join(__dirname, './favicon.ico'))
  const contextMenu = Menu.buildFromTemplate([
    // {label: 'Clear', click: clearData},
    { label: 'Main', click: createWindow },
    { label: 'Quit', click: app.quit }
  ])
  tray.setToolTip('Huayu-Storm.')
  tray.setContextMenu(contextMenu)
  createSubProc()
})