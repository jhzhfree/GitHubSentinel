import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
            self.email = config.get('email', {})
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            # 加载 GitHub 相关配置
            github_config = config.get('github', {})
            self.github_token = os.getenv('GITHUB_TOKEN', github_config.get('token'))
            self.subscriptions_file = github_config.get('subscriptions_file', 'subscriptions.json')  # 添加默认文件路径
            self.freq_days = github_config.get('progress_frequency_days', 1)
            self.exec_time = github_config.get('progress_execution_time', "08:00")

            # 加载 LLM 相关配置
            llm_config = config.get('llm', {})
            self.llm_model_type = llm_config.get('model_type', 'openai')
            self.openai_model_name = llm_config.get('openai_model_name', 'gpt-4o-mini')
            self.ollama_model_name = llm_config.get('ollama_model_name', 'llama3')
            self.ollama_api_url = llm_config.get('ollama_api_url', 'http://192.168.22.6:11434/api/chat')

            # 加载模型列表
            self.openai_models = llm_config.get('openai_models', ['gpt-3.5-turbo', 'gpt-4o'])
            self.ollama_models = llm_config.get('ollama_models', ['llama2', 'gemma2:2b'])

            # 加载报告类型配置
            self.report_types = config.get('report_types', ["github", "hacker_news"])  # 默认报告类型
            
            # 加载 Slack 配置
            slack_config = config.get('slack', {})
            self.slack_webhook_url = slack_config.get('webhook_url')

    def save_config(self):
        """将当前配置保存到文件"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # 更新配置
        config['llm'] = {
            'model_type': self.llm_model_type,
            'openai_model_name': self.openai_model_name,
            'ollama_model_name': self.ollama_model_name,
            'ollama_api_url': self.ollama_api_url,
            'openai_models': self.openai_models,
            'ollama_models': self.ollama_models
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    # 模型管理相关方法
    def get_models(self, model_type):
        """根据模型类型返回模型列表"""
        if model_type == 'openai':
            return self.openai_models
        elif model_type == 'ollama':
            return self.ollama_models

    def add_model(self, model_type, new_model):
        """向指定的模型类型列表中添加模型"""
        if model_type == 'openai':
            if new_model not in self.openai_models:
                self.openai_models.append(new_model)
        elif model_type == 'ollama':
            if new_model not in self.ollama_models:
                self.ollama_models.append(new_model)

        # 保存配置文件
        self.save_config()

    def delete_model(self, model_type, model_name):
        """从指定的模型类型列表中删除模型"""
        if model_type == 'openai' and model_name in self.openai_models:
            self.openai_models.remove(model_name)
        elif model_type == 'ollama' and model_name in self.ollama_models:
            self.ollama_models.remove(model_name)

        # 保存配置文件
        self.save_config()
