# ShareGPT Builder

ShareGPT Builder is a simple Flask application that allows you to manually build and store ShareGPT Formatted conversations for training LLM's with a system, a human, and GPT role. The conversations are stored in a JSON file, and automatically append themselves if the data file already exists.

For example datasets using this format, see my [Hermes 2.5 Dataset here](https://huggingface.co/datasets/teknium/OpenHermes-2.5).

### New: There is now DPO Sample Building as well.


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
pip install flask
```  

## Usage

1. Run the Flask application:
```bash
python app.py
```  


2. Open your web browser and navigate to `http://localhost:5000`.

3. You will see a form with three text areas: one for the system prompt, one for the user prompt, and one for the GPT response. Fill in these fields and click "Submit" to save the conversation to the `data.json` file.

4. To add more turns to the conversation, click the "Add Turn" button. This will add two more text areas: one for the user prompt and one for the GPT response.

5. After adding all the turns, click "Submit" to save the entire conversation.

6. The saved conversations can be viewed in the `data.json` file.

## Contributing

Contributions are welcome and greatly appreciated! Every little bit helps, and credit will always be given.

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