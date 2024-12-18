import gradio as gr
from huggingface_hub import whoami
import datetime
from dataset_uploader import ParquetScheduler

##########
# Setup  #
##########

contributor_username = whoami()["name"]

# only show an info the first time uploading to the hub
show_info = True 

every = 1  # we push once every 1 minute (use 5 if there are lots of people using the same HF token)

choices = ["sharegpt","standard"]

# schedulers
schedulers = {
    "sft-sharegpt": ParquetScheduler(repo_id=f"{contributor_username}/sft-sharegpt", every=every),
    "sft-standard": ParquetScheduler(repo_id=f"{contributor_username}/sft-standard", every=every),
    "dpo-sharegpt": ParquetScheduler(repo_id=f"{contributor_username}/dpo-sharegpt", every=every),
    "dpo-standard": ParquetScheduler(repo_id=f"{contributor_username}/dpo-standard", every=every),
}


##########
# Utils  #
##########


def chat_message(role, content, prompt_type=None):
    """
    A function that transforms the chat content into a chat message
    Args:
        role: A string, either "user" or "assistant"
        content: A string, the content of the message
        prompt_type: A string, either "standard" or "sharegpt"
    Returns:
        A dictionary, the message to be sent to the chatbot.
    """
    if prompt_type == "sharegpt":
        if role == "user":
            role = "human"
        elif role == "assistant":
            role = "gpt"
        # sharegpt chat format
        return {"from": role, "value": content}
    else:
        return {"role": role, "content": content}


def chat(prompt: str, history=[]):
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


def clear_3_fields():
    """
    A function that clears both the textbox and the chatbot.
    """
    return None, None, None


def setup_submission(system_prompt="", history=[], chat_format="sharegpt"):
    # removes the extra metadata field from the chat history and format sharegpt accordingly
    for i in range(len(history)):
        sample = history[i]
        history[i] = chat_message(
            sample["role"], sample["content"], prompt_type=chat_format
        )

    # add system prompt if provided
    system_prompt = system_prompt.strip()
    if system_prompt != "":
        sys = chat_message("system", system_prompt, prompt_type=chat_format)
        history.insert(0, sys)

    return history


def save_sft_data(system_prompt="", history=[], sft_chat_format="sharegpt"):
    """
    A function that pushes the data to the hub.
    """

    # setup the info message to only show once
    global show_info
    scheduler = schedulers[f"sft-{sft_chat_format}"]

    # case user clicked submit and did not have any chat history
    if history == []:
        raise gr.Error("you need to setup a chat first")

    # case history ends with user prompt
    if history[-1]["role"] == "user":
        raise gr.Error("history needs to end with assistant prompt")

    history = setup_submission(system_prompt, history, sft_chat_format)
    # preparing the submission
    data = {"contributor": contributor_username}
    data["timestamp"] = str(datetime.datetime.now(datetime.UTC))
    data["chat_format"] = sft_chat_format
    data["conversations"] = history

    # submitting the data
    scheduler.append(data)

    # show the info message only once
    if show_info:
        gr.Info("Data has been saved successfully (this message is only shown once)")
        gr.Info(
            "The scheduler may take up to 1 minute to push the data, please wait 🤗"
        )
        show_info = False


def save_dpo_data(
    system_prompt="", history=[], chosen="", rejected="", dpo_chat_format="sharegpt"
):
    """
    A function that pushes the data to the hub.
    """

    # setup the info message to only show once
    global show_info
    scheduler = schedulers[f"dpo-{dpo_chat_format}"]

    # case user clicked submit and did not have any chat history
    if history == []:
        raise gr.Error("you need to setup a chat first")

    # case history ends with user prompt
    if history[-1]["role"] == "assistant":
        raise gr.Error("history needs to end with user prompt")

    # case chosen and rejected are not full
    chosen, rejected = chosen.strip(), rejected.strip()
    if chosen == "" or rejected == "":
        raise gr.Error(
            "both chosen and rejected need to have a text when you click the submit button"
        )

    history = setup_submission(system_prompt, history, dpo_chat_format)
    chosen_chat, rejected_chat = history.copy(), history.copy()
    chosen_chat.append(chat_message("user", chosen, dpo_chat_format))
    rejected_chat.append(chat_message("user", rejected, dpo_chat_format))

    # preparing the submission
    data = {"contributor": contributor_username}

    data["timestamp"] = str(datetime.datetime.now(datetime.UTC))
    data["chat_format"] = dpo_chat_format
    data["prompt"] = history
    data["chosen"] = chosen_chat
    data["rejected"] = rejected_chat

    # submitting the data
    scheduler.append(data)

    # show the info message only once
    if show_info:
        gr.Info("Data has been saved successfully (this message is only shown once)")
        gr.Info(
            "The scheduler may take up to 1 minute to push the data, please wait 🤗"
        )
        show_info = False


