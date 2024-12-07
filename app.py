import gradio as gr
from huggingface_hub.utils._auth import get_token
from huggingface_hub import whoami
import datetime

from dataset_uploader import ParquetScheduler

# get token if we're already logged in
hf_token = get_token()

contributor_username = whoami()["name"]
show_info = True
# will remove the metadata field from chat history
remove_metadata = True 
every = 1 # we push once every 5 minutes

# IMPORTANT !!!
# change these values
# repo to where we push the data
sft_scheduler = ParquetScheduler(repo_id="not-lain/sft", every=every)





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
    if history == [] or (len(history) > 1 and history[-1]["role"] == "assistant"):
        history.append(chat_message("user", prompt))
    else:
        history.append(chat_message("assistant", prompt))
    return history


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


def save_sft_data(system_prompt="", history=[]):
    """
    A function that pushes the data to the hub.
    """
    
    # setup the info message to only show once
    global show_info

    # case user clicked submit and did not have any chat history
    if history == []:
        gr.Error("you need to setup a chat first")
        return
    
    # case history ends with user prompt
    if history[-1]["role"] == "user" : 
        gr.Error("history needs to end with assistant prompt")
        return

    # preparing the submission
    data = {"contributor": contributor_username}
    # removes the extra metadata field from the chat history
    if remove_metadata : 
        for i in range(len(history)):
            sample = history[i]
            history[i] = {"role":sample["role"],"content":sample["content"]}
    # add system prompt if provided
    system_prompt = system_prompt.strip()
    if system_prompt != "":
        sys = chat_message("system", system_prompt)
        history.insert(0, sys )
    

    data["timestamp"] = str(datetime.datetime.now(datetime.UTC))
    data["conversations"] = history

    # submitting the data
    sft_scheduler.append(data)

    # show the info message only once
    if show_info:
        gr.Info("Data has been saved successfully (this message is only shown once)")
        gr.Info(
            "The scheduler may take up to 5 minutes to push the data, please wait 🤗"
        )
        show_info = False


def undo_chat(history):
    return history[:-2]


with gr.Blocks() as demo:
    with gr.Tab("sft"):
        with gr.Accordion("system prompt", open=False):
            system_prompt = gr.TextArea(show_label=False, container=False)
        
        chatbot = gr.Chatbot(
            type="messages", show_copy_button=True, show_copy_all_button=True
        )
        textbox = gr.Textbox(show_label=False, submit_btn=True)
        textbox.submit(
            fn=sft_chat, inputs=[textbox, chatbot], outputs=[chatbot]
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[textbox]
        )
        chatbot.undo(undo_chat, inputs=chatbot, outputs=chatbot)
        with gr.Row():
            clear_button = gr.Button("Clear")
            clear_button.click(clear_both_fields, outputs=[textbox, chatbot])
            submit = gr.Button("save chat", variant="primary")
            submit.click(save_sft_data, inputs=[system_prompt, chatbot])
    

demo.launch(debug=True, show_error=True)
