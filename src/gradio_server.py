import gradio as gr

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于 GitHub API 操作的客户端
from hacker_news_client import HackerNewsClient
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入用于处理语言模型的 LLM 类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hacker_news_client = HackerNewsClient()  # 创建 Hacker News 客户端实例
subscription_manager = SubscriptionManager(config.subscriptions_file)

# 公共的模型配置逻辑
def set_model_config(model_type, model_name):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    else:
        config.ollama_model_name = model_name
    return LLM(config), ReportGenerator(LLM(config), config.report_types)

# 获取模型列表
def get_models(model_type):
    """获取模型列表"""
    return config.get_models(model_type)

# 添加模型
def add_model(model_type, new_model, model_type_delete_value):
    """添加新模型"""
    if not new_model.strip():
        return "模型名称不能为空", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
    config.add_model(model_type, new_model)
    openai_models = config.get_models('openai')
    ollama_models = config.get_models('ollama')
    message = f"模型 {new_model} 已添加到 {model_type} 模型列表。"

    # 更新 model_to_delete 的 choices
    model_choices = config.get_models(model_type_delete_value)
    # 更新其他选项卡中的模型下拉框
    return (
        message,
        gr.update(choices=openai_models),
        gr.update(choices=ollama_models),
        gr.update(choices=model_choices, value=model_choices[0] if model_choices else None),
        gr.update(choices=get_models("openai")),
        gr.update(choices=get_models("ollama"))
    )

# 删除模型
def delete_model(model_type, model_name, model_type_delete_value):
    """删除模型"""
    if not model_name:
        return "未选择要删除的模型", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
    config.delete_model(model_type, model_name)
    openai_models = config.get_models('openai')
    ollama_models = config.get_models('ollama')
    message = f"模型 {model_name} 已从 {model_type} 模型列表中删除。"

    # 更新 model_to_delete 的 choices
    model_choices = config.get_models(model_type_delete_value)
    # 更新其他选项卡中的模型下拉框
    return (
        message,
        gr.update(choices=openai_models),
        gr.update(choices=ollama_models),
        gr.update(choices=model_choices, value=model_choices[0] if model_choices else None),
        gr.update(choices=get_models("openai")),
        gr.update(choices=get_models("ollama"))
    )

# 动态更新模型选择列表
def update_model_list(model_type):
    models = get_models(model_type)
    return gr.update(choices=models, value=models[0] if models else None)

# 生成GitHub报告的函数
def generate_github_report(model_type, model_name, repo, days):
    if not repo:
        return "Error: 无法生成报告，订阅项目未选择。", None  # 添加错误处理，返回错误信息

    llm, report_generator = set_model_config(model_type, model_name)

    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_github_report(raw_file_path)  # 生成报告

    return report, report_file_path  # 返回报告内容和报告文件路径

# 生成Hacker News热点报告的函数
def generate_hn_hour_topic(model_type, model_name):
    llm, report_generator = set_model_config(model_type, model_name)

    markdown_file_path = hacker_news_client.export_top_stories()
    report, report_file_path = report_generator.generate_hn_topic_report(markdown_file_path)

    return report, report_file_path  # 返回报告内容和报告文件路径

# 添加GitHub项目到订阅列表
def add_github_subscription(new_repo):
    """处理添加新的 GitHub 项目订阅"""
    if not new_repo.strip():
        return "仓库名称不能为空", gr.update(), gr.update(), gr.update()  # 返回错误提示

    message = subscription_manager.add_subscription(new_repo.strip())
    updated_subscriptions = subscription_manager.list_subscriptions()
    print("更新后的订阅列表:", updated_subscriptions)  # 调试信息

    return (
        message,
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None),
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None),
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None)
    )

