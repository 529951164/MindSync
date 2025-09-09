#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容相关的同步规则
根据文件内容和结构决定同步行为
"""

from pathlib import Path
from typing import Dict, Any, List
import re
from .base_rule import SyncRule

class TitlePrefixRule(SyncRule):
    """标题前缀规则"""
    
    def __init__(self, prefix_map: Dict[str, str] = None, priority: int = 85):
        """
        Args:
            prefix_map: 路径关键字到前缀的映射
        """
        super().__init__("动态标题前缀", priority)
        self.prefix_map = prefix_map or {
            'claude': '🤖 ',
            'work': '💼 ',
            'personal': '👤 ',
            'tech': '🔧 ',
            'notes': '📝 ',
            'todo': '✅ ',
            'draft': '📄 '
        }
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则来处理标题"""
        return self.enabled
    
    def get_title(self, md_file: Path, config: Dict[str, Any]) -> str:
        """重写标题生成逻辑，添加动态前缀"""
        # 先调用父类方法获取基础标题
        base_title = super().get_title(md_file, config)
        
        # 根据文件路径添加前缀
        file_path_str = str(md_file).lower()
        
        for keyword, prefix in self.prefix_map.items():
            if keyword in file_path_str:
                return f"{prefix}{base_title}"
        
        return base_title
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响标题生成，不执行实际同步"""
        return True

class ContentFilterRule(SyncRule):
    """内容过滤规则"""
    
    def __init__(self, 
                 required_patterns: List[str] = None,
                 excluded_patterns: List[str] = None,
                 priority: int = 80):
        """
        Args:
            required_patterns: 必须包含的正则表达式模式列表
            excluded_patterns: 不能包含的正则表达式模式列表
        """
        super().__init__("内容过滤", priority)
        self.required_patterns = required_patterns or []
        self.excluded_patterns = excluded_patterns or []
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件内容是否符合过滤条件"""
        if not self.enabled:
            return True
        
        try:
            encoding = config.get('sync_rules', {}).get('encoding', 'utf-8')
            with open(md_file, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 检查必须包含的模式
            for pattern in self.required_patterns:
                if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    self.logger.debug(f"文件不包含必需模式 '{pattern}': {md_file.name}")
                    return False
            
            # 检查不能包含的模式
            for pattern in self.excluded_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    self.logger.debug(f"文件包含排除模式 '{pattern}': {md_file.name}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"读取文件内容失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则不执行实际同步，只做过滤"""
        return True

class SizeLimitRule(SyncRule):
    """文件大小限制规则"""
    
    def __init__(self, max_size_mb: float = None, min_size_bytes: int = 10, priority: int = 90):
        """
        Args:
            max_size_mb: 最大文件大小（MB）
            min_size_bytes: 最小文件大小（字节）
        """
        super().__init__("文件大小限制", priority)
        self.max_size_mb = max_size_mb
        self.min_size_bytes = min_size_bytes
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件大小是否在允许范围内"""
        if not self.enabled:
            return True
        
        try:
            file_size = md_file.stat().st_size
            
            # 检查最小大小
            if file_size < self.min_size_bytes:
                self.logger.debug(f"文件太小: {md_file.name} ({file_size} bytes)")
                return False
            
            # 检查最大大小
            max_size_mb = self.max_size_mb or config.get('sync_rules', {}).get('max_file_size_mb', 50)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                self.logger.debug(f"文件太大: {md_file.name} ({file_size / 1024 / 1024:.2f}MB)")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查文件大小失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则不执行实际同步，只做过滤"""
        return True

class FolderMappingRule(SyncRule):
    """智能文件夹映射规则"""
    
    def __init__(self, priority: int = 85):
        super().__init__("智能文件夹映射", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则"""
        return self.enabled
    
    def get_folder(self, md_file: Path, config: Dict[str, Any]) -> str:
        """重写文件夹映射逻辑，提供更智能的映射"""
        # 获取配置中的文件夹映射
        folder_mappings = config.get('sync_rules', {}).get('folder_mappings', {})
        default_folder = config.get('notes_config', {}).get('default_folder', 'Notes')
        
        # 文件路径分析
        file_path_str = str(md_file).lower()
        file_name = md_file.name.lower()
        
        # 优先级映射：路径关键字 -> 文件夹名
        priority_mappings = [
            # 高优先级：特定项目或工作相关
            ('claude', folder_mappings.get('claude', '🤖 Claude文档')),
            ('work', folder_mappings.get('work', '💼 工作笔记')),
            ('project', folder_mappings.get('work', '💼 工作笔记')),
            
            # 中优先级：内容类型
            ('tech', folder_mappings.get('tech', '🔧 技术文档')),
            ('code', folder_mappings.get('tech', '🔧 技术文档')),
            ('programming', folder_mappings.get('tech', '🔧 技术文档')),
            
            # 个人相关
            ('personal', folder_mappings.get('personal', '👤 个人笔记')),
            ('diary', folder_mappings.get('personal', '👤 个人笔记')),
            ('journal', folder_mappings.get('personal', '👤 个人笔记')),
            
            # 特殊类型
            ('todo', '✅ 待办事项'),
            ('task', '✅ 待办事项'),
            ('meeting', '📅 会议记录'),
            ('draft', '📄 草稿'),
            ('temp', '🗃️ 临时文件'),
        ]
        
        # 按优先级匹配
        for keyword, folder_name in priority_mappings:
            if keyword in file_path_str or keyword in file_name:
                self.logger.debug(f"文件夹映射: {md_file.name} -> {folder_name} (关键字: {keyword})")
                return folder_name
        
        # 根据文件名模式匹配
        if re.match(r'^\d{4}-\d{2}-\d{2}', md_file.name):
            return '📅 日期笔记'
        
        if 'readme' in file_name:
            return '📖 说明文档'
        
        # 返回默认文件夹
        return folder_mappings.get('default', default_folder)
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响文件夹选择，不执行实际同步"""
        return True

class HeaderExtractorRule(SyncRule):
    """从Markdown标题提取备忘录标题规则"""
    
    def __init__(self, priority: int = 85):
        super().__init__("从内容提取标题", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查配置是否启用标题提取"""
        return self.enabled and config.get('sync_rules', {}).get('extract_title_from_content', False)
    
    def get_title(self, md_file: Path, config: Dict[str, Any]) -> str:
        """从文件内容中提取标题"""
        try:
            encoding = config.get('sync_rules', {}).get('encoding', 'utf-8')
            with open(md_file, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 查找第一个标题
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            if title_match:
                extracted_title = title_match.group(1).strip()
                self.logger.debug(f"从内容提取标题: {extracted_title}")
                
                # 应用配置中的前缀和后缀
                notes_config = config.get('notes_config', {})
                
                prefix = notes_config.get('title_prefix', '')
                if prefix:
                    extracted_title = f"{prefix}{extracted_title}"
                
                suffix = notes_config.get('title_suffix', '')
                if suffix:
                    extracted_title = f"{extracted_title}{suffix}"
                
                return extracted_title
        
        except Exception as e:
            self.logger.error(f"提取标题失败: {md_file} - {e}")
        
        # 失败时使用默认方法
        return super().get_title(md_file, config)
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响标题生成，不执行实际同步"""
        return True

class MetadataRule(SyncRule):
    """Markdown元数据处理规则"""
    
    def __init__(self, priority: int = 85):
        super().__init__("元数据处理", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则"""
        return self.enabled
    
    def get_content(self, md_file: Path, config: Dict[str, Any]) -> str:
        """处理Markdown元数据"""
        content = super().get_content(md_file, config)
        
        # 提取Front Matter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if frontmatter_match:
            metadata = frontmatter_match.group(1)
            body_content = frontmatter_match.group(2)
            
            # 解析元数据
            meta_info = []
            for line in metadata.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    meta_info.append(f"**{key.strip()}**: {value.strip()}")
            
            if meta_info:
                metadata_section = "## 📋 元数据\\n" + "\\n".join(meta_info) + "\\n\\n"
                content = metadata_section + body_content
        
        return content
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响内容处理，不执行实际同步"""
        return True