// const { app, BrowserWindow } = require('electron');
// const path = require('path');

// function createWindow() {
//   const win = new BrowserWindow({
//     width: 1200,
//     height: 800,
//     webPreferences: {
//       nodeIntegration: true,
//       contextIsolation: false
//     }
//   });

//   win.loadFile('index.html');
// }

// app.whenReady().then(() => {
//   createWindow();

//   app.on('activate', () => {
//     if (BrowserWindow.getAllWindows().length === 0) {
//       createWindow();
//     }
//   });
// });

// app.on('window-all-closed', () => {
//   if (process.platform !== 'darwin') {
//     app.quit();
//   }
// });


const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// Path to the todo.txt file
const todoFilePath = path.join(app.getPath('userData'), 'todo.txt');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            // !!! ВАЖНО: Разрешаване на Node.js интеграция в renderer процеса
            // Това е необходимо, за да може `require('electron')` да работи в index.html
            nodeIntegration: true,
            contextIsolation: false, // За по-лесно тестване, но по-малко сигурно. За production, използвайте preload script
        }
    });

    mainWindow.loadFile('index.html');

    // Отворете DevTools за отстраняване на грешки
    // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// --- IPC Main Handlers за TODO списъка ---

// Слушане за заявка за зареждане на TODO списъка от renderer
ipcMain.on('request-todo-list', (event) => {
    fs.readFile(todoFilePath, 'utf8', (err, data) => {
        let tasks = [];
        if (!err && data) {
            try {
                // Всеки ред е отделна задача, формат: "текст на задачата|true/false"
                tasks = data.split('\n')
                            .filter(line => line.trim() !== '') // Премахване на празни редове
                            .map(line => {
                                const parts = line.split('|');
                                return {
                                    text: parts[0],
                                    completed: parts[1] === 'true'
                                };
                            });
            } catch (parseError) {
                console.error("Error parsing todo.txt:", parseError);
                tasks = []; // Reset on error
            }
        }
        event.reply('load-todo-list', tasks); // Изпращане на задачите обратно към renderer
    });
});

// Слушане за запазване на TODO списъка от renderer
ipcMain.on('save-todo-list', (event, tasks) => {
    const dataToWrite = tasks.map(task => `${task.text}|${task.completed}`).join('\n');
    fs.writeFile(todoFilePath, dataToWrite, 'utf8', (err) => {
        if (err) {
            console.error("Error writing to todo.txt:", err);
        } else {
            console.log("TODO list saved successfully.");
        }
    });
});