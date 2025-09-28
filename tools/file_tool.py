import subprocess
import os
import re
from .base_tool import BaseAssistantTool


class FileTool(BaseAssistantTool):
    """文件操作工具"""

    def __init__(self, name:str, config : dict):
        super().__init__(name, config)

    def run(self, query: str) -> str:
        if "文件夹" in query or "目录" in query:
            return self.open_folder(query)
        else:
            return self.search_files(query)

    def open_folder(self, query: str) -> str:
        """打开文件夹"""
        folder_name = self.extract_folder_name(query)

        if folder_name and os.path.exists(folder_name):
            # macOS
            subprocess.run(["open", folder_name])
            return f"已在Finder中打开 {folder_name} 文件夹"
        elif folder_name:
            # 尝试在常见位置查找
            common_paths = [
                os.path.expanduser(f"~/{folder_name}"),
                os.path.expanduser(f"~/Desktop/{folder_name}"),
                os.path.expanduser(f"~/Documents/{folder_name}"),
                f"/{folder_name}"
            ]

            for path in common_paths:
                if os.path.exists(path):
                    subprocess.run(["open", path])
                    return f"已在Finder中打开 {path}"

            return f"未找到名为 {folder_name} 的文件夹"
        else:
            # 打开当前目录
            subprocess.run(["open", "."])
            return "已打开当前文件夹"

    def search_files(self, query: str) -> str:
        """搜索文件"""
        try:
            # 提取搜索关键词
            pattern = r'查找|搜索|找(.+?)(文件|文档)?$'
            match = re.search(pattern, query)
            if match:
                search_term = match.group(1).strip()
            else:
                search_term = query

            # 在macOS上使用mdfind搜索
            result = subprocess.run(
                ["mdfind", search_term],
                capture_output=True,
                text=True
            )

            files = [f for f in result.stdout.strip().split('\n') if f]

            if files:
                # 只显示前5个结果
                display_files = files[:5]
                result_text = f"找到 {len(files)} 个相关文件。前{len(display_files)}个：\n"
                for i, file_path in enumerate(display_files, 1):
                    file_name = os.path.basename(file_path)
                    result_text += f"{i}. {file_name}\n"

                result_text += "\n说'打开第一个'来打开文件。"
                return result_text
            else:
                return f"没有找到包含 '{search_term}' 的文件。"
        except Exception as e:
            return f"文件搜索失败: {str(e)}"

    def extract_folder_name(self, query: str) -> str:
        """从查询中提取文件夹名称"""
        patterns = [
            r'打开(.+?)文件夹',
            r'打开(.+?)目录',
            r'查找(.+?)文件夹',
            r'搜索(.+?)文件夹'
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()

        return ""