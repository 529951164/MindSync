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

# 检查Claude Code
if ! command -v claude-code &> /dev/null; then
    echo "⚠️  未找到Claude Code，请确保已安装Claude Code"
    echo "   Hook功能将不可用，但基本同步功能正常"
else
    echo "✅ 找到Claude Code，准备安装Hook"
    
    # 安装Hook
    if [[ -f "$SCRIPT_DIR/install_hook.py" ]]; then
        echo "🔗 正在安装Claude Code Hook..."
        python3 "$SCRIPT_DIR/install_hook.py"
    fi
fi

# 运行测试
echo "🧪 运行功能测试..."
if python3 test_sync.py; then
    echo "✅ 功能测试通过"
else
    echo "⚠️  功能测试失败，请检查配置"
fi

echo ""
echo "🎉 MindSync 部署完成！"
echo ""
echo "📖 使用指南："
echo "  • 同步文件：python3 main.py sync-file your-file.md"
echo "  • 查看帮助：python3 main.py --help"
echo "  • 如果配置了Hook，编辑MD文件时将自动同步"
echo ""
echo "📚 完整文档：https://github.com/529951164/MindSync"
echo "=================================="