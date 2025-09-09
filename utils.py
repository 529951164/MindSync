#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供各种辅助功能和通用函数
"""

import os
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

def get_project_name_from_path(file_path: Union[str, Path]) -> Optional[str]:
    """
    从文件路径中提取项目名称
    
    Args:
        file_path: 文件路径
        
    Returns:
        项目名称，如果无法识别则返回None
    """
    path = Path(file_path)
    path_parts = path.parts
    
    # 常见的项目目录识别模式
    project_indicators = [
        # Unity项目标识
        ('Assets', 'Scripts'),
        ('ProjectSettings',),
        ('Packages',),
        
        # Git项目标识
        ('.git',),
        
        # Node.js项目标识
        ('package.json',),
        ('node_modules',),
        
        # Python项目标识
        ('requirements.txt',),
        ('pyproject.toml',),
        ('setup.py',),
        ('main.py',),
        ('config.json',),
        
        # 其他常见项目结构
        ('src', 'main'),
        ('lib', 'include'),
        ('docs',),
        ('README.md',),
        ('README.rst',)
    ]
    
    # 向上查找项目根目录
    current_path = path.absolute().parent
    while current_path != current_path.parent:  # 直到根目录
        dir_contents = set(p.name for p in current_path.iterdir() if p.is_dir() or p.is_file())
        
        # 检查是否匹配项目标识
        for indicators in project_indicators:
            if all(indicator in dir_contents for indicator in indicators):
                return current_path.name
        
        current_path = current_path.parent
    
    # 如果没找到项目标识，使用文件所在的最近的有意义的目录名
    for part in reversed(path_parts[:-1]):  # 排除文件名
        # 跳过一些通用目录名
        if part.lower() not in ['documents', 'desktop', 'downloads', 'tmp', 'temp', 'users', 'home', 'volumes']:
            return part
    
    return None

def detect_file_category(file_path: Union[str, Path], content: str = None) -> str:
    """
    检测文件类别，用于智能分类
    
    Args:
        file_path: 文件路径
        content: 文件内容（可选）
        
    Returns:
        文件类别字符串
    """
    path = Path(file_path)
    file_name = path.name.lower()
    path_str = str(path).lower()
    
    # 基于文件名的分类
    name_patterns = {
        'readme': ['readme', 'read_me'],
        'changelog': ['changelog', 'change_log', 'changes'],
        'todo': ['todo', 'task', 'tasks'],
        'meeting': ['meeting', 'minutes', '会议'],
        'journal': ['journal', 'diary', '日记'],
        'draft': ['draft', '草稿'],
        'note': ['note', 'notes', '笔记'],
        'doc': ['doc', 'documentation', '文档'],
        'guide': ['guide', 'tutorial', '教程', '指南'],
        'api': ['api', 'reference'],
        'spec': ['spec', 'specification', '规范'],
        'design': ['design', '设计'],
        'architecture': ['architecture', 'arch', '架构'],
        'config': ['config', 'configuration', '配置'],
        'install': ['install', 'setup', '安装'],
        'troubleshooting': ['troubleshoot', 'faq', '故障', '问题']
    }
    
    for category, patterns in name_patterns.items():
        if any(pattern in file_name for pattern in patterns):
            return category
    
    # 基于路径的分类
    path_patterns = {
        'unity': ['unity', 'assets', 'scripts'],
        'web': ['web', 'html', 'css', 'js', 'javascript'],
        'mobile': ['mobile', 'android', 'ios', 'flutter', 'react-native'],
        'backend': ['backend', 'server', 'api', 'database'],
        'frontend': ['frontend', 'client', 'ui', 'ux'],
        'devops': ['devops', 'docker', 'kubernetes', 'ci', 'cd'],
        'data': ['data', 'analytics', 'ml', 'ai', 'machine-learning'],
        'security': ['security', 'auth', 'encryption'],
        'test': ['test', 'testing', 'spec', 'specs']
    }
    
    for category, patterns in path_patterns.items():
        if any(pattern in path_str for pattern in patterns):
            return category
    
    # 基于内容的分类（如果提供了内容）
    if content:
        content_lower = content.lower()
        
        # 检查代码块
        if '```' in content or '    ' in content:
            return 'technical'
        
        # 检查特定关键词
        if any(keyword in content_lower for keyword in ['class ', 'function ', 'def ', 'var ', 'let ', 'const ']):
            return 'code'
        
        if any(keyword in content_lower for keyword in ['meeting', 'action item', 'attendees', '会议', '参会']):
            return 'meeting'
        
        if any(keyword in content_lower for keyword in ['todo', 'task', '待办', '任务']):
            return 'todo'
    
    return 'general'

def get_claude_folder_path(file_path: Union[str, Path], project_name: str = None) -> str:
    """
    根据文件路径和项目名称生成Claude文件夹路径
    
    Args:
        file_path: 源文件路径
        project_name: 项目名称（可选）
        
    Returns:
        Claude备忘录中的文件夹路径
    """
    # 如果没有提供项目名称，尝试从路径中提取
    if not project_name:
        project_name = get_project_name_from_path(file_path)
    
    # 如果还是没有项目名称，使用默认路径
    if not project_name:
        return "Claude/Other"
    
    # 清理项目名称，移除特殊字符
    clean_name = re.sub(r'[^\w\s-]', '', project_name)
    clean_name = re.sub(r'[-\s]+', '-', clean_name).strip('-')
    
    return f"Claude/{clean_name}"

def generate_file_hash(file_path: Union[str, Path]) -> str:
    """
    生成文件内容的哈希值，用于检测内容变化
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容的MD5哈希值
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()
    except Exception:
        return ""