def undo_chat(history):
    return history[:-2]


##############
# Interface  #
##############

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center'>ShareGPT-Builder</h1>")

    #### SFT ####
    with gr.Tab("SFT"):
        with gr.Accordion("system prompt", open=False):
            system_prompt = gr.TextArea(show_label=False, container=False)
        sft_chat_format = gr.Radio(choices=choices, value="sharegpt")

        chatbot = gr.Chatbot(
            type="messages", show_copy_button=True, show_copy_all_button=True
        )
        textbox = gr.Textbox(show_label=False, submit_btn=True)
        textbox.submit(
            fn=chat, inputs=[textbox, chatbot], outputs=[chatbot]
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[textbox]
        )
        chatbot.undo(undo_chat, inputs=chatbot, outputs=chatbot)
        with gr.Row():
            clear_button = gr.Button("Clear")
            clear_button.click(clear_both_fields, outputs=[textbox, chatbot])
            submit = gr.Button("save chat", variant="primary")
            submit.click(
                save_sft_data, inputs=[system_prompt, chatbot, sft_chat_format]
            ).then(clear_both_fields, outputs=[textbox, chatbot])

    #### DPO ####
    with gr.Tab("DPO"):
        with gr.Accordion("system prompt", open=False):
            dpo_system_prompt = gr.TextArea(show_label=False, container=False)
        dpo_chat_format = gr.Radio(choices=choices, value="sharegpt")
        dpo_chatbot = gr.Chatbot(
            type="messages", show_copy_button=True, show_copy_all_button=True
        )
        gr.Markdown(
            "type in either of these fields and press enter, when you are ready for the final submission fill both fields, don't press enter and click on the save chat button"
        )
        with gr.Row():
            dpo_rejected_textbox = gr.Textbox(label="rejected (or add chat)", render=True)
            dpo_chosen_textbox = gr.Textbox(label="chosen (or add chat)")
        # submit using either of these fields
        dpo_chosen_textbox.submit(
            fn=chat, inputs=[dpo_chosen_textbox, dpo_chatbot], outputs=[dpo_chatbot]
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[dpo_chosen_textbox]
        )
        dpo_rejected_textbox.submit(
            fn=chat,
            inputs=[dpo_rejected_textbox, dpo_chatbot],
            outputs=[dpo_chatbot],
        ).then(  # empty field for convinience
            clear_textbox_field, outputs=[dpo_rejected_textbox]
        )
        dpo_chatbot.undo(undo_chat, inputs=dpo_chatbot, outputs=dpo_chatbot)
        with gr.Row():
            dpo_clear_button = gr.Button("Clear")
            dpo_clear_button.click(
                clear_3_fields,
                outputs=[dpo_chosen_textbox, dpo_rejected_textbox, dpo_chatbot],
            )
            dpo_submit = gr.Button("save chat", variant="primary")
            dpo_submit.click(
                save_dpo_data,
                inputs=[
                    dpo_system_prompt,
                    dpo_chatbot,
                    dpo_chosen_textbox,
                    dpo_rejected_textbox,
                    dpo_chat_format,
                ],
            ).then(
                clear_3_fields,
                outputs=[dpo_chosen_textbox, dpo_rejected_textbox, dpo_chatbot],
            )
    with gr.Tab("Inspect datasets"): 
        dataset = gr.Dropdown(choices=list(schedulers.keys()))
        @gr.render(inputs=dataset)
        def show_dataset(dataset) :
            gr.HTML(f""" <iframe
            src="https://huggingface.co/datasets/{contributor_username}/{dataset}/embed/viewer/default/train?row=0"
            frameborder="0"
            width="100%"
            height="560px"
            ></iframe>""")

if __name__ == "__main__":
    demo.launch(debug=True, show_error=True)