# 删除GitHub项目订阅
def delete_github_subscription(selected_repo):
    """处理删除 GitHub 项目订阅"""
    if not selected_repo:
        return "未选择要删除的订阅", gr.update(), gr.update(), gr.update()

    message = subscription_manager.remove_subscription(selected_repo)
    updated_subscriptions = subscription_manager.list_subscriptions()
    print("删除后的订阅列表:", updated_subscriptions)  # 调试信息

    return (
        message,
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None),
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None),
        gr.update(choices=updated_subscriptions, value=updated_subscriptions[0] if updated_subscriptions else None)
    )

# 使用CSS调整对齐
css = """
.align-left {
    margin-top: 10px; /* 控制左边距 */
    margin-left: 5px; /* 控制左边距 */
    margin-bottom: 10px; /* 控制底部间距 */
}
"""

# 创建 Gradio 界面
with gr.Blocks(title="GitHubSentinel", css=css) as demo:

    # 获取初始订阅列表
    subscriptions = subscription_manager.list_subscriptions()

    # 创建 GitHub 项目进展 Tab
    with gr.Tab("GitHub 项目进展"):
        gr.Markdown("## GitHub 项目进展")  # 小标题

        # 默认选择 "ollama" 模型类型
        model_type_progress_tab = gr.Radio(
            ["ollama", "openai"], 
            value="ollama", 
            label="模型类型", 
            info="使用 OpenAI GPT API 或 Ollama 私有化模型服务"
        )

        # 默认下拉框显示 ollama 模型选项
        model_name_progress_tab = gr.Dropdown(
            choices=get_models("ollama"),
            value=get_models("ollama")[0] if get_models("ollama") else None,
            label="选择模型",
            interactive=True
        )

        # 订阅列表从 subscriptions 获取
        subscription_list_progress_tab = gr.Dropdown(
            choices=subscriptions, 
            value=subscriptions[0] if subscriptions else None,
            label="订阅列表",
            info="已订阅GitHub项目",
            interactive=True
        )

        days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")

        # 切换模型类型时，更新模型列表和默认选择项
        model_type_progress_tab.change(
            fn=update_model_list,
            inputs=model_type_progress_tab,
            outputs=model_name_progress_tab
        )

        button = gr.Button("生成报告")
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")

        button.click(generate_github_report, inputs=[model_type_progress_tab, model_name_progress_tab, subscription_list_progress_tab, days], outputs=[markdown_output, file_output])

    # 创建 Hacker News 热点话题 Tab
    with gr.Tab("Hacker News 热点话题"):
        gr.Markdown("## Hacker News 热点话题")  # 小标题

        # 默认选择 "ollama" 模型类型
        model_type_hn_tab = gr.Radio(
            ["ollama", "openai"], 
            value="ollama", 
            label="模型类型", 
            info="使用 OpenAI GPT API 或 Ollama 私有化模型服务"
        )

        # 默认下拉框显示 ollama 模型选项
        model_name_hn_tab = gr.Dropdown(
            choices=get_models("ollama"),
            value=get_models("ollama")[0] if get_models("ollama") else None,
            label="选择模型",
            interactive=True
        )

        # 切换模型类型时，更新模型列表和默认选择项
        model_type_hn_tab.change(
            fn=update_model_list,
            inputs=model_type_hn_tab,
            outputs=model_name_hn_tab
        )

        button = gr.Button("生成最新热点话题")
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")

        button.click(generate_hn_hour_topic, inputs=[model_type_hn_tab, model_name_hn_tab], outputs=[markdown_output, file_output])

    # 管理订阅的 Tab
    with gr.Tab("管理订阅"):
        gr.Markdown("## 管理 GitHub 订阅")  # 小标题

        # 第一部分：显示当前订阅列表
        with gr.Group():
            gr.Markdown("### 当前订阅列表", elem_classes="align-left")
            subscription_list_manage_tab = gr.Dropdown(
                choices=subscriptions,
                value=subscriptions[0] if subscriptions else None,
                label="当前订阅列表",
                interactive=True
            )
            list_message = gr.Markdown()  # 用于显示订阅列表的消息

        gr.Markdown("---")  # 添加分隔线

        # 第二部分：添加订阅
        with gr.Group():
            gr.Markdown("### 添加订阅", elem_classes="align-left")
            new_repo = gr.Textbox(
                label="添加新的 GitHub 仓库名称"
            )
            add_button = gr.Button("添加")
            add_message = gr.Markdown()  # 用于显示添加订阅的消息

        gr.Markdown("---")  # 添加分隔线

        # 第三部分：删除订阅
        with gr.Group():
            gr.Markdown("### 删除订阅", elem_classes="align-left")
            delete_repo_dropdown = gr.Dropdown(
                choices=subscriptions,
                value=subscriptions[0] if subscriptions else None,
                label="选择要删除的订阅",
                interactive=True
            )
            delete_button = gr.Button("删除")
            delete_message = gr.Markdown()  # 用于显示删除订阅的消息

        # 添加订阅后，更新订阅列表
        add_button.click(
            fn=add_github_subscription,
            inputs=new_repo,
            outputs=[add_message, subscription_list_manage_tab, subscription_list_progress_tab, delete_repo_dropdown]
        )

        # 删除订阅后，更新订阅列表
        delete_button.click(
            fn=delete_github_subscription,
            inputs=delete_repo_dropdown,
            outputs=[delete_message, subscription_list_manage_tab, subscription_list_progress_tab, delete_repo_dropdown]
        )

    # 管理模型的 Tab
    with gr.Tab("管理模型"):
        gr.Markdown("## 模型管理")

        # 查看 OpenAI 和 Ollama 模型列表
        with gr.Group():
            gr.Markdown("### OpenAI 模型列表", elem_classes="align-left")
            openai_model_list = gr.Dropdown(choices=get_models('openai'), label="OpenAI 模型", interactive=True)

        with gr.Group():
            gr.Markdown("### Ollama 模型列表", elem_classes="align-left")
            ollama_model_list = gr.Dropdown(choices=get_models('ollama'), label="Ollama 模型", interactive=True)

        gr.Markdown("---")  # 分隔线

        # 添加模型
        with gr.Group():
            gr.Markdown("### 添加模型", elem_classes="align-left")
            model_type_add = gr.Radio(["openai", "ollama"], value="openai", label="模型类型")
            new_model_input = gr.Textbox(label="添加新模型名称")
            add_model_button = gr.Button("添加模型")
            add_model_message = gr.Markdown()

        # 删除模型
        with gr.Group():
            gr.Markdown("### 删除模型", elem_classes="align-left")
            model_type_delete = gr.Radio(["openai", "ollama"], value="openai", label="模型类型")
            model_to_delete = gr.Dropdown(choices=get_models('openai'), label="选择要删除的模型")
            delete_model_button = gr.Button("删除模型")
            delete_model_message = gr.Markdown()

        # 当模型类型改变时，更新 model_to_delete 的选项
        def update_model_to_delete(model_type):
            models = get_models(model_type)
            return gr.update(choices=models, value=models[0] if models else None)

        model_type_delete.change(
            fn=update_model_to_delete,
            inputs=model_type_delete,
            outputs=model_to_delete
        )

        # 添加模型按钮点击事件
        add_model_button.click(
            fn=add_model,
            inputs=[model_type_add, new_model_input, model_type_delete],
            outputs=[
                add_model_message,
                openai_model_list,
                ollama_model_list,
                model_to_delete,
                model_name_progress_tab,
                model_name_hn_tab
            ]
        )

        # 删除模型按钮点击事件
        delete_model_button.click(
            fn=delete_model,
            inputs=[model_type_delete, model_to_delete, model_type_delete],
            outputs=[
                delete_model_message,
                openai_model_list,
                ollama_model_list,
                model_to_delete,
                model_name_progress_tab,
                model_name_hn_tab
            ]
        )

if __name__ == "__main__":
    demo.launch(share=True, server_name="127.0.0.1")
