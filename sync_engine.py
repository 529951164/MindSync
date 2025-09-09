#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD文档同步引擎
核心同步逻辑，管理规则和执行同步
"""

import json
import logging
import logging.handlers
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from apple_bridge import AppleScriptBridge
from rules import (
    SyncRule, 
    UpdateExistingRule,
    CreateNewRule,
    FileTypeRule,
    FolderMappingRule,
    TitlePrefixRule,
    ClaudeAutoSyncRule
)

class MDSyncEngine:
    """MD文档同步引擎"""
    
    def __init__(self, config_path: str = None):
        """
        初始化同步引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "config.json"
        self.config = self.load_config()
        
        # 设置日志
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化AppleScript桥接
        notes_config = self.config.get('notes_config', {})
        self.apple_bridge = AppleScriptBridge(
            account=notes_config.get('account', 'iCloud'),
            default_folder=notes_config.get('default_folder', 'Notes')
        )
        
        # 初始化规则列表
        self.rules: List[SyncRule] = []
        self.setup_default_rules()
        
        self.logger.info("MD同步引擎初始化完成")
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ 已加载配置文件: {self.config_path}")
                    return config
            else:
                print(f"⚠️ 配置文件不存在: {self.config_path}，使用默认配置")
                return self.get_default_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "sync_rules": {
                "auto_update": True,
                "backup_before_update": False,
                "max_file_size_mb": 50,
                "encoding": "utf-8",
                "excluded_patterns": ["*.tmp.md", "*draft*", ".*", "_*"],
                "folder_mappings": {
                    "work": "工作笔记",
                    "personal": "个人笔记", 
                    "tech": "技术文档",
                    "claude": "Claude文档",
                    "default": "Notes"
                }
            },
            "notes_config": {
                "account": "iCloud",
                "default_folder": "Notes",
                "title_prefix": "",
                "title_suffix": "",
                "add_timestamp": False,
                "add_source_path": True
            },
            "logging": {
                "level": "INFO",
                "log_file": "logs/sync.log",
                "max_log_size_mb": 10,
                "backup_count": 5,
                "console_output": True
            }
        }
    
    def setup_logging(self):
        """设置日志系统"""
        log_config = self.config.get('logging', {})
        
        # 创建logs目录
        log_file = Path(log_config.get('log_file', 'logs/sync.log'))
        log_file.parent.mkdir(exist_ok=True)
        
        # 配置root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # 清除已有的处理器
        root_logger.handlers.clear()
        
        # 文件处理器（带轮转）
        max_size = log_config.get('max_log_size_mb', 10) * 1024 * 1024
        backup_count = log_config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 控制台处理器
        if log_config.get('console_output', True):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
    
    def setup_default_rules(self):
        """设置默认同步规则"""
        # 基础规则（按优先级排序）
        default_rules = [
            FileTypeRule(priority=95),                    # 文件类型过滤
            ClaudeAutoSyncRule(priority=100)              # Claude完整同步流程
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
        
        self.logger.info(f"已设置 {len(default_rules)} 个默认规则（包含Claude专用规则）")
    
    def add_rule(self, rule: SyncRule):
        """
        添加同步规则
        
        Args:
            rule: 同步规则实例
        """
        self.rules.append(rule)
        # 按优先级排序（优先级高的先执行）
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        self.logger.debug(f"添加规则: {rule}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        移除指定名称的规则
        
        Args:
            rule_name: 规则名称
            
        Returns:
            移除成功返回True
        """
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        
        success = len(self.rules) < original_count
        if success:
            self.logger.info(f"已移除规则: {rule_name}")
        else:
            self.logger.warning(f"规则不存在: {rule_name}")
        
        return success
    
    def list_rules(self) -> List[SyncRule]:
        """获取所有规则列表"""
        return self.rules.copy()
    
    def enable_rule(self, rule_name: str) -> bool:
        """启用规则"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                self.logger.info(f"已启用规则: {rule_name}")
                return True
        
        self.logger.warning(f"规则不存在: {rule_name}")
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """禁用规则"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                self.logger.info(f"已禁用规则: {rule_name}")
                return True
        
        self.logger.warning(f"规则不存在: {rule_name}")
        return False
    
    def sync_file(self, md_file_path: str, dry_run: bool = False) -> bool:
        """
        同步单个文件
        
        Args:
            md_file_path: MD文件路径
            dry_run: 是否只是试运行（不实际执行）
            
        Returns:
            同步成功返回True
        """
        md_file = Path(md_file_path)
        
        if not md_file.exists():
            self.logger.error(f"❌ 文件不存在: {md_file}")
            return False
        
        if not md_file.is_file():
            self.logger.error(f"❌ 不是文件: {md_file}")
            return False
        
        self.logger.info(f"开始同步文件: {md_file.name}")
        
        # 设置试运行配置
        config = self.config.copy()
        if dry_run:
            config['dry_run'] = True
            self.logger.info("🔸 试运行模式")
        
        # 应用所有规则
        success_count = 0
        applied_rules = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # 检查规则是否应该应用
                if rule.should_apply(md_file, config):
                    applied_rules.append(rule.name)
                    
                    # 执行规则
                    if not dry_run:
                        success = rule.execute(md_file, self.apple_bridge, config)
                        if success:
                            success_count += 1
                        else:
                            self.logger.error(f"❌ 规则执行失败: {rule.name}")
                    else:
                        # 试运行模式
                        rule.execute(md_file, self.apple_bridge, config)
                        success_count += 1
                
            except Exception as e:
                self.logger.error(f"❌ 规则执行异常: {rule.name} - {e}")
        
        if applied_rules:
            self.logger.info(f"应用了 {len(applied_rules)} 个规则: {', '.join(applied_rules)}")
            
            if not dry_run:
                if success_count > 0:
                    self.logger.info(f"✅ 同步完成: {md_file.name}")
                    return True
                else:
                    self.logger.error(f"❌ 所有规则执行失败: {md_file.name}")
                    return False
            else:
                self.logger.info(f"🔸 试运行完成: {md_file.name}")
                return True
        else:
            self.logger.info(f"⏭️ 没有适用的规则: {md_file.name}")
            return True
    
    def sync_folder(self, folder_path: str, recursive: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        """
        批量同步文件夹
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归处理子目录
            dry_run: 是否只是试运行
            
        Returns:
            同步统计信息
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            self.logger.error(f"❌ 文件夹不存在: {folder}")
            return {'error': '文件夹不存在'}
        
        if not folder.is_dir():
            self.logger.error(f"❌ 不是文件夹: {folder}")
            return {'error': '不是文件夹'}
        
        self.logger.info(f"开始批量同步: {folder}")
        
        # 查找MD文件
        if recursive:
            md_files = list(folder.rglob("*.md"))
        else:
            md_files = list(folder.glob("*.md"))
        
        self.logger.info(f"找到 {len(md_files)} 个MD文件")
        
        # 统计信息
        stats = {
            'total_files': len(md_files),
            'success_count': 0,
            'failure_count': 0,
            'skipped_count': 0,
            'start_time': datetime.now(),
            'processed_files': []
        }
        
        # 处理每个文件
        for md_file in md_files:
            try:
                success = self.sync_file(str(md_file), dry_run)
                
                file_info = {
                    'path': str(md_file),
                    'name': md_file.name,
                    'success': success,
                    'timestamp': datetime.now()
                }
                
                if success:
                    stats['success_count'] += 1
                else:
                    stats['failure_count'] += 1
                
                stats['processed_files'].append(file_info)
                
            except Exception as e:
                self.logger.error(f"❌ 处理文件异常: {md_file} - {e}")
                stats['failure_count'] += 1
                
                stats['processed_files'].append({
                    'path': str(md_file),
                    'name': md_file.name,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        # 完成统计
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        # 输出统计结果
        self.logger.info(f"📊 批量同步完成:")
        self.logger.info(f"   总文件数: {stats['total_files']}")
        self.logger.info(f"   成功: {stats['success_count']}")
        self.logger.info(f"   失败: {stats['failure_count']}")
        self.logger.info(f"   耗时: {stats['duration']:.2f}秒")
        
        return stats
    
    def sync_files(self, file_paths: List[str], dry_run: bool = False) -> Dict[str, Any]:
        """
        批量同步指定文件列表
        
        Args:
            file_paths: 文件路径列表
            dry_run: 是否只是试运行
            
        Returns:
            同步统计信息
        """
        self.logger.info(f"开始批量同步 {len(file_paths)} 个文件")
        
        stats = {
            'total_files': len(file_paths),
            'success_count': 0,
            'failure_count': 0,
            'start_time': datetime.now(),
            'processed_files': []
        }
        
        for file_path in file_paths:
            try:
                success = self.sync_file(file_path, dry_run)
                
                file_info = {
                    'path': file_path,
                    'name': Path(file_path).name,
                    'success': success,
                    'timestamp': datetime.now()
                }
                
                if success:
                    stats['success_count'] += 1
                else:
                    stats['failure_count'] += 1
                
                stats['processed_files'].append(file_info)
                
            except Exception as e:
                self.logger.error(f"❌ 处理文件异常: {file_path} - {e}")
                stats['failure_count'] += 1
                
                stats['processed_files'].append({
                    'path': file_path,
                    'name': Path(file_path).name,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        self.logger.info(f"📊 批量同步完成: 成功 {stats['success_count']}/{stats['total_files']}")
        
        return stats
    
    def get_notes_info(self) -> Dict[str, Any]:
        """获取备忘录应用信息"""
        try:
            folders = self.apple_bridge.get_folders()
            total_notes = 0
            
            folder_info = {}
            for folder in folders:
                notes = self.apple_bridge.get_existing_notes(folder)
                folder_info[folder] = len(notes)
                total_notes += len(notes)
            
            return {
                'total_folders': len(folders),
                'total_notes': total_notes,
                'folders': folder_info,
                'account': self.apple_bridge.account
            }
            
        except Exception as e:
            self.logger.error(f"获取备忘录信息失败: {e}")
            return {'error': str(e)}
    
    def validate_config(self) -> List[str]:
        """验证配置文件"""
        issues = []
        
        # 检查必需的配置项
        required_configs = [
            ('sync_rules', dict),
            ('notes_config', dict),
            ('logging', dict)
        ]
        
        for key, expected_type in required_configs:
            if key not in self.config:
                issues.append(f"缺少配置项: {key}")
            elif not isinstance(self.config[key], expected_type):
                issues.append(f"配置项类型错误: {key} 应该是 {expected_type.__name__}")
        
        # 检查文件大小限制
        max_size = self.config.get('sync_rules', {}).get('max_file_size_mb')
        if max_size is not None and (not isinstance(max_size, (int, float)) or max_size <= 0):
            issues.append("max_file_size_mb 应该是正数")
        
        # 检查日志配置
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            issues.append(f"无效的日志级别: {log_level}，应该是 {valid_levels} 之一")
        
        return issues