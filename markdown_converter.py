#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown到Apple备忘录格式转换器
将Markdown文本转换为备忘录应用能正确显示的格式
"""

import re
from typing import List

class MarkdownToNotesConverter:
    """Markdown到备忘录格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        pass
    
    def convert(self, markdown_text: str) -> str:
        """
        转换Markdown文本为备忘录格式
        
        Args:
            markdown_text: 原始Markdown文本
            
        Returns:
            转换后的备忘录格式文本
        """
        text = markdown_text
        
        # 按顺序应用转换规则
        text = self._convert_headers(text)
        text = self._convert_bold_italic(text)
        text = self._convert_code(text)
        text = self._convert_lists(text)
        text = self._convert_quotes(text)
        text = self._convert_links(text)
        text = self._convert_horizontal_rules(text)
        text = self._clean_up(text)
        
        return text
    
    def _convert_headers(self, text: str) -> str:
        """转换标题"""
        # H1: # 标题 -> 【标题】
        text = re.sub(r'^# (.+)$', r'【\1】', text, flags=re.MULTILINE)
        
        # H2: ## 标题 -> ■ 标题
        text = re.sub(r'^## (.+)$', r'■ \1', text, flags=re.MULTILINE)
        
        # H3: ### 标题 -> ▶ 标题
        text = re.sub(r'^### (.+)$', r'▶ \1', text, flags=re.MULTILINE)
        
        # H4+: #### 标题 -> • 标题
        text = re.sub(r'^#{4,} (.+)$', r'• \1', text, flags=re.MULTILINE)
        
        return text
    
    def _convert_bold_italic(self, text: str) -> str:
        """转换加粗和斜体"""
        # **加粗** 或 __加粗__ -> 【加粗】
        text = re.sub(r'\*\*(.+?)\*\*', r'【\1】', text)
        text = re.sub(r'__(.+?)__', r'【\1】', text)
        
        # *斜体* 或 _斜体_ -> 《斜体》
        text = re.sub(r'\*([^*]+?)\*', r'《\1》', text)
        text = re.sub(r'_([^_]+?)_', r'《\1》', text)
        
        return text
    
    def _convert_code(self, text: str) -> str:
        """转换代码"""
        # 代码块 ```code``` -> 移除标记，保持缩进
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            
            # 为每行代码添加缩进
            lines = code.strip().split('\n')
            indented_lines = [f"    {line}" for line in lines]
            
            if lang:
                header = f"[{lang}代码]"
                return f"{header}\n" + "\n".join(indented_lines)
            else:
                return "\n".join(indented_lines)
        
        text = re.sub(r'```(\w*)\n?(.*?)```', replace_code_block, text, flags=re.DOTALL)
        
        # 行内代码 `code` -> 「code」
        text = re.sub(r'`([^`]+?)`', r'「\1」', text)
        
        return text
    
    def _convert_lists(self, text: str) -> str:
        """转换列表"""
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            # 有序列表 1. 项目 -> ① 项目
            ordered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
            if ordered_match:
                indent = ordered_match.group(1)
                number = int(ordered_match.group(2))
                content = ordered_match.group(3)
                
                # 使用圆圈数字符号
                if number <= 10:
                    symbols = ['', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
                    symbol = symbols[number] if number < len(symbols) else f"({number})"
                else:
                    symbol = f"({number})"
                
                result_lines.append(f"{indent}{symbol} {content}")
                continue
            
            # 无序列表 - 项目 或 * 项目 -> • 项目
            unordered_match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            if unordered_match:
                indent = unordered_match.group(1)
                content = unordered_match.group(2)
                
                # 根据缩进级别使用不同符号
                indent_level = len(indent) // 2
                if indent_level == 0:
                    symbol = '•'
                elif indent_level == 1:
                    symbol = '◦'
                else:
                    symbol = '▪'
                
                result_lines.append(f"{indent}{symbol} {content}")
                continue
            
            # 普通行保持不变
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _convert_quotes(self, text: str) -> str:
        """转换引用"""
        # > 引用 -> 「引用」
        lines = text.split('\n')
        result_lines = []
        in_quote = False
        quote_lines = []
        
        for line in lines:
            if line.startswith('> '):
                # 引用行
                quote_content = line[2:]  # 移除 "> "
                quote_lines.append(quote_content)
                in_quote = True
            else:
                # 非引用行
                if in_quote and quote_lines:
                    # 结束引用块
                    quote_text = '\n'.join(quote_lines)
                    result_lines.append(f"💬 {quote_text}")
                    quote_lines = []
                    in_quote = False
                
                if line.strip():  # 非空行
                    result_lines.append(line)
                else:  # 空行
                    result_lines.append(line)
        
        # 处理文档末尾的引用
        if in_quote and quote_lines:
            quote_text = '\n'.join(quote_lines)
            result_lines.append(f"💬 {quote_text}")
        
        return '\n'.join(result_lines)
    
    def _convert_links(self, text: str) -> str:
        """转换链接"""
        # [文本](链接) -> 文本 (链接)
        text = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'\1 (\2)', text)
        
        # 自动链接 <链接> -> 链接
        text = re.sub(r'<(https?://[^>]+?)>', r'\1', text)
        
        return text
    
    def _convert_horizontal_rules(self, text: str) -> str:
        """转换水平分割线"""
        # --- 或 *** -> ——————————
        text = re.sub(r'^(-{3,}|\*{3,}|_{3,})$', '——————————', text, flags=re.MULTILINE)
        
        return text
    
    def _clean_up(self, text: str) -> str:
        """清理和优化文本"""
        # 确保段落间有足够的分隔
        lines = text.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # 在以下情况后添加额外空行：
            # 1. 标题后
            # 2. 列表项组后
            # 3. 代码块后
            # 4. 引用后
            if line.strip():
                if (line.startswith('【') and line.endswith('】') or  # H1标题
                    line.startswith('■ ') or  # H2标题
                    line.startswith('▶ ') or  # H3标题
                    line.startswith('💬 ') or  # 引用
                    line == '——————————'):  # 分隔线
                    
                    # 检查下一行是否为空，如果不是则添加空行
                    if (i + 1 < len(lines) and 
                        lines[i + 1].strip() != ''):
                        result_lines.append('')
        
        # 重新组合文本
        text = '\n'.join(result_lines)
        
        # 移除超过2个的连续换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 去除首尾空白
        text = text.strip()
        
        # 为Apple Notes转换换行符
        # Apple Notes使用HTML格式，需要<br>标签来表示换行
        text = text.replace('\n\n', '<br><br>')  # 段落间距
        text = text.replace('\n', '<br>')        # 单行换行
        
        return text

def convert_markdown_for_notes(markdown_text: str) -> str:
    """
    便捷函数：转换Markdown文本为备忘录格式
    
    Args:
        markdown_text: 原始Markdown文本
        
    Returns:
        转换后的备忘录格式文本
    """
    converter = MarkdownToNotesConverter()
    return converter.convert(markdown_text)