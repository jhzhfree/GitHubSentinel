import gradio as gr

def main():
    subscriptions = ["项目A", "项目B", "项目C"]

    with gr.Blocks() as demo:
        with gr.Tab("GitHub 项目进展"):
            gr.Markdown("## GitHub 项目进展")
            subscription_list_progress_tab = gr.Dropdown(
                    choices=subscriptions, 
                    value=subscriptions[1],
                    label="订阅列表1",
                    elem_id="subscription_list_progress_tab",
                    info="已订阅GitHub项目1",
                    interactive=True  # 设置为交互模式
                )

        with gr.Tab("管理订阅"):
            gr.Markdown("## 管理 GitHub 订阅")
            subscription_list_manage_tab = gr.Dropdown(
                    choices=subscriptions, 
                    value=subscriptions[2],
                    label="订阅列表2",
                    elem_id="subscription_list_manage_tab",
                    info="已订阅GitHub项目2",
                    interactive=True  # 设置为交互模式
                )

    demo.launch()

if __name__ == "__main__":
    main()
