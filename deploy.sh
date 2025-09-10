#!/bin/bash
# MindSync 一键部署脚本
# 适用于任何macOS用户的自动部署

set -e  # 遇到错误立即退出

echo "🚀 MindSync 一键部署脚本"
echo "=================================="

# 检查是否为macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误：此脚本只支持macOS系统"
    exit 1
fi

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.7.0"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ 错误：需要Python 3.7+，当前版本：$python_version"
    exit 1
fi

echo "✅ 环境检查通过"

# 获取当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "📂 项目目录：$SCRIPT_DIR"

# 检查必要文件
required_files=("main.py" "config.json" "install_hook.py")
for file in "${required_files[@]}"; do
    if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
        echo "❌ 缺少必要文件：$file"
        exit 1
    fi
done

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"
echo "✅ 日志目录已创建"

# 初始化配置
echo "🔧 初始化配置文件..."
cd "$SCRIPT_DIR"
python3 main.py config --init

# 验证配置
echo "🔍 验证配置..."
python3 main.py config --validate

# 检测和安装编辑器集成
echo ""
echo "🔍 检测已安装的编辑器..."

INSTALLED_EDITORS=0

# 检查Claude Code
if command -v claude-code &> /dev/null; then
    echo "✅ 检测到 Claude Code"
    INSTALLED_EDITORS=$((INSTALLED_EDITORS + 1))
    
    # 安装Hook
    if [[ -f "$SCRIPT_DIR/install_hook.py" ]]; then
        echo "🔗 正在安装Claude Code Hook..."
        if python3 "$SCRIPT_DIR/install_hook.py"; then
            # 更新配置状态
            python3 "$SCRIPT_DIR/main.py" api config --editor claude_code --set hook_installed true --format json > /dev/null
            echo "✅ Claude Code Hook安装成功"
        else
            echo "❌ Claude Code Hook安装失败"
        fi
    fi
else
    echo "⚠️  未找到Claude Code"
fi

# 检查Cursor
CURSOR_PATH=""
if [[ -f "/Applications/Cursor.app/Contents/MacOS/Cursor" ]]; then
    CURSOR_PATH="/Applications/Cursor.app"
elif [[ -d "$HOME/.cursor" ]]; then
    CURSOR_PATH="~/.cursor"
fi

if [[ -n "$CURSOR_PATH" ]]; then
    echo "✅ 检测到 Cursor"
    INSTALLED_EDITORS=$((INSTALLED_EDITORS + 1))
    
    # 安装Cursor扩展
    if [[ -f "$SCRIPT_DIR/cursor-extension/install.sh" ]]; then
        echo "🔗 正在安装Cursor扩展..."
        if bash "$SCRIPT_DIR/cursor-extension/install.sh"; then
            # 更新配置状态
            python3 "$SCRIPT_DIR/main.py" api config --editor cursor --set extension_installed true --format json > /dev/null
            echo "✅ Cursor扩展安装成功"
        else
            echo "❌ Cursor扩展安装失败"
        fi
    fi
else
    echo "⚠️  未找到Cursor"
fi

# 检查VSCode
VSCODE_PATH=""
if [[ -f "/Applications/Visual Studio Code.app/Contents/MacOS/Electron" ]]; then
    VSCODE_PATH="/Applications/Visual Studio Code.app"
elif [[ -d "$HOME/.vscode" ]]; then
    VSCODE_PATH="~/.vscode"
fi

if [[ -n "$VSCODE_PATH" ]]; then
    echo "✅ 检测到 VSCode"
    INSTALLED_EDITORS=$((INSTALLED_EDITORS + 1))
    
    # VSCode使用相同的扩展
    if [[ -f "$SCRIPT_DIR/cursor-extension/install.sh" ]]; then
        echo "🔗 正在安装VSCode扩展..."
        if bash "$SCRIPT_DIR/cursor-extension/install.sh"; then
            # 更新配置状态
            python3 "$SCRIPT_DIR/main.py" api config --editor vscode --set extension_installed true --format json > /dev/null
            echo "✅ VSCode扩展安装成功"
        else
            echo "❌ VSCode扩展安装失败"
        fi
    fi
else
    echo "⚠️  未找到VSCode"
fi

if [[ $INSTALLED_EDITORS -eq 0 ]]; then
    echo "❌ 未检测到支持的编辑器（Claude Code、Cursor、VSCode）"
    echo "   基本同步功能仍可使用"
else
    echo "🎉 成功集成 $INSTALLED_EDITORS 个编辑器"
fi

# 运行测试
echo "🧪 运行功能测试..."
if python3 test_sync.py; then
    echo "✅ 功能测试通过"
else
    echo "⚠️  功能测试失败，请检查配置"
fi

echo ""
echo "🎉 MindSync 多编辑器支持部署完成！"
echo ""

# 显示编辑器特定的使用指南
echo "📖 使用指南："

if python3 "$SCRIPT_DIR/main.py" api config --editor claude_code --get hook_installed --format json 2>/dev/null | grep -q "true"; then
    echo "  📝 Claude Code："
    echo "    • 编辑MD文件时自动同步到备忘录"
    echo "    • 无需任何额外操作"
fi

if python3 "$SCRIPT_DIR/main.py" api config --editor cursor --get extension_installed --format json 2>/dev/null | grep -q "true"; then
    echo "  🎯 Cursor："
    echo "    • 保存MD文件时自动同步"
    echo "    • 使用 Cmd+Shift+M 手动同步"
    echo "    • 状态栏显示同步状态"
fi

if python3 "$SCRIPT_DIR/main.py" api config --editor vscode --get extension_installed --format json 2>/dev/null | grep -q "true"; then
    echo "  📋 VSCode："
    echo "    • 保存MD文件时自动同步"
    echo "    • 使用 Cmd+Shift+M 手动同步"
    echo "    • 状态栏显示同步状态"
fi

echo ""
echo "⚡ 通用命令："
echo "  • 手动同步：python3 main.py sync-file your-file.md"
echo "  • 检查状态：python3 main.py api status"
echo "  • 查看配置：python3 main.py config --show"
echo "  • 查看帮助：python3 main.py --help"
echo ""
echo "🔧 配置管理："
echo "  • 获取设置：python3 main.py api config --editor cursor --get auto_sync"
echo "  • 修改设置：python3 main.py api config --editor cursor --set auto_sync false"
echo ""
echo "📚 完整文档：https://github.com/529951164/MindSync"
echo "🐛 问题反馈：https://github.com/529951164/MindSync/issues"
echo "=================================="