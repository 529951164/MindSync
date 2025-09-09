#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude专用同步规则
针对Claude工作流程的特殊规则
"""

from pathlib import Path
from typing import Dict, Any
import re
from .base_rule import SyncRule
from utils import get_project_name_from_path, get_claude_folder_path

class ClaudeProjectMappingRule(SyncRule):
    """Claude项目文件夹映射规则"""
    
    def __init__(self, priority: int = 90):
        super().__init__("Claude项目文件夹映射", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则来处理Claude文件夹映射"""
        return self.enabled
    
    def get_folder(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        智能映射到Claude文件夹结构
        
        Claude/
        ├── Unity项目名/
        ├── Web项目名/
        ├── Other/           # 默认文件夹
        └── ...
        """
        # 尝试从路径中提取项目名称
        project_name = get_project_name_from_path(md_file)
        
        if project_name:
            # 清理项目名称，确保符合文件夹命名规范
            clean_name = self._clean_project_name(project_name)
            folder_path = f"Claude/{clean_name}"
            self.logger.debug(f"映射到项目文件夹: {md_file.name} -> {folder_path}")
            return folder_path
        else:
            # 没有识别到项目，使用默认文件夹
            self.logger.debug(f"使用默认文件夹: {md_file.name} -> Claude/Other")
            return "Claude/Other"
    
    def _clean_project_name(self, project_name: str) -> str:
        """
        清理项目名称，确保适合作为文件夹名
        
        Args:
            project_name: 原始项目名称
            
        Returns:
            清理后的项目名称
        """
        # 移除特殊字符，只保留字母数字和常见符号
        clean_name = re.sub(r'[^\w\s\-_.]', '', project_name)
        
        # 替换空格为下划线
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        # 移除连续的分隔符
        clean_name = re.sub(r'[_\-\.]+', '_', clean_name)
        
        # 去除首尾的分隔符
        clean_name = clean_name.strip('_-.')
        
        # 保持原始大小写，不强制首字母大写
        # clean_name = clean_name.capitalize()  # 移除这行
        
        return clean_name or "Unknown"
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """
        执行Claude文件夹映射，如果文件夹不存在则创建
        
        Args:
            md_file: MD文件路径
            apple_bridge: AppleScript桥接对象
            config: 配置字典
            
        Returns:
            执行成功返回True
        """
        folder_name = self.get_folder(md_file, config)
        
        # 检查文件夹是否存在
        existing_folders = apple_bridge.get_folders()
        
        if folder_name not in existing_folders:
            # 创建文件夹
            success = apple_bridge.create_folder(folder_name)
            if success:
                self.logger.info(f"📁 已创建Claude文件夹: {folder_name}")
            else:
                self.logger.error(f"❌ 创建Claude文件夹失败: {folder_name}")
                return False
        
        return True

class ClaudeTitleRule(SyncRule):
    """Claude文档标题规则"""
    
    def __init__(self, priority: int = 85):
        super().__init__("Claude文档标题规则", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则来处理标题"""
        return self.enabled
    
    def get_title(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        生成简洁的标题
        格式: 文档名（不含扩展名）
        """
        # 只返回文件名，不添加项目前缀
        return md_file.stem
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响标题生成，不执行实际同步"""
        return True

class ClaudeContentRule(SyncRule):
    """Claude文档内容增强规则"""
    
    def __init__(self, priority: int = 85):
        super().__init__("Claude内容增强", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则来处理内容"""
        return self.enabled
    
    def get_content(self, md_file: Path, config: Dict[str, Any]) -> str:
        """
        增强Claude文档内容，转换为备忘录友好格式
        """
        try:
            # 获取原始内容
            encoding = config.get('sync_rules', {}).get('encoding', 'utf-8')
            with open(md_file, 'r', encoding=encoding) as f:
                original_content = f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败: {md_file} - {e}")
            return f"❌ 读取文件失败: {str(e)}"
        
        # 导入转换器
        try:
            from markdown_converter import convert_markdown_for_notes
        except ImportError:
            # 如果转换器不可用，使用简化格式
            self.logger.warning("Markdown转换器不可用，使用简化格式")
            # 简化格式也需要使用<br><br>来确保文件名和内容分隔
            simple_content = original_content.replace('\n', '<br>')
            return f"{md_file.stem}<br><br>{simple_content}"
        
        # 第一行：只使用文件名（作为备忘录标题）
        title_line = md_file.stem
        
        # 转换Markdown内容为备忘录格式
        converted_content = convert_markdown_for_notes(original_content)
        
        # 组合内容：文件名 + 转换后的内容
        # 确保文件名和内容之间有明确的分隔，使用<br><br>而不是\n\n
        enhanced_content = f"{title_line}<br><br>{converted_content}"
        
        return enhanced_content
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则主要影响内容处理，不执行实际同步"""
        return True

class ClaudeAutoSyncRule(SyncRule):
    """Claude自动同步规则（集成其他规则的完整流程）"""
    
    def __init__(self, priority: int = 100):
        super().__init__("Claude自动同步", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查是否应该自动同步"""
        if not self.enabled:
            return False
        
        # 检查文件大小
        if not self.check_file_size(md_file, config):
            return False
        
        # 检查是否被忽略
        if self.should_ignore_file(md_file, config):
            return False
        
        return True
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """
        执行Claude完整同步流程
        1. 确保文件夹存在
        2. 生成标题和内容
        3. 执行同步
        """
        try:
            # 1. 获取目标文件夹并确保存在
            folder_mapping_rule = ClaudeProjectMappingRule()
            folder_name = folder_mapping_rule.get_folder(md_file, config)
            
            # 检查嵌套文件夹是否存在并创建
            folder_parts = [part.strip() for part in folder_name.split('/') if part.strip()]
            if not apple_bridge._folder_exists_at_path(folder_parts):
                if not apple_bridge.create_folder(folder_name):
                    self.logger.error(f"❌ 创建文件夹失败: {folder_name}")
                    return False
            
            # 2. 生成标题
            title_rule = ClaudeTitleRule()
            title = title_rule.get_title(md_file, config)
            
            # 3. 生成内容
            content_rule = ClaudeContentRule()
            content = content_rule.get_content(md_file, config)
            
            # 4. 执行同步
            auto_update = config.get('sync_rules', {}).get('auto_update', True)
            
            if auto_update and apple_bridge.note_exists(title, folder_name):
                # 更新已存在的备忘录
                success = apple_bridge.update_note(title, content, folder_name)
                if success:
                    self.logger.info(f"🔄 更新Claude文档: {title}")
            else:
                # 创建新备忘录
                success = apple_bridge.create_note(title, content, folder_name)
                if success:
                    self.logger.info(f"📝 创建Claude文档: {title}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Claude同步失败: {md_file} - {e}")
            return False