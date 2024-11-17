import json
import os

class SubscriptionManager:
    def __init__(self, subscriptions_file):
        self.subscriptions_file = subscriptions_file
        self.subscriptions = self.load_subscriptions()

    def load_subscriptions(self):
        """加载订阅文件，确保返回的是列表"""
        try:
            with open(self.subscriptions_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):  # 确保读取到的是列表
                    return data
                else:
                    print("警告: 订阅文件内容不是列表，初始化为空列表。")
                    return []  # 如果内容不是列表，返回空列表
        except FileNotFoundError:
            print("订阅文件未找到，初始化为空列表。")
            return []
        except json.JSONDecodeError:
            print("订阅文件格式错误，初始化为空列表。")
            return []

    def save_subscriptions(self):
        """保存订阅列表到文件"""
        try:
            with open(self.subscriptions_file, 'w') as f:
                json.dump(self.subscriptions, f, indent=4)
            print(f"订阅列表已保存到 {self.subscriptions_file}")
        except Exception as e:
            print(f"保存订阅文件时出现错误：{e}")

    def list_subscriptions(self):
        """返回当前的订阅列表"""
        return self.subscriptions

    def add_subscription(self, repo):
        """添加新的仓库订阅，如果已存在则不添加"""
        if repo in self.subscriptions:
            print(f"项目 {repo} 已存在订阅列表中。")
            return f"项目 {repo} 已存在订阅列表中。"
        
        self.subscriptions.append(repo)
        self.save_subscriptions()
        print(f"项目 {repo} 已成功添加订阅。")
        return f"项目 {repo} 已成功添加订阅。"

    def remove_subscription(self, repo):
        """从订阅列表中移除指定仓库"""
        if repo not in self.subscriptions:
            print(f"项目 {repo} 不在订阅列表中。")
            return f"项目 {repo} 不在订阅列表中。"
        
        self.subscriptions.remove(repo)
        self.save_subscriptions()
        print(f"项目 {repo} 已成功从订阅列表中移除。")
        return f"项目 {repo} 已成功从订阅列表中移除。"
