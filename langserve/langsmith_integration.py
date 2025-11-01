from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langsmith import Client

from config.settings import settings


class LangSmithIntegration:
    """LangSmith 集成类"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangSmithIntegration, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化 LangSmith 客户端和回调"""
        if not settings.LANGCHAIN_TRACING_V2:
            self.client = None
            self.tracer = None
            self.callback_manager = None
            return

        try:
            # 创建 LangSmith 客户端
            self.client = Client(
                api_url=settings.LANGCHAIN_ENDPOINT,
                api_key=settings.LANGCHAIN_API_KEY
            )

            # 创建 LangChain 追踪器
            self.tracer = LangChainTracer(
                project_name=settings.LANGCHAIN_PROJECT,
                client=self.client
            )

            # 创建回调管理器
            self.callback_manager = CallbackManager(handlers=[self.tracer])

            print(f"LangSmith 已启用，项目: {settings.LANGCHAIN_PROJECT}")
        except Exception as e:
            print(f"初始化 LangSmith 失败: {str(e)}")
            self.client = None
            self.tracer = None
            self.callback_manager = None

    def get_callback_manager(self):
        """获取回调管理器"""
        return self.callback_manager

    def trace_run(self, run_id: str):
        """在 LangSmith 中查看运行详情"""
        if not self.client:
            print("LangSmith 未启用")
            return

        try:
            run_url = f"{settings.LANGCHAIN_ENDPOINT}/runs/{run_id}"
            print(f"查看运行详情: {run_url}")
            return run_url
        except Exception as e:
            print(f"获取运行详情失败: {str(e)}")

    def log_feedback(self, run_id: str, feedback: dict):
        """记录用户反馈"""
        if not self.client:
            print("LangSmith 未启用")
            return False

        try:
            self.client.create_feedback(
                run_id=run_id,
                key="user_feedback",
                score=feedback.get("score", 0),
                comment=feedback.get("comment", ""),
                value=feedback
            )
            print("用户反馈已记录")
            return True
        except Exception as e:
            print(f"记录反馈失败: {str(e)}")
            return False

    def analyze_performance(self):
        """分析助手性能"""
        if not self.client:
            print("LangSmith 未启用")
            return

        try:
            # 获取最近运行
            runs = self.client.list_runs(project_name=settings.LANGCHAIN_PROJECT, limit=100)

            # 计算关键指标
            total_runs = 0
            successful_runs = 0
            total_latency = 0
            tool_usage = {}

            for run in runs:
                total_runs += 1
                if run.status == "success":
                    successful_runs += 1

                total_latency += run.latency.total_seconds() if run.latency else 0

                # 统计工具使用
                if run.run_type == "tool":
                    tool_name = run.name
                    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

            # 计算成功率
            success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

            # 计算平均延迟
            avg_latency = (total_latency / total_runs) if total_runs > 0 else 0

            # 打印报告
            print("\n===== LangSmith 性能报告 =====")
            print(f"总运行次数: {total_runs}")
            print(f"成功率: {success_rate:.2f}%")
            print(f"平均延迟: {avg_latency:.2f} 秒")
            print("\n工具使用统计:")
            for tool, count in tool_usage.items():
                print(f"- {tool}: {count} 次")

            return {
                "total_runs": total_runs,
                "success_rate": success_rate,
                "avg_latency": avg_latency,
                "tool_usage": tool_usage
            }
        except Exception as e:
            print(f"分析性能失败: {str(e)}")
            return None


# 全局 LangSmith 集成实例
langsmith_integration = LangSmithIntegration()
