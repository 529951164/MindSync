# 🎮 Unity项目文档同步指南

> 一键同步Unity项目的所有Markdown文档到Apple备忘录

## 🚀 快速使用

### 基本语法
```bash
python3 sync_unity_project.py <Unity项目路径>
```

### 使用示例
```bash
# 同步gamebox_develop项目
python3 sync_unity_project.py /Volumes/Q/MiniGame/gbt-2021/gamebox_develop

# 同步MonroeDiner项目  
python3 sync_unity_project.py /Volumes/Q/MiniGame/MonroeDiner_Dev

# 同步任意Unity项目
python3 sync_unity_project.py /path/to/your/unity/project
```

## ✨ 功能特性

### 智能排除
自动排除以下目录的文档：
- `Library/` - Unity Library目录
- `PackageCache/` - Unity包缓存
- `Temp/` - 临时文件
- `.git/` - Git版本控制
- `node_modules/` - Node.js模块
- `__pycache__/` - Python缓存
- 以`.`开头的隐藏文件

### 统一归类
- 所有文档同步到 `Claude/{项目名}` 文件夹
- 文档标题格式：`[项目名] 文档名`
- 自动Markdown格式转换

### 安全确认
- 显示文档统计信息
- 按目录分类展示
- 需要用户确认后才执行同步

## 📊 同步流程

1. **扫描项目** - 递归查找所有MD文档
2. **智能过滤** - 排除无关的系统和缓存文件
3. **统计展示** - 显示文档分布和数量
4. **用户确认** - 确认后开始同步
5. **批量同步** - 逐一同步到指定文件夹
6. **结果报告** - 显示成功/失败统计

## 📋 使用场景

### 项目文档整理
```bash
# 整理工作项目的技术文档
python3 sync_unity_project.py /Volumes/Q/MiniGame/WorkProject

# 同步学习项目的笔记
python3 sync_unity_project.py /Users/yourname/UnityProjects/LearningProject
```

### 多项目批量同步
```bash
# 依次同步多个项目
python3 sync_unity_project.py /path/to/project1
python3 sync_unity_project.py /path/to/project2  
python3 sync_unity_project.py /path/to/project3
```

## 🛡️ 安全保障

- **只读操作** - 不会修改或删除源文件
- **增量同步** - 已存在的文档会被更新，不会重复创建
- **错误处理** - 单个文档失败不影响其他文档同步
- **详细日志** - 显示每个文档的同步状态

## 📱 查看结果

同步完成后，在Apple备忘录中：

```
Claude/
├── gamebox_develop/          # 第一个项目
│   ├── [gamebox_develop] README
│   ├── [gamebox_develop] 五子棋AI模块详细分析
│   └── ...
├── MonroeDiner_Dev/          # 第二个项目  
│   ├── [MonroeDiner_Dev] README
│   ├── [MonroeDiner_Dev] CLAUDE
│   └── ...
└── YourProject/              # 你的项目
    ├── [YourProject] 文档1
    └── ...
```

## 💡 最佳实践

1. **项目根目录** - 使用Unity项目的根目录路径
2. **批量操作** - 一次处理一个项目，避免混乱
3. **定期同步** - 项目更新后重新同步以获得最新文档
4. **备份重要** - 虽然是只读操作，建议重要文档有备份

## 🚨 注意事项

- 确保Apple备忘录已登录iCloud账户
- 大项目首次同步可能需要较长时间
- 网络不稳定时可能出现个别文档同步失败
- 同名文档会被更新覆盖，不会重复创建

---

🎯 **一个命令，整理所有Unity项目文档！**