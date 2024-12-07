import gradio as gr
from huggingface_hub.utils._auth import get_token
from huggingface_hub import InferenceClient, whoami

from dataset_uploader import ParquetScheduler

# get token if we're already logged in
hf_token = get_token()

contributor_username = whoami()["name"]

# IMPORTANT !!!
# change these values
# repo to where we push the data
sft_scheduler = ParquetScheduler(repo_id="not-lain/sft",every=5)


show_info = True

def generate(messages):
    """
    A function that generates a response to a given prompt. 
    Args:
        messages: A list of strings, each string being a message from the user or the assistant.
    Returns:
        A generator of strings being a response from the assistant.
    """
    
    # we do not need to explecitly pass it if we're already logged in
    client = InferenceClient(api_key=hf_token)

    stream = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=1024,
        stream=True,
    )

    for chunk in stream:
        yield (chunk.choices[0].delta.content)


def chat_message(role, content):
    """
    A function that transforms the chat content into a chat message
    Args:
        role: A string, either "user" or "assistant"
        content: A string, the content of the message
    Returns:
        A dictionary, containing the role and the content of the message.
    """
    
    return {"role": role, "content": content}


def sft_chat(prompt: str, history=[]):
    """
    A function that generates a response to a given prompt. 
    Args:
        prompt: A string, the prompt to be sent to the chatbot.
        history: A list of dictionaries, each dictionary being a message from the user or the assistant.
    Returns:
        A generator in the form of a single updated list of dictionaries, being a list of messages from the user and assistant
    """
    
    history.append(chat_message("user", prompt))
    yield history
    out = ""
    history.append(chat_message("assistant", out))
    for token in generate(history):
        out += token
        history[-1] = chat_message("assistant", out)
        yield history


def clear_textbox_field():
    """
    A function that clears the textbox field.
    """
    return None


def clear_both_fields():
    """
    A function that clears both the textbox and the chatbot.
    """
    return None, None


def save_sft_data(history):
    """
    A function that pushes the data to the hub.
    """
    # setup the info message to only show once
    global show_info 

    # preparing the submission
    data = {"contributor" : contributor_username}
    data["model_name"] = "Qwen/Qwen2.5-Coder-32B-Instruct"
    data["conversations"] = history

    # submitting the data
    sft_scheduler.append(data)
    
    # show the info message only once 
    if show_info:
        gr.Info("Data has been saved successfully (this message is only shown once)")
        gr.Info("The scheduler may take up to 5 minutes to push the data, please wait 🤗")
        show_info = False


with gr.Blocks() as demo:
    with gr.Tab("sft"):
        chatbot = gr.Chatbot(type="messages")
        textbox = gr.Textbox(show_label=False, submit_btn=True)
        textbox.submit(
            fn=sft_chat, inputs=[textbox, chatbot], outputs=[chatbot]
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[textbox]
        )
        with gr.Row():
            clear_button = gr.Button("Clear")
            clear_button.click(clear_both_fields, outputs=[textbox, chatbot])
            submit = gr.Button("save chat", variant="primary")
            submit.click(save_sft_data, inputs=[chatbot])

demo.launch(debug=True, show_error=True)
