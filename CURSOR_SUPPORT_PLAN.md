# 🎯 MindSync多编辑器支持开发计划

## 📋 项目目标

**让MindSync完美支持Claude Code和Cursor，实现真正的多编辑器AI编程文档同步**

- ✅ Claude Code Hook (已有) 
- 🚀 Cursor扩展 (新增)
- 🔧 统一配置和管理
- 📖 完整文档和一键安装

## 🏗️ 技术架构

```
┌─────────── 编辑器层 ───────────┐
│  Claude Code Hook  │  Cursor   │
│     (重构)         │ Extension │
└────────────────────┼──────────┘
                     │
┌─────────── API层 ────────────┐
│    Enhanced CLI API          │
│  python main.py api <cmd>    │
└────────────────────┼──────────┘
                     │
┌─────────── 核心层 ──────────┐
│  Sync Engine (不变)         │
│  Apple Bridge (不变)        │
│  Config Manager (增强)      │
└──────────────────────────────┘
```

## 📅 开发计划 (总计6小时)

### 🔥 第一阶段：CLI API增强 (1.5小时)

**目标**: 为Python CLI添加JSON API模式，便于其他工具调用

**任务清单**:
- [ ] 1.1 新增`api`子命令支持 (30分钟)
- [ ] 1.2 添加JSON格式输出 (30分钟) 
- [ ] 1.3 增强错误处理和状态返回 (30分钟)

**验收标准**:
```bash
# 成功调用示例
python main.py api sync --file test.md --format json
# 返回: {"status": "success", "message": "同步完成", "file": "test.md"}

python main.py api status --format json  
# 返回: {"version": "1.3.0", "config_valid": true, "notes_accessible": true}
```

### ⚡ 第二阶段：Cursor扩展开发 (2小时)

**目标**: 创建轻量级VSCode扩展，支持Cursor/VSCode

**任务清单**:
- [ ] 2.1 初始化VSCode扩展项目结构 (20分钟)
- [ ] 2.2 实现文件保存监听和过滤逻辑 (30分钟)
- [ ] 2.3 集成Python CLI API调用 (40分钟)
- [ ] 2.4 添加状态栏显示和通知 (20分钟)
- [ ] 2.5 实现配置界面和快捷命令 (10分钟)

**验收标准**:
- ✅ 保存.md文件时自动触发同步
- ✅ 状态栏显示同步状态
- ✅ 命令面板包含MindSync命令
- ✅ 设置界面可配置自动同步开关

### 🔧 第三阶段：配置统一管理 (1小时)

**目标**: 统一配置文件，支持多编辑器设置

**任务清单**:
- [ ] 3.1 扩展config.json结构支持编辑器配置 (20分钟)
- [ ] 3.2 更新配置加载和验证逻辑 (20分钟)
- [ ] 3.3 添加编辑器特定配置命令 (20分钟)

**配置结构设计**:
```json
{
  "sync_rules": { /* 现有配置保持不变 */ },
  "notes_config": { /* 现有配置保持不变 */ },
  "editors": {
    "claude_code": {
      "enabled": true,
      "auto_sync": true,
      "hook_installed": false
    },
    "cursor": {
      "enabled": true,
      "auto_sync": true,
      "extension_installed": false
    }
  },
  "api": {
    "output_format": "json",
    "quiet_mode": false
  }
}
```

### 🚀 第四阶段：自动化安装 (1小时)

**目标**: 创建智能安装脚本，自动检测和配置

**任务清单**:
- [ ] 4.1 增强deploy.sh支持Cursor扩展安装 (30分钟)
- [ ] 4.2 添加编辑器检测和引导逻辑 (20分钟)
- [ ] 4.3 创建VSCode扩展打包和安装脚本 (10分钟)

**安装流程设计**:
```bash
./deploy.sh
# 1. 检测系统环境
# 2. 初始化Python配置  
# 3. 检测Claude Code -> 安装Hook
# 4. 检测Cursor/VSCode -> 安装扩展
# 5. 运行端到端测试
# 6. 输出使用指南
```

### 📖 第五阶段：文档更新 (30分钟)

**任务清单**:
- [ ] 5.1 更新README添加Cursor支持说明 (15分钟)
- [ ] 5.2 创建Cursor扩展用户指南 (10分钟)  
- [ ] 5.3 更新开发者文档 (5分钟)

### 🧪 第六阶段：测试验证 (1小时)

**任务清单**:
- [ ] 6.1 单元测试：CLI API功能 (20分钟)
- [ ] 6.2 集成测试：Cursor扩展 (20分钟)
- [ ] 6.3 端到端测试：多编辑器场景 (20分钟)

## 📁 项目文件结构

```
MindSync/
├── main.py                    # 增强API接口
├── config.json               # 统一配置文件  
├── deploy.sh                 # 增强安装脚本
├── cursor-extension/         # 新增：Cursor扩展
│   ├── package.json         
│   ├── extension.js         
│   ├── README.md            
│   └── icon.png             
├── tests/                    # 新增：测试目录
│   ├── test_api.py          
│   └── test_cursor.js       
└── docs/                     # 文档目录
    ├── CURSOR_GUIDE.md      # 新增
    └── DEVELOPER.md         # 新增
```

## 🎯 关键技术实现

### CLI API设计
```python
# main.py 新增API模式
@click.group()
def api():
    """API模式，便于其他工具调用"""
    pass

@api.command()
@click.option('--file', required=True)
@click.option('--format', default='text', type=click.Choice(['text', 'json']))
def sync(file, format):
    """同步单个文件到备忘录"""
    result = sync_file_to_notes(file)
    if format == 'json':
        click.echo(json.dumps(result))
```

### Cursor扩展核心
```javascript
// extension.js 核心逻辑
const vscode = require('vscode');
const { exec } = require('child_process');

function syncFile(filePath) {
    const config = vscode.workspace.getConfiguration('mindsync');
    if (!config.get('autoSync')) return;
    
    exec(`python3 main.py api sync --file "${filePath}" --format json`, 
         (error, stdout) => {
            const result = JSON.parse(stdout);
            if (result.status === 'success') {
                vscode.window.showInformationMessage('✅ 同步成功');
            }
         });
}
```

## ✅ 验收标准

### 功能验收
- [ ] Claude Code用户编辑MD文件时自动同步
- [ ] Cursor用户编辑MD文件时自动同步  
- [ ] 两个编辑器可以同时使用，互不冲突
- [ ] 统一的配置文件和管理命令
- [ ] 一键安装脚本支持所有场景

### 性能验收
- [ ] API调用延迟 < 100ms
- [ ] 扩展启动时间 < 1s
- [ ] 文件同步完成时间 < 2s

### 用户体验验收
- [ ] 安装过程全自动化，无需手动配置
- [ ] 错误信息清晰，有明确的解决建议
- [ ] 文档完整，新用户可以独立完成安装

## 🚀 开始执行

**当前状态**: 已创建cursor-support分支，准备开始第一阶段开发

**下一步**: 开始增强Python CLI API接口

---

*更新时间: 2024-09-09*  
*负责人: Claude*  
*预计完成时间: 6小时*