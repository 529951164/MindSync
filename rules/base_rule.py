#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步规则基类
定义所有同步规则的通用接口和行为
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SyncRule(ABC):
    """同步规则基类"""
    
    def __init__(self, name: str, priority: int = 0, enabled: bool = True):
        """
        初始化同步规则
        
        Args:
            name: 规则名称
            priority: 规则优先级，数字越大优先级越高
            enabled: 是否启用规则
        """
        self.name = name
        self.priority = priority
        self.enabled = enabled
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def __str__(self) -> str:
        return f"{self.name}(priority={self.priority}, enabled={self.enabled})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', priority={self.priority}, enabled={self.enabled})"
    
    @abstractmethod
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """
        判断规则是否应该应用到指定文件
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            如果规则应该应用返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """
        执行同步规则
        
        Args:
            md_file: MD文件路径
            apple_bridge: AppleScript桥接对象
            config: 配置字典
            
        Returns:
            执行成功返回True，否则返回False
        """
        pass
    
    def get_title(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        获取备忘录标题
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            生成的备忘录标题
        """
        notes_config = config.get('notes_config', {})
        
        # 基础标题（文件名不含扩展名）
        base_title = md_file.stem
        
        # 添加前缀
        prefix = notes_config.get('title_prefix', '')
        if prefix:
            base_title = f"{prefix}{base_title}"
        
        # 添加后缀
        suffix = notes_config.get('title_suffix', '')
        if suffix:
            base_title = f"{base_title}{suffix}"
        
        # 添加时间戳（如果启用）
        if notes_config.get('add_timestamp', False):
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_title = f"{base_title}_{timestamp}"
        
        return base_title
    
    def get_content(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        获取备忘录内容
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            处理后的备忘录内容
        """
        try:
            # 读取文件内容
            encoding = config.get('sync_rules', {}).get('encoding', 'utf-8')
            with open(md_file, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 添加源文件路径（如果启用）
            notes_config = config.get('notes_config', {})
            if notes_config.get('add_source_path', False):
                source_info = f"\\n\\n---\\n📁 源文件: {md_file}"
                content += source_info
            
            return content
            
        except UnicodeDecodeError as e:
            self.logger.error(f"文件编码错误: {md_file} - {e}")
            return f"❌ 文件编码错误，无法读取内容\\n文件路径: {md_file}"
        except Exception as e:
            self.logger.error(f"读取文件失败: {md_file} - {e}")
            return f"❌ 读取文件失败: {str(e)}\\n文件路径: {md_file}"
    
    def get_folder(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        获取目标文件夹名称
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            目标文件夹名称
        """
        # 默认文件夹
        default_folder = config.get('notes_config', {}).get('default_folder', 'Notes')
        
        # 文件夹映射
        folder_mappings = config.get('sync_rules', {}).get('folder_mappings', {})
        
        # 根据文件路径匹配文件夹
        file_path_str = str(md_file).lower()
        
        for keyword, folder_name in folder_mappings.items():
            if keyword == 'default':
                continue
            if keyword.lower() in file_path_str:
                return folder_name
        
        # 返回默认文件夹
        return folder_mappings.get('default', default_folder)
    
    def should_ignore_file(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """
        检查文件是否应该被忽略
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            如果应该忽略返回True，否则返回False
        """
        excluded_patterns = config.get('sync_rules', {}).get('excluded_patterns', [])
        
        file_name = md_file.name.lower()
        
        for pattern in excluded_patterns:
            pattern = pattern.lower()
            
            # 简单通配符匹配
            if pattern.startswith('*') and pattern.endswith('*'):
                # *pattern* - 包含匹配
                if pattern[1:-1] in file_name:
                    return True
            elif pattern.startswith('*'):
                # *pattern - 后缀匹配
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith('*'):
                # pattern* - 前缀匹配
                if file_name.startswith(pattern[:-1]):
                    return True
            else:
                # 完全匹配
                if file_name == pattern:
                    return True
        
        return False
    
    def check_file_size(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """
        检查文件大小是否超限
        
        Args:
            md_file: MD文件路径
            config: 配置字典
            
        Returns:
            如果文件大小合法返回True，否则返回False
        """
        max_size_mb = config.get('sync_rules', {}).get('max_file_size_mb', 50)
        
        try:
            file_size_mb = md_file.stat().st_size / (1024 * 1024)
            
            if file_size_mb > max_size_mb:
                self.logger.warning(f"文件大小超限: {md_file} ({file_size_mb:.2f}MB > {max_size_mb}MB)")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查文件大小失败: {md_file} - {e}")
            return False