def is_binary_file(file_path: Union[str, Path]) -> bool:
    """
    检查文件是否为二进制文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        如果是二进制文件返回True
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读字符串
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def format_time_delta(td: timedelta) -> str:
    """
    格式化时间差为可读字符串
    
    Args:
        td: 时间差
        
    Returns:
        格式化的时间字符串
    """
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}秒"
    elif total_seconds < 3600:
        return f"{total_seconds//60}分钟"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}天{hours}小时"

def extract_markdown_title(content: str) -> Optional[str]:
    """
    从Markdown内容中提取第一个标题
    
    Args:
        content: Markdown内容
        
    Returns:
        提取的标题，如果没有找到返回None
    """
    # 匹配 # 标题
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    # 匹配下划线标题
    underline_match = re.search(r'^(.+)\n=+', content, re.MULTILINE)
    if underline_match:
        return underline_match.group(1).strip()
    
    return None

def extract_markdown_tags(content: str) -> List[str]:
    """
    从Markdown内容中提取标签
    
    Args:
        content: Markdown内容
        
    Returns:
        标签列表
    """
    # 匹配 #tag 格式的标签
    tags = re.findall(r'(?:^|\s)#(\w+)', content)
    
    # 匹配 YAML front matter 中的 tags
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        yaml_content = frontmatter_match.group(1)
        tag_match = re.search(r'tags:\s*\[(.*?)\]', yaml_content)
        if tag_match:
            yaml_tags = [tag.strip().strip('"\'') for tag in tag_match.group(1).split(',')]
            tags.extend(yaml_tags)
    
    return list(set(tags))  # 去重

def clean_filename_for_title(filename: str) -> str:
    """
    清理文件名用作备忘录标题
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的标题
    """
    # 移除扩展名
    name = Path(filename).stem
    
    # 替换连字符和下划线为空格
    name = re.sub(r'[-_]', ' ', name)
    
    # 移除数字前缀（如 "01-", "001."）
    name = re.sub(r'^\d+[-.]?\s*', '', name)
    
    # 首字母大写
    name = name.title()
    
    # 清理多余空格
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def validate_applescript_string(text: str) -> bool:
    """
    验证字符串是否适合AppleScript使用
    
    Args:
        text: 要验证的字符串
        
    Returns:
        如果字符串安全返回True
    """
    # 检查长度限制
    if len(text) > 10000:  # AppleScript字符串长度限制
        return False
    
    # 检查是否包含null字符
    if '\0' in text:
        return False
    
    return True

def get_file_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    获取文件元数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        包含文件元数据的字典
    """
    path = Path(file_path)
    
    try:
        stat = path.stat()
        
        return {
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size_bytes': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'is_binary': is_binary_file(path),
            'project_name': get_project_name_from_path(path),
            'category': detect_file_category(path)
        }
    except Exception as e:
        return {'error': str(e)}

def find_files_by_pattern(directory: Union[str, Path], 
                         pattern: str = "*.md",
                         recursive: bool = True,
                         exclude_patterns: List[str] = None) -> List[Path]:
    """
    根据模式查找文件
    
    Args:
        directory: 搜索目录
        pattern: 文件模式（如 "*.md"）
        recursive: 是否递归搜索
        exclude_patterns: 排除模式列表
        
    Returns:
        匹配的文件路径列表
    """
    directory = Path(directory)
    exclude_patterns = exclude_patterns or []
    
    if recursive:
        files = directory.rglob(pattern)
    else:
        files = directory.glob(pattern)
    
    # 应用排除模式
    filtered_files = []
    for file_path in files:
        should_exclude = False
        
        for exclude_pattern in exclude_patterns:
            if file_path.match(exclude_pattern):
                should_exclude = True
                break
        
        if not should_exclude:
            filtered_files.append(file_path)
    
    return sorted(filtered_files)

class ProgressReporter:
    """进度报告器"""
    
    def __init__(self, total: int, description: str = "处理中"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        self._print_progress()
    
    def _print_progress(self):
        """打印进度条"""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        filled_length = int(50 * self.current // self.total) if self.total > 0 else 0
        
        bar = '█' * filled_length + '-' * (50 - filled_length)
        
        elapsed = datetime.now() - self.start_time
        if self.current > 0:
            avg_time = elapsed.total_seconds() / self.current
            eta = timedelta(seconds=avg_time * (self.total - self.current))
            eta_str = f" ETA: {format_time_delta(eta)}"
        else:
            eta_str = ""
        
        print(f'\r{self.description}: |{bar}| {self.current}/{self.total} ({percentage:.1f}%){eta_str}', end='', flush=True)
        
        if self.current >= self.total:
            print()  # 换行
    
    def finish(self):
        """完成进度报告"""
        self.current = self.total
        self._print_progress()