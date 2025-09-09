# 🧠 MindSync - Mac备忘录同步工具

一个强大的Markdown文档同步工具，可以将本地MD文档自动同步到macOS备忘录中，支持智能项目识别、文件夹映射和Claude Code集成。

## ✨ 特性

- 🤖 **智能项目识别**: 自动识别Unity、Node.js、Python等项目类型
- 📁 **智能文件夹映射**: 根据项目自动创建和映射备忘录文件夹（Claude/ProjectName）
- 🔄 **多种同步模式**: 更新现有、仅创建新的、强制创建等
- 📝 **Markdown格式转换**: 将MD格式转换为苹果备忘录友好格式
- 🎯 **Claude专用**: 针对Claude Code工作流程优化
- 🔧 **灵活配置**: 支持多种同步规则和过滤条件
- 📊 **详细日志**: 完整的同步日志和统计信息
- ✅ **完美显示**: 支持换行符、标题、列表等格式正确显示

## 🏗️ 项目结构

```
MacNoteTools/
├── config.json              # 主配置文件
├── main.py                   # 命令行主入口
├── sync_engine.py            # 核心同步引擎
├── apple_bridge.py           # AppleScript桥接
├── claude_hook.py            # Claude Hook集成
├── markdown_converter.py     # Markdown格式转换器
├── test_sync.py              # 功能测试脚本
├── utils.py                  # 工具函数
├── rules/                    # 同步规则模块
│   ├── __init__.py
│   ├── base_rule.py          # 规则基类
│   ├── basic_rules.py        # 基础规则
│   ├── time_rules.py         # 时间相关规则
│   ├── content_rules.py      # 内容相关规则
│   └── claude_rules.py       # Claude专用规则
└── logs/                     # 日志文件夹
```

## 🚀 快速开始

### 1. 环境要求

- macOS 系统
- Python 3.7+
- 已登录iCloud账户的备忘录应用

### 2. 配置初始化

```bash
# 进入工具目录
cd /Volumes/Q/MiniGame/MacNoteTools

# 初始化配置文件
python main.py config --init

# 验证配置
python main.py config --validate
```

### 3. 基本使用

```bash
# 同步单个文件
python main.py sync-file document.md

# 同步整个文件夹
python main.py sync-folder ~/Documents/Projects --recursive

# 查看备忘录信息
python main.py info

# 试运行（不实际同步）
python main.py sync-file document.md --dry-run
```

### 4. Claude项目自动映射

工具会自动识别项目类型并映射到相应的Claude文件夹：

- **Unity项目** → `Claude/项目名`
- **Node.js项目** → `Claude/项目名`
- **Python项目** → `Claude/项目名`
- **其他文档** → `Claude/Other`

## 📋 详细使用说明

### 命令行接口

#### 同步命令

```bash
# 同步单个文件
python main.py sync-file <文件路径> [选项]

# 同步文件夹
python main.py sync-folder <文件夹路径> [选项]

# 批量同步多个文件
python main.py sync-files file1.md file2.md [选项]
```

**常用选项:**
- `--only-today`: 仅同步今天修改的文件
- `--modified-since HOURS`: 仅同步N小时内修改的文件
- `--mode {update,create_only,force_create}`: 同步模式
- `--max-size MB`: 文件大小限制
- `--dry-run`: 试运行模式

#### 配置管理

```bash
# 显示当前配置
python main.py config --show

# 验证配置文件
python main.py config --validate

# 重新初始化配置
python main.py config --init --force
```

#### 信息查看

```bash
# 查看备忘录和规则信息
python main.py info
```

### Claude Hook集成

#### 1. 测试Hook功能

```bash
# 测试基本功能
python claude_hook.py test

# 测试指定文件
python claude_hook.py test --file document.md
```

#### 2. 安装Hook到Claude Code

```bash
# 安装Hook
python claude_hook.py install --name md_sync

# 自定义Hook名称
python claude_hook.py install --name my_custom_sync
```

#### 3. 手动触发同步

```bash
# 同步单个文件
python claude_hook.py sync document.md

# 批量同步
python claude_hook.py batch file1.md file2.md
```

## ⚙️ 配置说明

### 基础配置

```json
{
  "sync_rules": {
    "auto_update": true,              # 自动更新已存在的备忘录
    "backup_before_update": false,    # 更新前备份
    "max_file_size_mb": 50,           # 最大文件大小限制
    "encoding": "utf-8",              # 文件编码
    "excluded_patterns": [            # 排除的文件模式
      "*.tmp.md",
      "*draft*",
      ".*"
    ],
    "folder_mappings": {              # 文件夹映射
      "work": "工作笔记",
      "tech": "技术文档",
      "claude": "Claude文档",
      "default": "Notes"
    }
  }
}
```

### 备忘录配置

```json
{
  "notes_config": {
    "account": "iCloud",              # 备忘录账户
    "default_folder": "Notes",        # 默认文件夹
    "title_prefix": "",               # 标题前缀
    "title_suffix": "",               # 标题后缀
    "add_timestamp": false,           # 添加时间戳
    "add_source_path": true           # 添加源文件路径
  }
}
```

