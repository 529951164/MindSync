#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AppleScript桥接模块
用于与macOS备忘录应用程序交互
"""

import subprocess
import logging
from typing import List, Optional, Dict, Any
import re

logger = logging.getLogger(__name__)

class AppleScriptBridge:
    """AppleScript桥接类，封装与备忘录应用的交互"""
    
    def __init__(self, account: str = "iCloud", default_folder: str = "Notes"):
        """
        初始化AppleScript桥接
        
        Args:
            account: 备忘录账户名，默认为"iCloud"
            default_folder: 默认文件夹名，默认为"Notes"
        """
        self.account = account
        self.default_folder = default_folder
    
    def execute_applescript(self, script: str) -> Optional[str]:
        """
        执行AppleScript脚本
        
        Args:
            script: AppleScript代码
            
        Returns:
            脚本执行结果，失败返回None
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=30
            )
            return result.stdout.strip() if result.stdout else ""
        except subprocess.CalledProcessError as e:
            logger.error(f"AppleScript执行失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logger.error("AppleScript执行超时")
            return None
        except Exception as e:
            logger.error(f"AppleScript执行异常: {e}")
            return None
    
    def get_existing_notes(self, folder: str = None) -> List[str]:
        """
        获取现有备忘录标题列表
        
        Args:
            folder: 文件夹名，默认使用default_folder
            
        Returns:
            备忘录标题列表
        """
        folder = folder or self.default_folder
        
        script = f'''
        tell application "Notes"
            set noteList to {{}}
            try
                tell account "{self.account}"
                    tell folder "{folder}"
                        repeat with thisNote in notes
                            set end of noteList to (name of thisNote)
                        end repeat
                    end tell
                end tell
            on error
                -- 如果文件夹不存在，返回空列表
                set noteList to {{}}
            end try
        end tell
        
        set AppleScript's text item delimiters to "|||"
        set noteListString to noteList as string
        set AppleScript's text item delimiters to ""
        
        return noteListString
        '''
        
        result = self.execute_applescript(script)
        if result is None:
            logger.warning("获取备忘录列表失败")
            return []
        
        if not result:
            return []
            
        # 解析返回结果
        notes = [note.strip() for note in result.split('|||') if note.strip()]
        logger.debug(f"找到 {len(notes)} 个备忘录")
        return notes
    
    def note_exists(self, title: str, folder: str = None) -> bool:
        """
        检查指定标题的备忘录是否存在
        
        Args:
            title: 备忘录标题
            folder: 文件夹路径，支持嵌套路径如 "Claude/ProjectName"，默认使用default_folder
            
        Returns:
            存在返回True，否则返回False
        """
        folder = folder or self.default_folder
        
        # 转义AppleScript中的特殊字符
        escaped_title = self._escape_applescript_string(title)
        
        # 处理嵌套文件夹路径
        folder_parts = [part.strip() for part in folder.split('/') if part.strip()]
        folder_ref = self._build_folder_reference(folder_parts)
        
        if folder_parts:
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        {folder_ref}
                            set targetNote to first note whose name is "{escaped_title}"
                        {self._build_end_tell_blocks(folder_parts)}
                    end tell
                    return "true"
                on error
                    return "false"
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        set targetNote to first note whose name is "{escaped_title}"
                    end tell
                    return "true"
                on error
                    return "false"
                end try
            end tell
            '''
        
        result = self.execute_applescript(script)
        return result == "true" if result else False
    
    def create_note(self, title: str, content: str, folder: str = None) -> bool:
        """
        创建新备忘录
        
        Args:
            title: 备忘录标题
            content: 备忘录内容
            folder: 文件夹路径，支持嵌套路径如 "Claude/ProjectName"，默认使用default_folder
            
        Returns:
            创建成功返回True，否则返回False
        """
        folder = folder or self.default_folder
        
        # 转义特殊字符
        escaped_title = self._escape_applescript_string(title)
        escaped_content = self._escape_applescript_string(content)
        
        # 处理嵌套文件夹路径
        folder_parts = [part.strip() for part in folder.split('/') if part.strip()]
        folder_ref = self._build_folder_reference(folder_parts)
        
        if folder_parts:
            script = f'''
            tell application "Notes"
                activate
                try
                    tell account "{self.account}"
                        {folder_ref}
                            set newNote to make new note
                            tell newNote
                                set body to "{escaped_content}"
                            end tell
                        {self._build_end_tell_blocks(folder_parts)}
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                activate
                try
                    tell account "{self.account}"
                        set newNote to make new note
                        tell newNote
                            set body to "{escaped_content}"
                        end tell
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        
        result = self.execute_applescript(script)
        
        if result and result.startswith("success"):
            logger.info(f"✅ 创建备忘录成功: {title}")
            return True
        else:
            logger.error(f"❌ 创建备忘录失败: {title} - {result}")
            return False
    
    def update_note(self, title: str, content: str, folder: str = None) -> bool:
        """
        更新现有备忘录
        
        Args:
            title: 备忘录标题
            content: 新的备忘录内容
            folder: 文件夹路径，支持嵌套路径如 "Claude/ProjectName"，默认使用default_folder
            
        Returns:
            更新成功返回True，否则返回False
        """
        folder = folder or self.default_folder
        
        # 转义特殊字符
        escaped_title = self._escape_applescript_string(title)
        escaped_content = self._escape_applescript_string(content)
        
        # 处理嵌套文件夹路径
        folder_parts = [part.strip() for part in folder.split('/') if part.strip()]
        folder_ref = self._build_folder_reference(folder_parts)
        
        if folder_parts:
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        {folder_ref}
                            set targetNote to first note whose name is "{escaped_title}"
                            tell targetNote
                                set body to "{escaped_content}"
                            end tell
                        {self._build_end_tell_blocks(folder_parts)}
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        set targetNote to first note whose name is "{escaped_title}"
                        tell targetNote
                            set body to "{escaped_content}"
                        end tell
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        
        result = self.execute_applescript(script)
        
        if result and result.startswith("success"):
            logger.info(f"🔄 更新备忘录成功: {title}")
            return True
        else:
            logger.error(f"❌ 更新备忘录失败: {title} - {result}")
            return False
    
    def delete_note(self, title: str, folder: str = None) -> bool:
        """
        删除备忘录
        
        Args:
            title: 备忘录标题
            folder: 文件夹名，默认使用default_folder
            
        Returns:
            删除成功返回True，否则返回False
        """
        folder = folder or self.default_folder
        
        escaped_title = self._escape_applescript_string(title)
        
        script = f'''
        tell application "Notes"
            try
                tell account "{self.account}"
                    tell folder "{folder}"
                        set targetNote to first note whose name is "{escaped_title}"
                        delete targetNote
                    end tell
                end tell
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_applescript(script)
        
        if result and result.startswith("success"):
            logger.info(f"🗑️ 删除备忘录成功: {title}")
            return True
        else:
            logger.error(f"❌ 删除备忘录失败: {title} - {result}")
            return False
    
    def get_folders(self) -> List[str]:
        """
        获取备忘录文件夹列表
        
        Returns:
            文件夹名称列表
        """
        script = f'''
        tell application "Notes"
            set folderList to {{}}
            try
                tell account "{self.account}"
                    repeat with thisFolder in folders
                        set end of folderList to (name of thisFolder)
                    end repeat
                end tell
            on error
                set folderList to {{}}
            end try
        end tell
        
        set AppleScript's text item delimiters to "|||"
        set folderListString to folderList as string
        set AppleScript's text item delimiters to ""
        
        return folderListString
        '''
        
        result = self.execute_applescript(script)
        if result is None:
            return []
            
        if not result:
            return []
            
        folders = [folder.strip() for folder in result.split('|||') if folder.strip()]
        return folders
    
    def create_folder(self, folder_path: str) -> bool:
        """
        创建备忘录文件夹，支持嵌套路径如 "Claude/ProjectName"
        
        Args:
            folder_path: 文件夹路径，支持 "/" 分隔的嵌套路径
            
        Returns:
            创建成功返回True，否则返回False
        """
        # 分解路径
        path_parts = [part.strip() for part in folder_path.split('/') if part.strip()]
        
        if not path_parts:
            logger.error("文件夹路径为空")
            return False
        
        # 逐级创建文件夹
        for i in range(len(path_parts)):
            current_path_parts = path_parts[:i+1]
            current_folder_name = current_path_parts[-1]
            parent_path_parts = current_path_parts[:-1]
            
            # 检查当前级别的文件夹是否已存在
            if self._folder_exists_at_path(current_path_parts):
                continue
                
            # 创建文件夹
            success = self._create_single_folder(current_folder_name, parent_path_parts)
            if not success:
                logger.error(f"❌ 创建文件夹失败: {'/'.join(current_path_parts)}")
                return False
            
            logger.info(f"📁 创建文件夹成功: {'/'.join(current_path_parts)}")
        
        return True
    
    def _folder_exists_at_path(self, path_parts: List[str]) -> bool:
        """
        检查指定路径的文件夹是否存在
        
        Args:
            path_parts: 文件夹路径部分列表
            
        Returns:
            存在返回True，否则返回False
        """
        if not path_parts:
            return True
        
        folder_name = path_parts[-1]
        parent_parts = path_parts[:-1]
        
        # 构建AppleScript来检查文件夹是否存在
        if parent_parts:
            # 嵌套文件夹检查
            parent_folder_ref = self._build_folder_reference(parent_parts)
            escaped_folder = self._escape_applescript_string(folder_name)
            
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        {parent_folder_ref}
                            set targetFolder to folder "{escaped_folder}"
                        end tell
                    end tell
                    return "exists"
                on error
                    return "not_exists"
                end try
            end tell
            '''
        else:
            # 根级文件夹检查
            escaped_folder = self._escape_applescript_string(folder_name)
            
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        set targetFolder to folder "{escaped_folder}"
                    end tell
                    return "exists"
                on error
                    return "not_exists"
                end try
            end tell
            '''
        
        result = self.execute_applescript(script)
        return result == "exists"
    
    def _create_single_folder(self, folder_name: str, parent_path_parts: List[str]) -> bool:
        """
        在指定父路径下创建单个文件夹
        
        Args:
            folder_name: 要创建的文件夹名称
            parent_path_parts: 父路径部分列表
            
        Returns:
            创建成功返回True，否则返回False
        """
        escaped_folder = self._escape_applescript_string(folder_name)
        
        if parent_path_parts:
            # 在嵌套路径下创建
            parent_folder_ref = self._build_folder_reference(parent_path_parts)
            
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        {parent_folder_ref}
                            make new folder with properties {{name:"{escaped_folder}"}}
                        end tell
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        else:
            # 在根级创建
            script = f'''
            tell application "Notes"
                try
                    tell account "{self.account}"
                        make new folder with properties {{name:"{escaped_folder}"}}
                    end tell
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
            '''
        
        result = self.execute_applescript(script)
        return result and result.startswith("success")
    
    def _build_folder_reference(self, path_parts: List[str]) -> str:
        """
        构建嵌套文件夹的AppleScript引用
        
        Args:
            path_parts: 文件夹路径部分列表
            
        Returns:
            AppleScript文件夹引用字符串
        """
        if not path_parts:
            return ""
        
        reference = ""
        for part in path_parts:
            escaped_part = self._escape_applescript_string(part)
            reference += f'tell folder "{escaped_part}"\n'
        
        return reference
    
    def _build_end_tell_blocks(self, path_parts: List[str]) -> str:
        """
        构建对应数量的 end tell 块
        
        Args:
            path_parts: 文件夹路径部分列表
            
        Returns:
            end tell 块字符串
        """
        return "\n".join(["end tell" for _ in path_parts])
    
    def _escape_applescript_string(self, text: str) -> str:
        """
        转义AppleScript字符串中的特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            转义后的文本
        """
        # 替换AppleScript中需要转义的字符
        text = text.replace('\\', '\\\\')  # 反斜杠
        text = text.replace('"', '\\"')     # 双引号
        # 注意：对于备忘录内容，不转义换行符，保持原始换行
        # text = text.replace('\n', '\\n')    # 换行符 - 注释掉
        # text = text.replace('\r', '\\r')    # 回车符 - 注释掉
        # text = text.replace('\t', '\\t')    # 制表符 - 注释掉
        
        return text
    
    def get_note_info(self, title: str, folder: str = None) -> Optional[Dict[str, Any]]:
        """
        获取备忘录详细信息
        
        Args:
            title: 备忘录标题
            folder: 文件夹名，默认使用default_folder
            
        Returns:
            备忘录信息字典，包含创建时间、修改时间等
        """
        folder = folder or self.default_folder
        escaped_title = self._escape_applescript_string(title)
        
        script = f'''
        tell application "Notes"
            try
                tell account "{self.account}"
                    tell folder "{folder}"
                        set targetNote to first note whose name is "{escaped_title}"
                        set noteInfo to (creation date of targetNote) & "|||" & (modification date of targetNote) & "|||" & (body of targetNote)
                        return noteInfo
                    end tell
                end tell
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.execute_applescript(script)
        if not result or result.startswith("error"):
            return None
            
        try:
            parts = result.split('|||')
            if len(parts) >= 3:
                return {
                    'creation_date': parts[0],
                    'modification_date': parts[1], 
                    'body': parts[2],
                    'title': title
                }
        except Exception as e:
            logger.error(f"解析备忘录信息失败: {e}")
            
        return None