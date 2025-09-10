# MindSync - Cursor/VSCode扩展

🧠 **让AI编程更高效的备忘录同步神器**

自动同步Markdown文档到Mac备忘录，支持Cursor、VSCode等编辑器。

## ✨ 功能特色

- 🔄 **自动同步** - 保存Markdown文件时自动同步到Mac备忘录
- ⚡ **快速响应** - 1秒内完成同步，无感知体验
- 🎯 **智能过滤** - 仅同步Markdown文件，忽略临时文件
- 📊 **状态监控** - 实时显示同步状态和系统健康度
- ⌨️ **快捷操作** - Cmd+Shift+M快速同步当前文档

## 🚀 快速开始

### 前置要求

- macOS系统
- Python 3.7+
- MindSync核心工具已安装

### 安装扩展

1. 将此目录复制到VSCode/Cursor扩展目录
2. 重启编辑器
3. 扩展会自动检测MindSync工具路径

### 配置设置

```json
{
  "mindsync.autoSync": true,           // 启用自动同步
  "mindsync.toolPath": "",             // 工具路径（留空自动检测）
  "mindsync.syncDelay": 1000,          // 同步延迟（毫秒）
  "mindsync.showNotifications": true   // 显示通知
}
```

## 📋 使用方法

### 自动同步
- 编辑并保存任何`.md`文件
- 扩展会在1秒后自动同步到备忘录
- 状态栏显示同步状态

### 手动同步
- 使用快捷键: `Cmd+Shift+M` (Mac) 或 `Ctrl+Shift+M` (Windows)
- 或者在命令面板中搜索"MindSync"
- 右键菜单中的"同步当前文档"

### 状态检查
- 点击状态栏的"MindSync"按钮
- 或运行"MindSync: 检查状态"命令
- 查看版本、配置和备忘录访问状态

## 🔧 命令列表

| 命令 | 快捷键 | 说明 |
|------|--------|------|
| `mindsync.syncCurrent` | Cmd+Shift+M | 同步当前Markdown文档 |
| `mindsync.toggleAutoSync` | - | 切换自动同步开关 |
| `mindsync.checkStatus` | - | 检查系统状态 |
| `mindsync.syncAll` | - | 同步所有文档（开发中）|

## 🛠️ 故障排除

### 扩展无法启动
1. 检查是否安装了MindSync核心工具
2. 确认Python 3.7+已正确安装
3. 查看VSCode/Cursor开发者工具的控制台错误

### 同步失败
1. 运行"MindSync: 检查状态"检查配置
2. 确认备忘录应用有正确权限
3. 手动在设置中配置MindSync工具路径

### 自动同步不工作
1. 检查`mindsync.autoSync`设置是否为true
2. 确认文件确实是Markdown格式(.md扩展名)
3. 查看是否有错误通知

## 📞 支持

- GitHub: https://github.com/529951164/MindSync
- 问题报告: https://github.com/529951164/MindSync/issues
- 完整文档: https://github.com/529951164/MindSync#readme

## 📄 许可证

MIT License - 完全免费开源使用