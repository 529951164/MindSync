#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础同步规则
包含最常用的同步规则实现
"""

from pathlib import Path
from typing import Dict, Any
from .base_rule import SyncRule

class UpdateExistingRule(SyncRule):
    """更新已存在的备忘录规则"""
    
    def __init__(self, priority: int = 100):
        super().__init__("更新已存在的备忘录", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """只有启用自动更新时才应用此规则"""
        if not self.enabled:
            return False
            
        # 检查是否启用自动更新
        return config.get('sync_rules', {}).get('auto_update', True)
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """执行更新或创建操作"""
        if self.should_ignore_file(md_file, config):
            self.logger.info(f"跳过被忽略的文件: {md_file.name}")
            return True
        
        if not self.check_file_size(md_file, config):
            return False
        
        title = self.get_title(md_file, config)
        content = self.get_content(md_file, config)
        folder = self.get_folder(md_file, config)
        
        # 检查备忘录是否已存在
        if apple_bridge.note_exists(title, folder):
            # 更新现有备忘录
            success = apple_bridge.update_note(title, content, folder)
            if success:
                self.logger.info(f"🔄 更新备忘录: {title}")
            return success
        else:
            # 创建新备忘录
            success = apple_bridge.create_note(title, content, folder)
            if success:
                self.logger.info(f"📝 创建备忘录: {title}")
            return success

class CreateNewRule(SyncRule):
    """仅创建新备忘录规则（不更新已存在的）"""
    
    def __init__(self, priority: int = 80):
        super().__init__("仅创建新备忘录", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则"""
        return self.enabled
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """仅在备忘录不存在时创建"""
        if self.should_ignore_file(md_file, config):
            self.logger.info(f"跳过被忽略的文件: {md_file.name}")
            return True
        
        if not self.check_file_size(md_file, config):
            return False
        
        title = self.get_title(md_file, config)
        content = self.get_content(md_file, config)
        folder = self.get_folder(md_file, config)
        
        # 只有当备忘录不存在时才创建
        if not apple_bridge.note_exists(title, folder):
            success = apple_bridge.create_note(title, content, folder)
            if success:
                self.logger.info(f"📝 创建新备忘录: {title}")
            return success
        else:
            self.logger.info(f"⏭️ 跳过已存在的备忘录: {title}")
            return True

class ForceCreateRule(SyncRule):
    """强制创建规则（总是创建新的，允许重复）"""
    
    def __init__(self, priority: int = 60):
        super().__init__("强制创建备忘录", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """总是应用此规则"""
        return self.enabled
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """强制创建新备忘录"""
        if self.should_ignore_file(md_file, config):
            self.logger.info(f"跳过被忽略的文件: {md_file.name}")
            return True
        
        if not self.check_file_size(md_file, config):
            return False
        
        title = self.get_title(md_file, config)
        content = self.get_content(md_file, config)
        folder = self.get_folder(md_file, config)
        
        # 总是创建新的备忘录
        success = apple_bridge.create_note(title, content, folder)
        if success:
            self.logger.info(f"📝 强制创建备忘录: {title}")
        return success

class FileTypeRule(SyncRule):
    """文件类型过滤规则"""
    
    def __init__(self, allowed_extensions: list = None, priority: int = 90):
        super().__init__("文件类型过滤", priority)
        self.allowed_extensions = allowed_extensions or ['.md', '.markdown', '.txt']
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件扩展名"""
        if not self.enabled:
            return False
        
        return md_file.suffix.lower() in self.allowed_extensions
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """文件类型规则不执行实际同步，只做过滤"""
        return True

class BackupRule(SyncRule):
    """备份规则（更新前备份原内容）"""
    
    def __init__(self, priority: int = 110):
        super().__init__("更新前备份", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查是否启用备份"""
        if not self.enabled:
            return False
        
        return config.get('sync_rules', {}).get('backup_before_update', False)
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """在更新前创建备份"""
        title = self.get_title(md_file, config)
        folder = self.get_folder(md_file, config)
        
        # 如果备忘录存在，先备份
        if apple_bridge.note_exists(title, folder):
            note_info = apple_bridge.get_note_info(title, folder)
            if note_info:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_title = f"{title}_backup_{timestamp}"
                
                success = apple_bridge.create_note(
                    backup_title, 
                    note_info.get('body', ''), 
                    folder
                )
                
                if success:
                    self.logger.info(f"💾 创建备份: {backup_title}")
                    return True
                else:
                    self.logger.error(f"❌ 备份失败: {backup_title}")
                    return False
        
        return True

class DryRunRule(SyncRule):
    """试运行规则（仅打印操作，不实际执行）"""
    
    def __init__(self, priority: int = 200):
        super().__init__("试运行模式", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查是否启用试运行模式"""
        return self.enabled and config.get('dry_run', False)
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """仅打印会执行的操作"""
        if self.should_ignore_file(md_file, config):
            print(f"🔸 [DRY RUN] 会跳过: {md_file.name}")
            return True
        
        title = self.get_title(md_file, config)
        folder = self.get_folder(md_file, config)
        
        if apple_bridge.note_exists(title, folder):
            print(f"🔄 [DRY RUN] 会更新备忘录: {title} (文件夹: {folder})")
        else:
            print(f"📝 [DRY RUN] 会创建备忘录: {title} (文件夹: {folder})")
        
        return True