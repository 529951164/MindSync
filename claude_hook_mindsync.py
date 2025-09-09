#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Hook脚本
自动同步MD文档到Apple Notes
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加同步工具路径
tool_path = Path(r"/Volumes/Q/MiniGame/MacNoteTools")
if str(tool_path) not in sys.path:
    sys.path.insert(0, str(tool_path))

from claude_hook import sync_file_hook, sync_multiple_files_hook

def is_markdown_file(file_path: str) -> bool:
    """检查文件是否为Markdown文件"""
    return file_path.lower().endswith(('.md', '.markdown'))

def main():
    """主函数 - Claude Hook入口点"""
    try:
        # 读取来自Claude Code的JSON数据
        stdin_data = ""
        for line in sys.stdin:
            stdin_data += line
        
        if not stdin_data.strip():
            sys.exit(0)
        
        # 解析JSON数据
        data = json.loads(stdin_data)
        
        # 获取工具信息
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        
        # 处理Write和Edit工具的Markdown文件
        if tool_name in ['Write', 'Edit'] and 'file_path' in tool_input:
            file_path = tool_input['file_path']
            
            if is_markdown_file(file_path):
                config_path = r"/Volumes/Q/MiniGame/MacNoteTools/config.json"
                
                # 执行同步
                success = sync_file_hook(file_path, "save", config_path)
                
                # 记录日志
                with open("/tmp/claude_mindsync.log", "a", encoding="utf-8") as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status = "成功" if success else "失败"
                    f.write(f"[{timestamp}] 同步{status}: {file_path}\n")
        
        sys.exit(0)
        
    except Exception as e:
        # 记录错误日志
        with open("/tmp/claude_mindsync_error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Hook执行异常: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()