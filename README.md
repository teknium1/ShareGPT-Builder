# ShareGPT Builder

ShareGPT Builder is a versatile Gradio application that provides two key functionalities for training Language Learning Models (LLMs). 

The application is designed to run locally, and submitted examples will be stored locally in the applications directory, but can also be served as a web application to anyone.

### Supervised Fine-Tuning (SFT) Conversation Sample Builder:

Firstly, it allows you to manually construct and store ShareGPT Formatted (SFT) conversations involving a system, a human, and GPT role or the Standard Formatted conversations involving a system, a user and an assistant. These conversations are automatically uploaded to huggingface.

For datasets using this format, refer to the [Hermes 2.5 Dataset here](https://huggingface.co/datasets/teknium/OpenHermes-2.5).

<img width="902" alt="image" src="https://github.com/user-attachments/assets/7f9a259b-a83d-4136-9fd7-30f63c0b7100">


### Direct Preference Optimization (DPO) RLHF Sample Builder:
Secondly, the application also includes a DPO Sample Builder. This feature enables the creation of sample comparison conversation responses, for Reinforcement Learning from Human Feedback (RLHF). This data gets automatically uploaded to the hub, and is in the Intel NeuralChat DPO format.

<img width="902" alt="image" src="https://github.com/user-attachments/assets/21f827c4-d709-45df-a2e4-6104e2436742">

### Datasets inspector
In this tab you can check all of your uploaded datasets, since the datasets are not uploaded in real time and there's an interval between the commits you will have to wait a little bit until the upload finishes as well as huggingface dataset viewer finished processing the newly commited data.

<img width="902" alt="image" src="https://github.com/user-attachments/assets/f637c051-8058-4aab-94e8-6535f39cd3e7">

## Installation

1. Clone the repository:
```bash
git clone https://github.com/teknium1/sharegpt-builder.git
```  

2. Navigate to the project directory:
```bash
cd sharegpt-builder
```  

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

4. login with your HuggingFace token with write access if you aren't already:
```bash
huggingface-cli login
```

## Usage

1. Run the Gradio application:
```bash
python app.py
```  

2. Open your web browser and navigate to `http://127.0.0.1:7860/`.

3. You will find 2 tabs, one for SFT and one for DPO, navigate to the one you want to contribute to and click there.

4. To add more turns to the conversation, fill the text field and press **↳ enter**

5. After adding all the turns, click `save chat` to upload the conversation.

6. The uploaded conversations can be viewed directly on the hub.

## Contributing
Contributions are welcome and greatly appreciated! Every little bit helps, and credit will always be given.

* `12/17/2024` : Thanks to [not-lain](https://github.com/not-lain) for fixing sharegpt template as well as adding the dataset viewer tab
* `12/13/2024` : Thanks to [aldryss](https://github.com/aldryss) for updating the UI 🔥
* `12/12/2024` : Thanks to [not-lain](https://github.com/not-lain) for the help switching from flask to gradio and supporting automatic dataset upload 🔥


Here are ways to contribute:

1. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
2. Fork the repository on GitHub and start making your changes to a new branch.
3. Write a test which shows that the bug was fixed or that the feature works as expected.
4. Send a pull request and bug the maintainer until it gets merged and published.

Alternatively, you can contribute via submission of bugs or feature requests to the issues tab.

## Note

The application is set to run in debug mode. For production use, make sure to turn off debug mode in `app.py`.

## License

This project is licensed under the terms of the MIT license.
