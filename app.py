import gradio as gr
import time


def update_history(role, content, history):
    history.append({"role": role, "content": content})
    return history


def process(prompt: str, history=[]):
    textbox.value = None
    history = update_history("user", prompt, history)
    yield history
    time.sleep(2)
    history = update_history("assistant", "placeholder", history)
    yield history


def clear_textbox_field():
    return None

def clear_all_fields():
    return None,None


def save_data(history):
    gr.Info('data has been saved successfully')


with gr.Blocks() as demo:
    with gr.Tab("sft"):
        chatbot = gr.Chatbot(type="messages")
        textbox = gr.Textbox(show_label=False, submit_btn=True)
        textbox.submit(
            fn=process, inputs=[textbox, chatbot], outputs=[chatbot]
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[textbox]
        )
        with gr.Row():
            clear_button = gr.Button("Clear")
            clear_button.click(clear_textbox_field, outputs=[textbox,chatbot])
            submit = gr.Button("save chat", variant="primary")
            submit.click(save_data,inputs=[chatbot])

demo.launch(debug=True, show_error=True)
