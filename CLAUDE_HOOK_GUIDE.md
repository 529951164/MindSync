# 🪝 MindSync x Claude Code Hook集成指南

> 实现保存即同步的完美工作流！

## 🎯 Hook集成概述

Claude Hook让MindSync与Claude Code深度集成，实现：
- **自动检测** - 监控Markdown文件的保存事件
- **智能延迟** - 避免频繁同步，等待编辑完成
- **无感操作** - 后台自动同步，不打断工作流
- **状态反馈** - 同步结果实时显示

## 🚀 快速集成 (3分钟)

### Step 1: 验证Hook环境
```bash
# 测试基础功能
python3 claude_hook.py test

# 期望输出:
# ✅ Hook测试通过
# ✅ 配置文件加载成功  
# ✅ AppleScript桥接正常
```

### Step 2: 安装Hook到Claude Code
```bash
# 标准安装
python3 claude_hook.py install --name mindsync

# 自定义Hook名称
python3 claude_hook.py install --name my_markdown_sync

# 期望输出:
# ✅ Hook已安装到Claude Code
# 🔗 Hook名称: mindsync
# 📍 配置路径: ~/.claude/hooks/mindsync.json
```

### Step 3: 验证安装
```bash
# 查看已安装的Hook
ls ~/.claude/hooks/

# 测试Hook触发
python3 claude_hook.py test --file your_test.md
```

## ⚙️ Hook配置详解

### 基础配置 (config.json)
```json
{
  "claude_hook": {
    "enabled": true,                    // 启用Hook功能
    "watch_patterns": ["*.md"],         // 监控的文件模式
    "delay_seconds": 2,                 // 同步延迟时间
    "auto_sync_on_save": true,          // 保存时自动同步
    "batch_sync": false,                // 批量同步模式
    "max_file_size_mb": 10              // Hook文件大小限制
  }
}
```

### 高级配置选项
```json
{
  "claude_hook": {
    // 文件过滤
    "watch_patterns": [
      "*.md",                           // 所有Markdown文件
      "docs/**/*.md",                   // docs目录下的MD文件
      "!**/draft/**/*.md"               // 排除draft目录
    ],
    
    // 同步策略
    "sync_strategy": {
      "delay_seconds": 2,               // 延迟同步避免频繁触发
      "debounce_interval": 5,           // 防抖间隔
      "max_retries": 3                  // 失败重试次数
    },
    
    // 通知设置
    "notifications": {
      "success": true,                  // 成功通知
      "errors": true,                   // 错误通知
      "show_progress": false            // 显示进度
    }
  }
}
```

## 🔧 Claude Code Hook配置

### 生成的Hook配置文件
```json
{
  "name": "MindSync Auto Sync",
  "description": "自动同步Markdown文档到Apple Notes",
  "trigger": {
    "type": "file_save",
    "patterns": ["*.md"]
  },
  "command": {
    "type": "shell",
    "command": "python3 /path/to/MacNoteTools/claude_hook.py sync \"$FILE_PATH\"",
    "working_directory": "/path/to/MacNoteTools",
    "timeout": 30
  },
  "options": {
    "async": true,
    "debounce": 2000,
    "show_output": false
  }
}
```

### Claude Code中的Hook设置
1. **打开Claude Code设置**
   - 按 `Cmd + ,` 打开设置
   - 导航到 "Hooks" 部分

2. **查看已安装Hook**
   ```
   Hooks > Installed Hooks > mindsync
   ```

3. **自定义Hook行为**
   - 调整触发条件
   - 修改文件模式匹配
   - 设置输出显示选项

## 🎮 Hook操作命令

### 基础操作
```bash
# 安装Hook
python3 claude_hook.py install --name hook_name

# 卸载Hook
python3 claude_hook.py uninstall --name hook_name

# 列出所有Hook
python3 claude_hook.py list

# 测试Hook
python3 claude_hook.py test [--file filename]
```

