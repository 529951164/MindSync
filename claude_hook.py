#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Hook集成脚本
用于与Claude Code的Hook系统集成，自动同步MD文档
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional

# 添加当前目录到Python路径，确保能导入模块
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from sync_engine import MDSyncEngine

def is_markdown_file(file_path: str) -> bool:
    """检查文件是否为Markdown文件"""
    return file_path.lower().endswith(('.md', '.markdown'))

def should_sync_file(file_path: str, config: dict = None) -> bool:
    """
    检查文件是否应该同步
    
    Args:
        file_path: 文件路径
        config: 配置字典
        
    Returns:
        如果应该同步返回True
    """
    path = Path(file_path)
    
    # 检查文件是否存在
    if not path.exists() or not path.is_file():
        return False
    
    # 检查是否为Markdown文件
    if not is_markdown_file(file_path):
        return False
    
    # 检查配置中的观察模式
    if config:
        claude_hook_config = config.get('claude_hook', {})
        
        # 检查是否启用
        if not claude_hook_config.get('enabled', True):
            return False
        
        # 检查文件模式
        watch_patterns = claude_hook_config.get('watch_patterns', ['*.md'])
        if not any(path.match(pattern) for pattern in watch_patterns):
            return False
    
    return True

def sync_file_hook(file_path: str, hook_type: str = 'save', config_path: str = None) -> bool:
    """
    Hook函数：同步单个文件
    
    Args:
        file_path: 文件路径
        hook_type: Hook类型 ('save', 'create', 'modify')
        config_path: 配置文件路径
        
    Returns:
        同步成功返回True
    """
    try:
        # 检查是否应该同步
        engine = MDSyncEngine(config_path)
        
        if not should_sync_file(file_path, engine.config):
            print(f"🔸 跳过非Markdown文件: {Path(file_path).name}")
            return True
        
        # 检查延迟配置
        claude_hook_config = engine.config.get('claude_hook', {})
        delay_seconds = claude_hook_config.get('delay_seconds', 2)
        
        if delay_seconds > 0:
            import time
            print(f"⏳ 等待{delay_seconds}秒后同步...")
            time.sleep(delay_seconds)
        
        # 执行同步
        print(f"🔄 Hook触发同步: {Path(file_path).name} ({hook_type})")
        success = engine.sync_file(file_path)
        
        if success:
            print(f"✅ Hook同步完成: {Path(file_path).name}")
        else:
            print(f"❌ Hook同步失败: {Path(file_path).name}")
        
        return success
        
    except Exception as e:
        print(f"❌ Hook同步异常: {e}")
        return False

def sync_multiple_files_hook(file_paths: List[str], hook_type: str = 'batch', config_path: str = None) -> bool:
    """
    Hook函数：批量同步多个文件
    
    Args:
        file_paths: 文件路径列表
        hook_type: Hook类型
        config_path: 配置文件路径
        
    Returns:
        全部同步成功返回True
    """
    try:
        engine = MDSyncEngine(config_path)
        
        # 过滤出需要同步的Markdown文件
        md_files = [f for f in file_paths if should_sync_file(f, engine.config)]
        
        if not md_files:
            print("🔸 没有需要同步的Markdown文件")
            return True
        
        print(f"🔄 Hook批量同步 {len(md_files)} 个文件")
        
        # 检查延迟配置
        claude_hook_config = engine.config.get('claude_hook', {})
        delay_seconds = claude_hook_config.get('delay_seconds', 2)
        
        if delay_seconds > 0:
            import time
            print(f"⏳ 等待{delay_seconds}秒后同步...")
            time.sleep(delay_seconds)
        
        # 批量同步
        stats = engine.sync_files(md_files)
        
        success = stats['success_count'] == len(md_files)
        
        if success:
            print(f"✅ Hook批量同步完成: {stats['success_count']}/{len(md_files)}")
        else:
            print(f"⚠️ Hook批量同步部分失败: {stats['success_count']}/{len(md_files)}")
        
        return success
        
    except Exception as e:
        print(f"❌ Hook批量同步异常: {e}")
        return False

