#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD文档同步工具主入口
提供命令行界面和基本功能
"""

import argparse
import sys
from pathlib import Path
import json
from typing import List

from sync_engine import MDSyncEngine
from rules import (
    UpdateExistingRule,
    CreateNewRule,
    ForceCreateRule,
    ModifiedTodayRule,
    ModifiedSinceRule,
    CreatedTodayRule,
    TitlePrefixRule,
    ContentFilterRule,
    SizeLimitRule
)

def print_banner():
    """打印工具横幅"""
    banner = """
╭─────────────────────────────────────────────╮
│           🍎 Mac备忘录同步工具               │
│      将Markdown文档同步到macOS备忘录        │
╰─────────────────────────────────────────────╯
"""
    print(banner)

def create_engine_with_rules(config_path: str = None, rules_config: dict = None) -> MDSyncEngine:
    """
    创建配置好规则的同步引擎
    
    Args:
        config_path: 配置文件路径
        rules_config: 规则配置字典
        
    Returns:
        配置好的同步引擎
    """
    engine = MDSyncEngine(config_path)
    
    # 根据规则配置添加额外规则
    if rules_config:
        # 时间过滤规则
        if rules_config.get('only_today'):
            engine.add_rule(ModifiedTodayRule())
            print("✅ 已启用：仅同步今天修改的文件")
        
        if rules_config.get('only_created_today'):
            engine.add_rule(CreatedTodayRule())
            print("✅ 已启用：仅同步今天创建的文件")
        
        if rules_config.get('modified_since_hours'):
            hours = rules_config['modified_since_hours']
            engine.add_rule(ModifiedSinceRule(since_hours=hours))
            print(f"✅ 已启用：仅同步{hours}小时内修改的文件")
        
        # 内容过滤规则
        if rules_config.get('content_filters'):
            filters = rules_config['content_filters']
            engine.add_rule(ContentFilterRule(
                required_patterns=filters.get('required', []),
                excluded_patterns=filters.get('excluded', [])
            ))
            print("✅ 已启用：内容过滤规则")
        
        # 大小限制规则
        if rules_config.get('max_size_mb'):
            engine.add_rule(SizeLimitRule(max_size_mb=rules_config['max_size_mb']))
            print(f"✅ 已启用：文件大小限制 {rules_config['max_size_mb']}MB")
        
        # 同步模式
        sync_mode = rules_config.get('sync_mode', 'update')
        if sync_mode == 'create_only':
            # 移除更新规则，只保留创建规则
            engine.remove_rule('更新已存在的备忘录')
            engine.add_rule(CreateNewRule(priority=100))
            print("✅ 同步模式：仅创建新备忘录")
        elif sync_mode == 'force_create':
            engine.remove_rule('更新已存在的备忘录')
            engine.add_rule(ForceCreateRule(priority=100))
            print("✅ 同步模式：强制创建（允许重复）")
        else:
            print("✅ 同步模式：更新已存在的备忘录")
    
    return engine

def sync_file_command(args):
    """同步单个文件命令"""
    if not Path(args.file).exists():
        print(f"❌ 文件不存在: {args.file}")
        return False
    
    # 构建规则配置
    rules_config = {
        'only_today': args.only_today,
        'only_created_today': args.only_created_today,
        'sync_mode': args.mode,
        'max_size_mb': args.max_size
    }
    
    if args.modified_since:
        rules_config['modified_since_hours'] = args.modified_since
    
    engine = create_engine_with_rules(args.config, rules_config)
    
    print(f"🔄 开始同步文件: {Path(args.file).name}")
    success = engine.sync_file(args.file, dry_run=args.dry_run)
    
    if success:
        print("✅ 文件同步完成")
        return True
    else:
        print("❌ 文件同步失败")
        return False

def sync_folder_command(args):
    """同步文件夹命令"""
    if not Path(args.folder).exists():
        print(f"❌ 文件夹不存在: {args.folder}")
        return False
    
    # 构建规则配置
    rules_config = {
        'only_today': args.only_today,
        'only_created_today': args.only_created_today,
        'sync_mode': args.mode,
        'max_size_mb': args.max_size
    }
    
    if args.modified_since:
        rules_config['modified_since_hours'] = args.modified_since
    
    engine = create_engine_with_rules(args.config, rules_config)
    
    print(f"📁 开始批量同步文件夹: {args.folder}")
    stats = engine.sync_folder(args.folder, recursive=args.recursive, dry_run=args.dry_run)
    
    if 'error' in stats:
        print(f"❌ 同步失败: {stats['error']}")
        return False
    else:
        print("✅ 文件夹同步完成")
        return True

def sync_files_command(args):
    """同步文件列表命令"""
    files = []
    
    # 从命令行参数读取文件
    if args.files:
        files.extend(args.files)
    
    # 从文件读取文件列表
    if args.file_list:
        try:
            with open(args.file_list, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        files.append(line)
        except Exception as e:
            print(f"❌ 读取文件列表失败: {e}")
            return False
    
    if not files:
        print("❌ 没有指定要同步的文件")
        return False
    
    # 构建规则配置
    rules_config = {
        'only_today': args.only_today,
        'only_created_today': args.only_created_today,
        'sync_mode': args.mode,
        'max_size_mb': args.max_size
    }
    
    if args.modified_since:
        rules_config['modified_since_hours'] = args.modified_since
    
    engine = create_engine_with_rules(args.config, rules_config)
    
    print(f"📋 开始批量同步 {len(files)} 个文件")
    stats = engine.sync_files(files, dry_run=args.dry_run)
    
    print("✅ 批量同步完成")
    return True

def info_command(args):
    """显示信息命令"""
    engine = create_engine_with_rules(args.config)
    
    print("📊 备忘录信息:")
    info = engine.get_notes_info()
    
    if 'error' in info:
        print(f"❌ 获取信息失败: {info['error']}")
        return False
    
    print(f"   账户: {info['account']}")
    print(f"   文件夹数: {info['total_folders']}")
    print(f"   备忘录总数: {info['total_notes']}")
    print(f"   各文件夹备忘录数量:")
    
    for folder, count in info['folders'].items():
        print(f"     📁 {folder}: {count}")
    
    print("\n🔧 当前配置的同步规则:")
    rules = engine.list_rules()
    for i, rule in enumerate(rules, 1):
        status = "✅" if rule.enabled else "❌"
        print(f"   {i:2d}. {status} {rule.name} (优先级: {rule.priority})")
    
    return True

def config_command(args):
    """配置命令"""
    config_path = args.config or "config.json"
    
    if args.show:
        # 显示当前配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"📄 配置文件: {config_path}")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {config_path}")
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
        return True
    
    if args.validate:
        # 验证配置
        engine = MDSyncEngine(config_path)
        issues = engine.validate_config()
        
        if issues:
            print("❌ 配置验证失败:")
            for issue in issues:
                print(f"   • {issue}")
            return False
        else:
            print("✅ 配置验证通过")
            return True
    
    if args.init:
        # 初始化配置文件
        if Path(config_path).exists() and not args.force:
            print(f"❌ 配置文件已存在: {config_path}")
            print("使用 --force 参数强制覆盖")
            return False
        
        engine = MDSyncEngine()  # 使用默认配置
        default_config = engine.get_default_config()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"✅ 已创建配置文件: {config_path}")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False
    
    print("❌ 请指定配置操作 (--show, --validate, 或 --init)")
    return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MD文档同步工具 - 将Markdown文档同步到macOS备忘录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s sync-file document.md                    # 同步单个文件
  %(prog)s sync-folder ~/Documents --recursive      # 递归同步文件夹
  %(prog)s sync-files file1.md file2.md            # 同步多个文件
  %(prog)s info                                     # 显示备忘录信息
  %(prog)s config --init                           # 初始化配置文件
        """
    )
    
    # 全局参数
    parser.add_argument('-c', '--config', help='配置文件路径 (默认: config.json)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式（不实际执行）')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # sync-file 子命令
    file_parser = subparsers.add_parser('sync-file', help='同步单个文件')
    file_parser.add_argument('file', help='要同步的MD文件路径')
    file_parser.add_argument('--only-today', action='store_true', help='仅同步今天修改的文件')
    file_parser.add_argument('--only-created-today', action='store_true', help='仅同步今天创建的文件')
    file_parser.add_argument('--modified-since', type=int, metavar='HOURS', help='仅同步指定小时内修改的文件')
    file_parser.add_argument('--mode', choices=['update', 'create_only', 'force_create'], 
                           default='update', help='同步模式 (默认: update)')
    file_parser.add_argument('--max-size', type=float, metavar='MB', help='最大文件大小限制(MB)')
    
    # sync-folder 子命令
    folder_parser = subparsers.add_parser('sync-folder', help='同步文件夹')
    folder_parser.add_argument('folder', help='要同步的文件夹路径')
    folder_parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    folder_parser.add_argument('--only-today', action='store_true', help='仅同步今天修改的文件')
    folder_parser.add_argument('--only-created-today', action='store_true', help='仅同步今天创建的文件')
    folder_parser.add_argument('--modified-since', type=int, metavar='HOURS', help='仅同步指定小时内修改的文件')
    folder_parser.add_argument('--mode', choices=['update', 'create_only', 'force_create'], 
                             default='update', help='同步模式 (默认: update)')
    folder_parser.add_argument('--max-size', type=float, metavar='MB', help='最大文件大小限制(MB)')
    
    # sync-files 子命令
    files_parser = subparsers.add_parser('sync-files', help='同步多个文件')
    files_parser.add_argument('files', nargs='*', help='要同步的文件路径列表')
    files_parser.add_argument('-l', '--file-list', help='包含文件路径列表的文本文件')
    files_parser.add_argument('--only-today', action='store_true', help='仅同步今天修改的文件')
    files_parser.add_argument('--only-created-today', action='store_true', help='仅同步今天创建的文件')
    files_parser.add_argument('--modified-since', type=int, metavar='HOURS', help='仅同步指定小时内修改的文件')
    files_parser.add_argument('--mode', choices=['update', 'create_only', 'force_create'], 
                            default='update', help='同步模式 (默认: update)')
    files_parser.add_argument('--max-size', type=float, metavar='MB', help='最大文件大小限制(MB)')
    
    # info 子命令
    info_parser = subparsers.add_parser('info', help='显示备忘录和规则信息')
    
    # config 子命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--show', action='store_true', help='显示当前配置')
    config_group.add_argument('--validate', action='store_true', help='验证配置文件')
    config_group.add_argument('--init', action='store_true', help='初始化配置文件')
    config_parser.add_argument('--force', action='store_true', help='强制覆盖已存在的配置文件')
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定子命令，显示帮助
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # 显示横幅（除了config show命令）
    if not (args.command == 'config' and args.show):
        print_banner()
    
    # 执行对应的命令
    try:
        if args.command == 'sync-file':
            success = sync_file_command(args)
        elif args.command == 'sync-folder':
            success = sync_folder_command(args)
        elif args.command == 'sync-files':
            success = sync_files_command(args)
        elif args.command == 'info':
            success = info_command(args)
        elif args.command == 'config':
            success = config_command(args)
        else:
            print(f"❌ 未知命令: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()