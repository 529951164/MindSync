#!/bin/bash
# MindSync Cursor/VSCode扩展安装脚本

set -e

echo "🚀 MindSync Cursor/VSCode扩展安装器"
echo "===================================="

# 检测编辑器
CURSOR_EXT_DIR="$HOME/.cursor/extensions"
VSCODE_EXT_DIR="$HOME/.vscode/extensions"
INSTALLED=false

# 生成扩展目录名
EXT_NAME="mindsync.mindsync-cursor-1.0.0"

# 获取当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

install_to_editor() {
    local ext_dir="$1"
    local editor_name="$2"
    
    if [[ -d "$ext_dir" ]]; then
        echo "📁 检测到 $editor_name"
        
        # 创建扩展目录
        mkdir -p "$ext_dir/$EXT_NAME"
        
        # 复制扩展文件
        cp "$SCRIPT_DIR/package.json" "$ext_dir/$EXT_NAME/"
        cp "$SCRIPT_DIR/extension.js" "$ext_dir/$EXT_NAME/"
        cp "$SCRIPT_DIR/README.md" "$ext_dir/$EXT_NAME/"
        
        echo "✅ $editor_name 扩展安装完成"
        INSTALLED=true
    fi
}

# 尝试安装到Cursor
install_to_editor "$CURSOR_EXT_DIR" "Cursor"

# 尝试安装到VSCode  
install_to_editor "$VSCODE_EXT_DIR" "VSCode"

if [[ "$INSTALLED" == true ]]; then
    echo ""
    echo "🎉 扩展安装成功！"
    echo ""
    echo "📖 使用说明："
    echo "  1. 重启编辑器"
    echo "  2. 打开任意Markdown文件"
    echo "  3. 保存文件时会自动同步到备忘录"
    echo "  4. 使用Cmd+Shift+M手动同步当前文档"
    echo ""
    echo "⚙️  设置："
    echo "  • 打开设置，搜索'mindsync'"
    echo "  • 配置自动同步、通知等选项"
    echo ""
    echo "🔍 状态检查："
    echo "  • 点击状态栏的'MindSync'按钮"
    echo "  • 或运行命令'MindSync: 检查状态'"
    echo ""
else
    echo "❌ 未检测到支持的编辑器"
    echo "请确保安装了Cursor或VSCode"
fi

echo "===================================="