### Claude Hook配置

```json
{
  "claude_hook": {
    "enabled": true,                  # 启用Hook
    "watch_patterns": ["*.md"],       # 监控的文件模式
    "delay_seconds": 2,               # 同步延迟
    "auto_sync_on_save": true         # 保存时自动同步
  }
}
```

## 🎯 Claude专用功能

### 1. 智能项目映射

工具会自动分析文件路径，识别项目类型：

- 检查常见项目文件（如 `package.json`, `Unity项目文件` 等）
- 分析目录结构特征
- 生成清理后的项目名称作为文件夹名

### 2. 文档标题格式

- **有项目信息**: `[项目名] 文档名`
- **无项目信息**: `[文档] 文档名`

### 3. 格式转换

自动将Markdown格式转换为备忘录友好格式：

```
原始Markdown → 备忘录格式
# 标题        → 【标题】
## 二级标题   → ■ 二级标题  
### 三级标题  → ▶ 三级标题
**粗体**     → 【粗体】
*斜体*       → 《斜体》
`代码`       → 「代码」
- 列表       → • 列表
1. 有序列表  → ① 有序列表
> 引用       → 💬 引用
```

### 4. 内容格式

文档在备忘录中的显示格式：

```
文件名

【转换后的内容】
```

## 🧪 功能测试

### 自动化测试

```bash
# 运行完整功能测试
python test_sync.py
```

测试内容包括：
- Unity项目文档识别
- 普通文档处理
- 中文文件名支持
- 文件夹自动创建
- 内容格式化

### 手动验证

1. 检查Mac备忘录应用
2. 确认Claude文件夹结构
3. 验证文档内容和格式
4. 测试更新和创建功能

## 🔧 故障排除

### 常见问题

#### 1. AppleScript权限问题

**症状**: 无法访问备忘录应用

**解决方案**:
- 在 系统偏好设置 > 安全性与隐私 > 隐私 中添加终端的备忘录访问权限
- 重启终端应用

#### 2. 字符编码问题

**症状**: 中文字符显示异常

**解决方案**:
- 确保文件使用UTF-8编码保存
- 检查配置文件中的 `encoding` 设置

#### 3. 文件夹创建失败

**症状**: 无法创建Claude子文件夹

**解决方案**:
- 手动在备忘录中创建 `Claude` 根文件夹
- 确认iCloud同步正常工作

#### 4. 项目识别不准确

**症状**: 项目名称识别错误或为空

**解决方案**:
- 检查项目目录是否包含标识文件
- 手动配置文件夹映射规则
- 使用自定义标题前缀

#### 5. 换行符显示问题

**症状**: 文本在备忘录中连续显示，没有换行

**解决方案**:
- 最新版本已修复此问题，使用HTML `<br>` 标签确保正确换行
- 确保使用最新的 `markdown_converter.py`
- 重新同步文档以应用修复

### 调试模式

```bash
# 启用详细输出
python main.py sync-file document.md --verbose

# 查看同步日志
tail -f logs/sync.log

# 试运行模式调试
python main.py sync-folder ~/Documents --dry-run
```

## 🔄 更新和维护

### 更新配置

```bash
# 备份当前配置
cp config.json config.json.backup

# 重新初始化（会覆盖现有配置）
python main.py config --init --force

# 恢复部分设置后验证
python main.py config --validate
```

### 清理日志

```bash
# 手动清理日志
rm -rf logs/*

# 配置文件中设置日志轮转
# "max_log_size_mb": 10,
# "backup_count": 5
```

### 卸载

```bash
# 停止所有Hook
# 删除Claude Code中的Hook配置

# 删除工具文件
rm -rf /Volumes/Q/MiniGame/MacNoteTools

# 可选：清理备忘录中的Claude文件夹
```

## 📞 支持和反馈

如果遇到问题或有改进建议：

1. 检查上述故障排除部分
2. 运行 `python test_sync.py` 进行完整测试
3. 查看 `logs/sync.log` 获取详细错误信息
4. 记录重现步骤和错误信息

## 📄 许可证

此工具为个人使用项目，请根据实际需要进行修改和分发。

---

## 🆕 最新更新

### v1.2 (当前版本)
- ✅ 修复换行符显示问题，使用HTML `<br>` 标签确保正确换行
- ✅ 完善Markdown格式转换，支持标题、加粗、斜体、代码、列表、引用
- ✅ 优化内容格式，简化为文件名+转换内容的清晰结构
- ✅ 修复嵌套文件夹创建逻辑，确保Claude/ProjectName结构正确

### v1.1
- ✅ 实现智能项目识别和文件夹映射
- ✅ 支持Claude Hook集成
- ✅ 添加多种同步规则和模式

### v1.0
- ✅ 基础Markdown到Apple Notes同步功能
- ✅ AppleScript桥接实现

---

🎉 **享受完美的Markdown同步体验！**