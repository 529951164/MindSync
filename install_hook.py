#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Hook 一键安装脚本
快速配置Markdown文档自动同步到Mac备忘录功能
"""

import os
import sys
import json
import shutil
from pathlib import Path

def check_prerequisites():
    """检查安装前置条件"""
    print("🔍 检查安装环境...")
    
    issues = []
    
    # 检查macOS
    if sys.platform != "darwin":
        issues.append("❌ 此工具只支持macOS系统")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        issues.append("❌ 需要Python 3.7或更高版本")
    
    # 检查Claude Code配置目录
    claude_config_dir = Path.home() / '.claude'
    if not claude_config_dir.exists():
        issues.append("❌ Claude Code配置目录不存在，请确保Claude Code已正确安装")
    
    # 检查备忘录应用
    try:
        os.system("osascript -e 'tell application \"Notes\" to activate' >/dev/null 2>&1")
        print("✅ 备忘录应用访问正常")
    except:
        issues.append("⚠️ 无法访问备忘录应用，可能需要授权")
    
    if issues:
        print("\\n发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("✅ 环境检查通过")
    return True

def backup_claude_settings():
    """备份Claude设置"""
    settings_file = Path.home() / '.claude' / 'settings.json'
    
    if settings_file.exists():
        backup_file = settings_file.with_suffix('.json.backup')
        shutil.copy2(settings_file, backup_file)
        print(f"✅ 已备份Claude设置到: {backup_file}")
        return True
    else:
        print("⚠️ Claude设置文件不存在，将创建新的配置")
        return False

def get_tool_path():
    """获取工具路径"""
    current_path = Path(__file__).parent.absolute()
    hook_script = current_path / 'claude_hook_mindsync.py'
    
    if not hook_script.exists():
        print(f"❌ Hook脚本不存在: {hook_script}")
        return None
    
    print(f"✅ 找到Hook脚本: {hook_script}")
    return str(hook_script)

def install_hook(hook_script_path):
    """安装Hook到Claude Code配置"""
    settings_file = Path.home() / '.claude' / 'settings.json'
    
    # 读取现有设置
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}
    
    # 创建Hook配置
    hook_config = {
        "type": "command",
        "command": f"python3 {hook_script_path}"
    }
    
    # 更新设置
    if "hooks" not in settings:
        settings["hooks"] = {}
    
    if "PostToolUse" not in settings["hooks"]:
        settings["hooks"]["PostToolUse"] = []
    
    # 检查是否已经存在相同的Hook
    existing_hook = None
    for hook_group in settings["hooks"]["PostToolUse"]:
        for hook in hook_group.get("hooks", []):
            if hook.get("command") == hook_config["command"]:
                existing_hook = hook
                break
    
    if existing_hook:
        print("⚠️ Hook已存在，正在更新...")
    else:
        # 添加新的Hook配置
        hook_group = {
            "matcher": ".*",
            "hooks": [hook_config]
        }
        settings["hooks"]["PostToolUse"].append(hook_group)
    
    # 保存设置
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        print("✅ Hook配置已安装到Claude Code")
        return True
    except Exception as e:
        print(f"❌ 安装Hook失败: {e}")
        return False

def test_hook_installation():
    """测试Hook安装"""
    print("🧪 测试Hook功能...")
    
    # 创建测试文件
    test_file = Path("hook_install_test.md")
    test_content = f"""# Hook安装测试

这是一个测试文档，用于验证Claude Code Hook是否正常工作。

## 测试信息
- 安装时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 测试状态: Hook安装完成

如果您在备忘录中看到这个文档，说明Hook工作正常！
"""
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 运行测试同步
        from claude_hook import sync_file_hook
        success = sync_file_hook(str(test_file), "install_test")
        
        # 清理测试文件
        test_file.unlink()
        
        if success:
            print("✅ Hook功能测试通过")
            print("📱 请检查Mac备忘录中是否出现 'hook_install_test' 文档")
            return True
        else:
            print("❌ Hook功能测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        # 清理可能残留的测试文件
        if test_file.exists():
            test_file.unlink()
        return False

def show_usage_instructions():
    """显示使用说明"""
    print("""
🎉 Claude Code Hook 安装完成！

📋 使用方法:
1. 在Claude Code中创建或编辑.md文件
2. 文档将自动同步到Mac备忘录
3. 备忘录标题为文件名（无项目前缀）
4. 同步日志记录在 /tmp/claude_mindsync.log

🔧 手动同步命令:
  python claude_hook.py sync document.md    # 同步单个文件
  python claude_hook.py test               # 测试功能

🐛 故障排除:
  tail -f /tmp/claude_mindsync.log         # 查看同步日志
  tail -f /tmp/claude_mindsync_error.log   # 查看错误日志

📖 详细文档请查看 README.md 中的 "Claude Code Hook 完整配置指南"
""")

def main():
    """主安装流程"""
    print("""
╔══════════════════════════════════════════════════╗
║          Claude Code Hook 一键安装器              ║
║     自动同步Markdown文档到Mac备忘录               ║
╚══════════════════════════════════════════════════╝
""")
    
    # 1. 检查前置条件
    if not check_prerequisites():
        print("\\n❌ 安装中止，请解决上述问题后重试")
        sys.exit(1)
    
    # 2. 备份现有配置
    backup_claude_settings()
    
    # 3. 获取工具路径
    hook_script_path = get_tool_path()
    if not hook_script_path:
        print("\\n❌ 找不到Hook脚本，安装失败")
        sys.exit(1)
    
    # 4. 安装Hook
    print("\\n🔧 正在安装Hook...")
    if not install_hook(hook_script_path):
        print("\\n❌ Hook安装失败")
        sys.exit(1)
    
    # 5. 测试安装
    print("\\n🧪 测试Hook功能...")
    test_success = test_hook_installation()
    
    # 6. 显示完成信息
    print("\\n" + "="*50)
    if test_success:
        print("✅ 安装成功！Claude Code Hook已配置完成")
    else:
        print("⚠️ 安装完成，但测试未通过，请检查配置")
    
    show_usage_instructions()

if __name__ == "__main__":
    main()