def create_hook_script(script_path: str, config_path: str = None) -> bool:
    """
    创建Hook脚本文件
    
    Args:
        script_path: Hook脚本保存路径
        config_path: 配置文件路径
        
    Returns:
        创建成功返回True
    """
    try:
        # Hook脚本模板
        script_template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Hook脚本
自动生成的文档同步Hook
"""

import sys
from pathlib import Path

# 添加同步工具路径
tool_path = Path(r"{current_dir.absolute()}")
if str(tool_path) not in sys.path:
    sys.path.insert(0, str(tool_path))

from claude_hook import sync_file_hook, sync_multiple_files_hook

def main():
    """主函数 - Claude Hook入口点"""
    if len(sys.argv) < 2:
        print("用法: python hook_script.py <文件路径> [hook类型]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    hook_type = sys.argv[2] if len(sys.argv) > 2 else "save"
    
    config_path = r"{config_path or (current_dir / 'config.json').absolute()}"
    
    # 执行同步
    success = sync_file_hook(file_path, hook_type, config_path)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
        
        # 写入Hook脚本
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_template)
        
        # 设置执行权限（在类Unix系统上）
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
        
        print(f"✅ 已创建Hook脚本: {script_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建Hook脚本失败: {e}")
        return False

def install_claude_hook(hook_name: str = "md_sync", config_path: str = None) -> bool:
    """
    安装Claude Code Hook
    
    Args:
        hook_name: Hook名称
        config_path: 配置文件路径
        
    Returns:
        安装成功返回True
    """
    try:
        # Claude Code配置目录（通常在用户home目录下）
        claude_config_dir = Path.home() / '.claude'
        
        if not claude_config_dir.exists():
            claude_config_dir = Path.home() / '.config' / 'claude'
        
        if not claude_config_dir.exists():
            print("❌ 找不到Claude Code配置目录")
            print("请确保Claude Code已正确安装")
            return False
        
        # Hook脚本路径
        hook_script_path = current_dir / f"claude_hook_{hook_name}.py"
        
        # 创建Hook脚本
        if not create_hook_script(str(hook_script_path), config_path):
            return False
        
        # Claude Code Hook配置
        hook_config = {
            "name": f"MD文档同步 ({hook_name})",
            "description": "自动同步Markdown文档到Mac备忘录",
            "trigger": "file_save",
            "script": str(hook_script_path.absolute()),
            "file_patterns": ["*.md", "*.markdown"],
            "enabled": True
        }
        
        print(f"📋 Hook配置:")
        print(json.dumps(hook_config, indent=2, ensure_ascii=False))
        print()
        print(f"请将以上配置添加到Claude Code的Hook配置中")
        print(f"Hook脚本路径: {hook_script_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 安装Claude Hook失败: {e}")
        return False

def test_hook(test_file: str = None, config_path: str = None) -> bool:
    """
    测试Hook功能
    
    Args:
        test_file: 测试文件路径
        config_path: 配置文件路径
        
    Returns:
        测试成功返回True
    """
    try:
        print("🧪 开始测试Hook功能...")
        
        # 如果没有提供测试文件，创建一个临时测试文件
        if not test_file:
            test_file = current_dir / "test_hook_document.md"
            test_content = f"""# Hook测试文档

这是一个用于测试Claude Hook功能的临时文档。

## 测试信息
- 创建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 工具版本: Claude MD同步工具 v1.0
- 测试类型: Hook集成测试

## 功能验证
- [x] Hook脚本创建
- [x] 文件路径识别  
- [x] 项目名称提取
- [x] 备忘录同步

