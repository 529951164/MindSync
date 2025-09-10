/**
 * MindSync Cursor Extension
 * 自动同步Markdown文档到Mac备忘录
 */

const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * 获取MindSync工具路径
 */
function getMindSyncPath() {
    const config = vscode.workspace.getConfiguration('mindsync');
    const configuredPath = config.get('toolPath');
    
    if (configuredPath && fs.existsSync(configuredPath)) {
        return configuredPath;
    }
    
    // 自动检测：查找工作区中的main.py
    if (vscode.workspace.workspaceFolders) {
        for (const folder of vscode.workspace.workspaceFolders) {
            const mainPyPath = path.join(folder.uri.fsPath, 'main.py');
            if (fs.existsSync(mainPyPath)) {
                return folder.uri.fsPath;
            }
        }
    }
    
    return null;
}

/**
 * 执行MindSync命令
 */
function executeMindSyncCommand(command, callback) {
    const mindSyncPath = getMindSyncPath();
    if (!mindSyncPath) {
        callback(new Error('未找到MindSync工具。请在设置中配置工具路径。'));
        return;
    }
    
    const fullCommand = `cd "${mindSyncPath}" && python3 main.py ${command}`;
    
    exec(fullCommand, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
            callback(error);
            return;
        }
        
        try {
            // 尝试解析JSON输出
            const result = JSON.parse(stdout);
            callback(null, result);
        } catch (parseError) {
            // 如果不是JSON，返回原始输出
            callback(null, { status: 'success', message: stdout.trim() });
        }
    });
}

/**
 * 同步单个文件
 */
function syncFile(filePath, showNotification = true) {
    const config = vscode.workspace.getConfiguration('mindsync');
    
    if (!config.get('autoSync') && showNotification) {
        vscode.window.showInformationMessage('自动同步已禁用');
        return;
    }
    
    const command = `api sync --file "${filePath}" --format json`;
    
    executeMindSyncCommand(command, (error, result) => {
        if (error) {
            console.error('同步失败:', error);
            if (showNotification && config.get('showNotifications')) {
                vscode.window.showErrorMessage(`同步失败: ${error.message}`);
            }
            return;
        }
        
        if (result.status === 'success') {
            if (showNotification && config.get('showNotifications')) {
                vscode.window.showInformationMessage('✅ 已同步到备忘录');
            }
        } else {
            if (showNotification && config.get('showNotifications')) {
                vscode.window.showErrorMessage(`同步失败: ${result.message}`);
            }
        }
    });
}

/**
 * 检查系统状态
 */
function checkStatus() {
    const command = 'api status --format json';
    
    executeMindSyncCommand(command, (error, result) => {
        if (error) {
            vscode.window.showErrorMessage(`状态检查失败: ${error.message}`);
            return;
        }
        
        if (result.status === 'success') {
            const message = `MindSync状态正常\\n版本: ${result.version}\\n配置: ${result.config_valid ? '有效' : '无效'}\\n备忘录: ${result.notes_accessible ? '可访问' : '不可访问'}`;
            vscode.window.showInformationMessage(message);
        } else {
            vscode.window.showErrorMessage(`状态检查失败: ${result.message}`);
        }
    });
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 扩展激活函数
 */
function activate(context) {
    console.log('MindSync扩展已激活');
    
    const config = vscode.workspace.getConfiguration('mindsync');
    
    // 创建防抖的同步函数
    const debouncedSync = debounce((filePath) => {
        syncFile(filePath, false);
    }, config.get('syncDelay') || 1000);
    
    // 监听文件保存事件
    const saveListener = vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === 'markdown' && config.get('autoSync')) {
            debouncedSync(document.fileName);
        }
    });
    
    // 注册命令
    const syncCurrentCommand = vscode.commands.registerCommand('mindsync.syncCurrent', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.languageId === 'markdown') {
            if (editor.document.isDirty) {
                vscode.window.showWarningMessage('请先保存文件再同步');
                return;
            }
            syncFile(editor.document.fileName, true);
        } else {
            vscode.window.showInformationMessage('请打开Markdown文件');
        }
    });
    
    const toggleAutoSyncCommand = vscode.commands.registerCommand('mindsync.toggleAutoSync', () => {
        const currentValue = config.get('autoSync');
        config.update('autoSync', !currentValue, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`自动同步已${!currentValue ? '启用' : '禁用'}`);
    });
    
    const checkStatusCommand = vscode.commands.registerCommand('mindsync.checkStatus', checkStatus);
    
    const syncAllCommand = vscode.commands.registerCommand('mindsync.syncAll', () => {
        vscode.window.showInformationMessage('批量同步功能开发中...');
    });
    
    // 状态栏项目
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(sync) MindSync';
    statusBarItem.tooltip = 'MindSync: 点击检查状态';
    statusBarItem.command = 'mindsync.checkStatus';
    statusBarItem.show();
    
    // 添加到订阅列表
    context.subscriptions.push(
        saveListener,
        syncCurrentCommand,
        toggleAutoSyncCommand,
        checkStatusCommand,
        syncAllCommand,
        statusBarItem
    );
    
    // 显示激活消息
    if (config.get('showNotifications')) {
        vscode.window.showInformationMessage('🧠 MindSync扩展已启用');
    }
}

/**
 * 扩展停用函数
 */
function deactivate() {
    console.log('MindSync扩展已停用');
}

module.exports = {
    activate,
    deactivate
};