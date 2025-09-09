# ⚡ MindSync - 超级简洁使用指南

> 3分钟上手，1行命令搞定Markdown同步！

## 🎯 核心功能

**MindSync** 让你的Markdown文档自动同步到Apple备忘录，格式完美，智能分类！

```
本地MD文档 → 一键同步 → Apple备忘录完美显示 → 手机随时查看
```

## 🚀 快速开始

### 1️⃣ 环境检查 (30秒)
```bash
# 确保你有这些：
✅ macOS系统
✅ Python 3.7+
✅ 已登录iCloud的备忘录应用
```

### 2️⃣ 首次同步 (1分钟)
```bash
# 进入工具目录
cd /Volumes/Q/MiniGame/MacNoteTools

# 同步你的第一个文档
python3 main.py sync-file your_document.md
```

就是这么简单！🎉

## 📱 神奇效果

### 自动格式转换
```
你写的Markdown          →    Apple备忘录显示
# 大标题                →    【大标题】  
## 小标题               →    ■ 小标题
**重要内容**           →    【重要内容】
`代码片段`             →    「代码片段」  
- 列表项               →    • 列表项
> 重要引用             →    💬 重要引用
```

### 智能文件夹分类
```
Unity项目文档    → Claude/MonroeDiner
Node.js项目文档  → Claude/WebProject  
Python项目文档   → Claude/DataAnalysis
其他文档         → Claude/Other
```

## 🎮 常用命令

```bash
# 同步单个文件
python3 main.py sync-file README.md

# 同步整个文件夹
python3 main.py sync-folder ./docs

# 查看工具信息
python3 main.py info

# 查看配置
python3 main.py config --show
```

## ⚡ Claude Hook集成 - 自动化神器

### 什么是Claude Hook？
当你在Claude Code中保存Markdown文件时，MindSync自动帮你同步到备忘录！

### 3步安装Hook

#### 步骤1：测试Hook功能
```bash
# 测试基本功能
python3 claude_hook.py test

# 测试指定文件
python3 claude_hook.py test --file your_doc.md
```

#### 步骤2：安装Hook
```bash
# 安装到Claude Code
python3 claude_hook.py install --name mindsync

# 自定义名称
python3 claude_hook.py install --name my_sync
```

#### 步骤3：享受自动同步
```
在Claude Code中编辑MD文档 → 保存文件 → 自动同步到备忘录 ✨
```

### Hook配置优化
编辑 `config.json` 中的Claude Hook设置：
```json
{
  "claude_hook": {
    "enabled": true,
    "watch_patterns": ["*.md"],       // 监控的文件类型  
    "delay_seconds": 2,               // 同步延迟
    "auto_sync_on_save": true         // 保存时自动同步
  }
}
```

## 🛠️ 个性化配置

### 基础配置 (config.json)
```json
{
  "sync_rules": {
    "auto_update": true,              // 自动更新已存在的备忘录
    "max_file_size_mb": 50,           // 最大文件大小限制
    "excluded_patterns": [            // 忽略的文件
      "*.tmp.md", "*draft*", ".*"
    ]
  },
  "notes_config": {
    "account": "iCloud",              // 备忘录账户
    "default_folder": "Notes"         // 默认文件夹
  }
}
```

### 项目文件夹映射
```json
{
  "folder_mappings": {
    "work": "工作笔记",
    "personal": "个人笔记", 
    "tech": "技术文档",
    "claude": "Claude文档"
  }
}
```

## 🔥 高级用法

### 批量同步
```bash
# 同步多个文件
python3 main.py sync-files doc1.md doc2.md doc3.md

# 同步今天修改的文件
python3 main.py sync-folder . --only-today

# 同步最近2小时修改的文件  
python3 main.py sync-folder . --modified-since 2
```

### 同步模式
```bash
# 更新模式（默认）- 更新已存在的备忘录
python3 main.py sync-file doc.md --mode update

# 仅创建模式 - 只创建新备忘录，不更新已存在的
python3 main.py sync-file doc.md --mode create_only

# 强制创建模式 - 总是创建新备忘录
python3 main.py sync-file doc.md --mode force_create
```

## 🚨 常见问题1秒解决

### Q: 备忘录权限问题？
**A:** 系统偏好设置 → 安全与隐私 → 隐私 → 给终端添加备忘录权限

### Q: 文档没有换行？
**A:** 已修复！确保使用最新版本

### Q: 项目文件夹识别错误？
**A:** 手动配置 `folder_mappings` 或确保项目目录有标识文件

### Q: Hook不工作？
**A:** 检查Claude Code设置，确保Hook已正确安装

## 💡 专业小贴士

1. **使用相对路径** - 在项目根目录运行命令
2. **定期更新** - 新版本持续优化格式转换
3. **备份配置** - 个性化配置记得备份
4. **项目标识** - 在项目根目录放置package.json等标识文件

## 🎊 开始享受

现在你已经掌握了MindSync的精髓！去创建美丽的文档，让它们自动同步到你的Apple备忘录吧！

**一个命令，连接两个世界** 🌉

---
**需要帮助？** 查看完整的README.md或提交Issue！