import re

from .base_tool import BaseAssistantTool


class CalculatorTool(BaseAssistantTool):
    """计算器工具"""

    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.precision = 2

    def run(self, query: str) -> str:
        try:
            # 清理查询并提取表达式
            expression = self._extract_expression(query)
            if not expression:
                return "未找到有效的数学表达式"

            # 安全评估表达式
            result = self._safe_eval(expression)

            # 格式化结果
            if isinstance(result, float):
                result = round(result, self.precision)
                if result.is_integer():
                    result = int(result)

            return f"计算结果: {expression} = {result}"
        except Exception as e:
            return f"计算失败: {str(e)}"

    def extract_expression(self, query: str) -> str:
        """从查询中提取数学表达式"""
        # 尝试匹配常见数学表达式
        patterns = [
            r'(\d+\.?\d*)\s*([\+\-\*\/\^])\s*(\d+\.?\d*)',  # 基本运算
            r'计算(.+?)等于多少',  # 中文查询
            r'算一下(.+?)是多少',  # 中文查询
            r'(\d+\.?\d*)\s*的平方',  # 平方
            r'(\d+\.?\d*)\s*的立方',  # 立方
            r'(\d+\.?\d*)\s*的平方根',  # 平方根
            r'(\d+\.?\d*)\s*的立方根'  # 立方根
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                if pattern in patterns[0]:
                    # 基本运算
                    return f"{match.group(1)} {match.group(2)} {match.group(3)}"
                elif pattern in patterns[1:3]:
                    # 中文查询
                    return match.group(1)
                elif pattern == patterns[3]:
                    # 平方
                    return f"{match.group(1)} ** 2"
                elif pattern == patterns[4]:
                    # 立方
                    return f"{match.group(1)} ** 3"
                elif pattern == patterns[5]:
                    # 平方根
                    return f"{match.group(1)} ** 0.5"
                elif pattern == patterns[6]:
                    # 立方根
                    return f"{match.group(1)} ** (1/3)"

        # 尝试提取纯数学表达式
        math_chars = set('0123456789.+-*/^() ')
        if all(char in math_chars for char in query):
            return query

        return ""

    def safe_eval(self, expression: str):
        """安全评估数学表达式"""
        # 替换中文运算符
        expression = expression.replace('×', '*').replace('÷', '/')

        # 移除空格
        expression = expression.replace(' ', '')

        # 验证表达式安全性
        allowed_chars = set('0123456789.+-*/^() ')
        if not all(char in allowed_chars for char in expression):
            raise ValueError("表达式包含不安全字符")

        # 使用eval计算（在受限环境中）
        return eval(expression, {"__builtins__": None}, {})