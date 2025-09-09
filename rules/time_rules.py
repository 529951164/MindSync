#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间相关的同步规则
根据文件的时间属性决定是否同步
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta
from .base_rule import SyncRule

class ModifiedTodayRule(SyncRule):
    """今天修改过的文件规则"""
    
    def __init__(self, priority: int = 70):
        super().__init__("仅同步今天修改的文件", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件是否在今天修改过"""
        if not self.enabled:
            return False
        
        try:
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            today = datetime.now().date()
            
            # 检查是否是今天修改的
            return mtime.date() == today
            
        except Exception as e:
            self.logger.error(f"检查文件修改时间失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """执行同步"""
        # 使用更新规则的逻辑
        from .basic_rules import UpdateExistingRule
        update_rule = UpdateExistingRule()
        return update_rule.execute(md_file, apple_bridge, config)

class ModifiedSinceRule(SyncRule):
    """指定时间后修改的文件规则"""
    
    def __init__(self, since_hours: int = 24, priority: int = 70):
        """
        Args:
            since_hours: 多少小时内修改的文件才同步
        """
        super().__init__(f"同步{since_hours}小时内修改的文件", priority)
        self.since_hours = since_hours
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件是否在指定时间内修改过"""
        if not self.enabled:
            return False
        
        try:
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(hours=self.since_hours)
            
            # 检查是否在指定时间内修改的
            return mtime >= cutoff_time
            
        except Exception as e:
            self.logger.error(f"检查文件修改时间失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """执行同步"""
        from .basic_rules import UpdateExistingRule
        update_rule = UpdateExistingRule()
        return update_rule.execute(md_file, apple_bridge, config)

class CreatedTodayRule(SyncRule):
    """今天创建的文件规则"""
    
    def __init__(self, priority: int = 70):
        super().__init__("仅同步今天创建的文件", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件是否在今天创建"""
        if not self.enabled:
            return False
        
        try:
            # 获取文件创建时间
            ctime = datetime.fromtimestamp(md_file.stat().st_ctime)
            today = datetime.now().date()
            
            # 检查是否是今天创建的
            return ctime.date() == today
            
        except Exception as e:
            self.logger.error(f"检查文件创建时间失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """执行同步"""
        from .basic_rules import UpdateExistingRule
        update_rule = UpdateExistingRule()
        return update_rule.execute(md_file, apple_bridge, config)

class CreatedSinceRule(SyncRule):
    """指定时间后创建的文件规则"""
    
    def __init__(self, since_hours: int = 24, priority: int = 70):
        """
        Args:
            since_hours: 多少小时内创建的文件才同步
        """
        super().__init__(f"同步{since_hours}小时内创建的文件", priority)
        self.since_hours = since_hours
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件是否在指定时间内创建"""
        if not self.enabled:
            return False
        
        try:
            # 获取文件创建时间
            ctime = datetime.fromtimestamp(md_file.stat().st_ctime)
            cutoff_time = datetime.now() - timedelta(hours=self.since_hours)
            
            # 检查是否在指定时间内创建的
            return ctime >= cutoff_time
            
        except Exception as e:
            self.logger.error(f"检查文件创建时间失败: {md_file} - {e}")
            return False
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """执行同步"""
        from .basic_rules import UpdateExistingRule
        update_rule = UpdateExistingRule()
        return update_rule.execute(md_file, apple_bridge, config)

class NotModifiedRecentlyRule(SyncRule):
    """排除最近修改的文件规则（用于避免频繁同步）"""
    
    def __init__(self, exclude_minutes: int = 5, priority: int = 85):
        """
        Args:
            exclude_minutes: 排除多少分钟内修改的文件
        """
        super().__init__(f"排除{exclude_minutes}分钟内修改的文件", priority)
        self.exclude_minutes = exclude_minutes
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查文件是否应该被排除（太新的文件）"""
        if not self.enabled:
            return True  # 不启用时允许所有文件
        
        try:
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(minutes=self.exclude_minutes)
            
            # 如果文件修改时间太新，则排除
            if mtime > cutoff_time:
                self.logger.debug(f"排除最近修改的文件: {md_file.name}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查文件修改时间失败: {md_file} - {e}")
            return True  # 出错时允许同步
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则不执行实际同步，只做过滤"""
        return True

class WeekdayOnlyRule(SyncRule):
    """仅工作日同步规则"""
    
    def __init__(self, priority: int = 75):
        super().__init__("仅工作日同步", priority)
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查今天是否是工作日"""
        if not self.enabled:
            return True
        
        # 0-6: 周一到周日，0-4是工作日
        today_weekday = datetime.now().weekday()
        is_weekday = today_weekday < 5
        
        if not is_weekday:
            self.logger.debug("今天是周末，跳过同步")
        
        return is_weekday
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则不执行实际同步，只做过滤"""
        return True

class BusinessHoursRule(SyncRule):
    """仅工作时间同步规则"""
    
    def __init__(self, start_hour: int = 9, end_hour: int = 18, priority: int = 75):
        """
        Args:
            start_hour: 开始小时 (24小时制)
            end_hour: 结束小时 (24小时制)
        """
        super().__init__(f"仅在{start_hour:02d}:00-{end_hour:02d}:00同步", priority)
        self.start_hour = start_hour
        self.end_hour = end_hour
    
    def should_apply(self, md_file: Path, config: Dict[str, Any]) -> bool:
        """检查当前时间是否在工作时间内"""
        if not self.enabled:
            return True
        
        current_hour = datetime.now().hour
        is_business_hours = self.start_hour <= current_hour < self.end_hour
        
        if not is_business_hours:
            self.logger.debug(f"当前时间 {current_hour:02d}:xx 不在工作时间内")
        
        return is_business_hours
    
    def execute(self, md_file: Path, apple_bridge, config: Dict[str, Any]) -> bool:
        """此规则不执行实际同步，只做过滤"""
        return True