测试完成后此文档将被删除。
"""
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            print(f"📝 已创建测试文件: {test_file}")
            
            # 标记需要清理
            cleanup_test_file = True
        else:
            cleanup_test_file = False
        
        # 执行Hook测试
        success = sync_file_hook(str(test_file), "test", config_path)
        
        if cleanup_test_file and Path(test_file).exists():
            try:
                Path(test_file).unlink()
                print(f"🗑️ 已清理测试文件: {test_file}")
            except Exception as e:
                print(f"⚠️ 清理测试文件失败: {e}")
        
        if success:
            print("✅ Hook功能测试通过")
            return True
        else:
            print("❌ Hook功能测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Hook测试异常: {e}")
        return False

def handle_claude_hook(debug: bool = False, config_path: str = None) -> bool:
    """
    处理Claude Code Hook调用
    从stdin读取JSON数���，解析工具使用信息并同步相应文件
    
    Args:
        debug: 是否开启调试模式
        config_path: 配置文件路径
        
    Returns:
        处理成功返回True
    """
    try:
        import json
        import sys
        
        # 从stdin读取Hook数据
        hook_data = ""
        for line in sys.stdin:
            hook_data += line
        
        if debug:
            print(f"🔍 Hook输入数据: {hook_data}", file=sys.stderr)
        
        if not hook_data.strip():
            if debug:
                print("⚠️ 未收到Hook数据", file=sys.stderr)
            return True
        
        # 解析JSON数据
        try:
            data = json.loads(hook_data)
        except json.JSONDecodeError as e:
            if debug:
                print(f"❌ JSON解析失败: {e}", file=sys.stderr)
            return False
        
        # 检查是否是Write或Edit工具
        tool_name = data.get('tool', {}).get('name', '')
        if tool_name not in ['Write', 'Edit']:
            if debug:
                print(f"🔸 跳过非Write/Edit工具: {tool_name}", file=sys.stderr)
            return True
        
        # 获取文件路径
        tool_params = data.get('tool', {}).get('parameters', {})
        file_path = tool_params.get('file_path', '')
        
        if not file_path:
            if debug:
                print("⚠️ 未找到文件路径", file=sys.stderr)
            return True
        
        # 检查是否是Markdown文件
        if not file_path.lower().endswith(('.md', '.markdown')):
            if debug:
                print(f"🔸 跳过非Markdown文件: {file_path}", file=sys.stderr)
            return True
        
        if debug:
            print(f"🔄 开始同步MD文件: {file_path}", file=sys.stderr)
        
        # 执行同步
        success = sync_file_hook(file_path, "hook", config_path)
        
        if debug:
            status = "成功" if success else "失败"
            print(f"✅ Hook同步{status}: {file_path}", file=sys.stderr)
        
        return success
        
    except Exception as e:
        if debug:
            print(f"❌ Hook处理异常: {e}", file=sys.stderr)
        return False

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description='Claude Hook集成脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s sync file.md                    # 同步单个文件
  %(prog)s batch file1.md file2.md         # 批量同步
  %(prog)s install                         # 安装Hook
  %(prog)s test                           # 测试Hook功能
        """
    )
    
    parser.add_argument('-c', '--config', help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # sync命令
    sync_parser = subparsers.add_parser('sync', help='同步单个文件')
    sync_parser.add_argument('file', help='要同步的文件路径')
    sync_parser.add_argument('--hook-type', default='save', help='Hook类型')
    
    # batch命令  
    batch_parser = subparsers.add_parser('batch', help='批量同步文件')
    batch_parser.add_argument('files', nargs='+', help='要同步的文件路径列表')
    
    # install命令
    install_parser = subparsers.add_parser('install', help='安装Claude Hook')
    install_parser.add_argument('--name', default='md_sync', help='Hook名称')
    
    # test命令
    test_parser = subparsers.add_parser('test', help='测试Hook功能')
    test_parser.add_argument('--file', help='测试文件路径')
    
    # hook命令 - Claude Code Hook处理
    hook_parser = subparsers.add_parser('hook', help='处理Claude Code Hook调用')
    hook_parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'sync':
            success = sync_file_hook(args.file, args.hook_type, args.config)
        elif args.command == 'batch':
            success = sync_multiple_files_hook(args.files, 'batch', args.config)
        elif args.command == 'install':
            success = install_claude_hook(args.name, args.config)
        elif args.command == 'test':
            success = test_hook(args.file, args.config)
        elif args.command == 'hook':
            success = handle_claude_hook(args.debug, args.config)
        else:
            print(f"❌ 未知命令: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()