### 手动同步
```bash
# 单文件同步
python3 claude_hook.py sync document.md

# 批量同步
python3 claude_hook.py batch file1.md file2.md file3.md

# 项目同步
python3 claude_hook.py project /path/to/project
```

## 🔍 工作流程示例

### 典型Claude工作流
```
1. 在Claude Code中打开项目
2. 创建或编辑Markdown文档
3. 保存文档 (Cmd+S)
   ↓
4. Hook自动触发
5. MarkSync处理文档
6. 同步到Apple Notes
7. 手机上即时查看 ✨
```

### Hook触发日志
```
[2024-01-15 14:30:22] INFO - Hook触发: README.md
[2024-01-15 14:30:22] INFO - 项目识别: MonroeDiner_Dev  
[2024-01-15 14:30:23] INFO - 格式转换完成
[2024-01-15 14:30:24] INFO - 同步成功: Claude/MonroeDiner_Dev
[2024-01-15 14:30:24] INFO - 备忘录标题: [MonroeDiner_Dev] README
```

## 🛠️ 故障排除

### 常见问题

#### Hook不触发
```bash
# 检查Hook状态
python3 claude_hook.py status

# 检查Claude Code Hook配置
cat ~/.claude/hooks/mindsync.json

# 重新安装Hook
python3 claude_hook.py uninstall --name mindsync
python3 claude_hook.py install --name mindsync
```

#### 同步失败
```bash
# 查看详细日志
tail -f logs/sync.log

# 手动测试同步
python3 claude_hook.py test --file problematic_file.md

# 检查文件权限
ls -la problematic_file.md
```

#### 权限问题
```bash
# 检查AppleScript权限
osascript -e 'tell application "Notes" to get name of account 1'

# 重新授权终端访问备忘录
# 系统偏好设置 → 安全与隐私 → 隐私 → 完整磁盘访问权限
```

### 性能优化

#### 减少Hook触发频率
```json
{
  "claude_hook": {
    "delay_seconds": 3,               // 增加延迟
    "debounce_interval": 8,           // 增加防抖时间
    "watch_patterns": [               // 精确匹配文件
      "README.md",
      "docs/**/*.md"
    ]
  }
}
```

#### 批量同步模式
```json
{
  "claude_hook": {
    "batch_sync": true,               // 启用批量模式
    "batch_interval": 10,             // 批量间隔(秒)
    "batch_size": 5                   // 每批最大文件数
  }
}
```

## 🔐 安全考虑

### 数据安全
- **本地处理** - 所有数据处理都在本地完成
- **无网络传输** - 不会上传文档到外部服务器
- **权限最小化** - 只申请必要的系统权限
- **配置加密** - 敏感配置信息可选加密存储

### 隐私保护
- **文件内容不记录** - 日志中不包含文档内容
- **路径脱敏** - 日志中的路径信息做脱敏处理
- **用户可控** - 用户可以完全控制同步的文档和目标

## 🚀 高级应用

### 自定义Hook脚本
```bash
#!/bin/bash
# custom_marksync_hook.sh

FILE_PATH="$1"
PROJECT_ROOT="$2"

# 自定义预处理
echo "Processing: $FILE_PATH"

# 调用MarkSync
python3 /path/to/MacNoteTools/claude_hook.py sync "$FILE_PATH"

# 自定义后处理
echo "Sync completed for: $(basename $FILE_PATH)"
```

### 集成CI/CD流程
```yaml
# .github/workflows/docs-sync.yml
name: Documentation Sync
on:
  push:
    paths: ['docs/**/*.md']
    
jobs:
  sync-docs:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Sync Documentation
        run: |
          python3 claude_hook.py batch docs/**/*.md
```

## 🎉 成功使用MindSync Hook

现在你已经掌握了MindSync与Claude Code的完美集成！

**享受保存即同步的丝滑体验吧！** 🌟

---
**遇到问题？** 查看完整的故障排除指南或提交Issue获得帮助！