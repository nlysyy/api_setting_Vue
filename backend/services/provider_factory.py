"""Provider 工厂 — 根据 providerId 返回对应的适配器实例"""


class ProviderFactory:
    @staticmethod
    def get(provider_id: str):
        # 懒加载导入，避免循环依赖
        if provider_id == "deepseek":
            from services.deepseek import DeepSeekProvider
            return DeepSeekProvider()
        if provider_id == "openai":
            from services.openai import OpenAIProvider
            return OpenAIProvider()
        if provider_id == "claude":
            from services.claude import ClaudeProvider
            return ClaudeProvider()
        if provider_id == "gemini":
            from services.gemini import GeminiProvider
            return GeminiProvider()
        if provider_id == "qwen":
            from services.qwen import QwenProvider
            return QwenProvider()
        if provider_id == "moonshot":
            from services.moonshot import MoonshotProvider
            return MoonshotProvider()
        if provider_id == "stepfun":
            from services.stepfun import StepfunProvider
            return StepfunProvider()

        raise ValueError(f"不支持的服务商: {provider_id}")
