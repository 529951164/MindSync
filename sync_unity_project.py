#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用Unity项目文档同步脚本
将指定Unity项目的所有MD文档统一同步到Claude/{项目名}目录，自动排除Library等目录
"""

import subprocess
import sys
from pathlib import Path
from markdown_converter import convert_markdown_for_notes

class UnityProjectSyncer:
    def __init__(self):
        # Unity项目中需要排除的目录模式
        self.exclude_patterns = [
            "Library",           # Unity Library目录
            "PackageCache",      # 包缓存
            "Temp",              # 临时文件
            ".git",              # Git目录
            "node_modules",      # Node模块
            "__pycache__",       # Python缓存
            ".DS_Store",         # macOS系统文件
        ]
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        file_str = str(file_path)
        
        # 检查路径中是否包含排除的模式
        for pattern in self.exclude_patterns:
            if pattern in file_str:
                return True
        
        # 排除以点开头的隐藏文件
        if file_path.name.startswith('.'):
            return True
            
        return False
    
    def get_project_name(self, project_path: Path) -> str:
        """从项目路径中提取项目名称"""
        return project_path.name
    
    def find_md_files(self, project_path: Path) -> list:
        """查找项目中所有相关的MD文档"""
        md_files = []
        
        for md_file in project_path.rglob("*.md"):
            if md_file.is_file() and not self.should_exclude_file(md_file):
                md_files.append(md_file)
        
        return md_files
    
    def sync_single_doc(self, md_file: Path, project_name: str, target_folder: str, index: int, total: int) -> bool:
        """同步单个文档到指定文件夹"""
        try:
            # 生成标题
            title = f"[{project_name}] {md_file.stem}"
            
            # 读取和转换内容
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 转换内容
            converted_content = convert_markdown_for_notes(original_content)
            final_content = f"{md_file.stem}<br><br>{converted_content}"
            
            # 转义AppleScript字符串
            escaped_title = title.replace('\\', '\\\\').replace('"', '\\"')
            escaped_content = final_content.replace('\\', '\\\\').replace('"', '\\"')
            
            # 创建AppleScript
            script = f'''
            tell application "Notes"
                set acc to account "iCloud"
                set claudeFolder to folder "Claude" of acc
                
                -- 确保项目文件夹存在
                try
                    set projectFolder to folder "{project_name}" of claudeFolder
                on error
                    set projectFolder to make new folder at end of folders of claudeFolder with properties {{name:"{project_name}"}}
                end try
                
                -- 检查是否已存在同名备忘录
                set noteExists to false
                repeat with n in notes of projectFolder
                    if name of n is "{escaped_title}" then
                        set noteExists to true
                        tell n
                            set body to "{escaped_content}"
                        end tell
                        exit repeat
                    end if
                end repeat
                
                -- 如果不存在则创建新备忘录
                if not noteExists then
                    set newNote to make new note at end of notes of projectFolder
                    tell newNote
                        set body to "{escaped_content}"
                    end tell
                end if
                
                return "success"
            end tell
            '''
            
            # 执行AppleScript
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {index}/{total} 同步成功: {md_file.stem}")
                return True
            else:
                print(f"❌ {index}/{total} 同步失败: {md_file.name} - {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ {index}/{total} 处理失败: {md_file.name} - {e}")
            return False
    
    def sync_project(self, project_path_str: str) -> bool:
        """同步整个Unity项目的文档"""
        project_path = Path(project_path_str)
        
        if not project_path.exists():
            print(f"❌ 项目路径不存在: {project_path_str}")
            return False
        
        if not project_path.is_dir():
            print(f"❌ 路径不是目录: {project_path_str}")
            return False
        
        project_name = self.get_project_name(project_path)
        target_folder = f"Claude/{project_name}"
        
        print(f"🔄 开始同步Unity项目: {project_name}")
        print(f"📂 项目路径: {project_path}")
        print(f"📋 目标文件夹: {target_folder}")
        
        # 查找所有MD文档
        md_files = self.find_md_files(project_path)
        
        if not md_files:
            print("❌ 未找到任何MD文档")
            return False
        
        print(f"📋 找到 {len(md_files)} 个项目文档（已排除Library等目录）")
        
        # 显示即将同步的文档类型统计
        self.show_file_stats(md_files, project_path)
        
        # 确认是否继续
        confirm = input(f"\n是否继续同步 {len(md_files)} 个文档到 {target_folder}? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 用户取消同步")
            return False
        
        # 同步所有文档
        success_count = 0
        for i, md_file in enumerate(md_files, 1):
            if self.sync_single_doc(md_file, project_name, target_folder, i, len(md_files)):
                success_count += 1
        
        print(f"\n📊 同步完成: 成功 {success_count}/{len(md_files)}")
        
        if success_count == len(md_files):
            print(f"🎉 {project_name} 项目文档同步完成！")
            return True
        else:
            print("⚠️ 部分文档同步失败")
            return False
    
    def show_file_stats(self, md_files: list, project_path: Path):
        """显示文档统计信息"""
        print(f"\n📊 文档分布统计:")
        
        # 按目录分类统计
        dir_stats = {}
        for md_file in md_files:
            relative_path = md_file.relative_to(project_path)
            if len(relative_path.parts) > 1:
                top_dir = relative_path.parts[0]
            else:
                top_dir = "根目录"
            
            if top_dir not in dir_stats:
                dir_stats[top_dir] = []
            dir_stats[top_dir].append(md_file.name)
        
        # 显示统计
        for dir_name, files in sorted(dir_stats.items()):
            print(f"  📁 {dir_name}: {len(files)} 个文档")
            if len(files) <= 5:
                for file in files:
                    print(f"    - {file}")
            else:
                for file in files[:3]:
                    print(f"    - {file}")
                print(f"    - ... (还有{len(files)-3}个)")

def main():
    """主函数"""
    syncer = UnityProjectSyncer()
    
    if len(sys.argv) < 2:
        print("📖 Unity项目文档同步工具")
        print("\n使用方法:")
        print(f"  python3 {sys.argv[0]} <项目路径>")
        print("\n示例:")
        print(f"  python3 {sys.argv[0]} /Volumes/Q/MiniGame/MyUnityProject")
        print(f"  python3 {sys.argv[0]} /Volumes/Q/MiniGame/gbt-2021/gamebox_develop")
        print("\n功能:")
        print("  - 自动排除Unity Library/PackageCache等目录")
        print("  - 统一同步到Claude/{项目名}文件夹")
        print("  - 支持Markdown格式转换")
        print("  - 显示同步统计和确认")
        return
    
    project_path = sys.argv[1]
    success = syncer.sync_project(project_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()