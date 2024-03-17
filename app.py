from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os

app = Flask(__name__)

def clean_entry(entry):
    return entry.strip().replace("\r", "").replace(" \n", "\n")

# Route for index/main page
@app.route('/', defaults={'active_tab': 'sft'})
@app.route('/<active_tab>')
def index(active_tab):
    return render_template('index.html', active_tab=active_tab)

# Route for the SFT Dataset Builder.
@app.route('/sft', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Extract form data
        system_prompt = clean_entry(request.form.get('system'))
        user_prompts = [clean_entry(prompt) for prompt in request.form.getlist('user[]')]
        gpt_responses = [clean_entry(response) for response in request.form.getlist('gpt[]')]

        data_to_append = {
            'conversations': [{'from': 'system', 'value': system_prompt}],
            'source': 'manual'
        }

        for user_prompt, gpt_response in zip(user_prompts, gpt_responses):
            data_to_append['conversations'].append({'from': 'human', 'value': user_prompt})
            data_to_append['conversations'].append({'from': 'gpt', 'value': gpt_response})

        file_path = './sft_data.json'

        if os.path.exists(file_path):
            with open(file_path, 'r+', encoding='utf-8') as file:
                data = json.load(file)
                data.append(data_to_append)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump([data_to_append], file, indent=4)

    return redirect(url_for('index', active_tab='sft'))

# Route for the DPO dataset builder
@app.route('/dpo', methods=['GET', 'POST'])
def dpo_form():
    if request.method == 'POST':
        # Extract form data
        data_to_append = {
            'system': clean_entry(request.form.get('system')),
            'question': clean_entry(request.form.get('prompt')),
            'chosen': clean_entry(request.form.get('chosen')),
            'rejected': clean_entry(request.form.get('rejected')),
            'source': 'manual'
        }

        file_path = './dpo_data.json'

        if os.path.exists(file_path):
            with open(file_path, 'r+', encoding='utf-8') as file:
                data = json.load(file)
                data.append(data_to_append)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump([data_to_append], file, indent=4)

        return "Success", 200

    return render_template('index.html', active_tab='dpo')

@app.route('/sft_data.json', methods=['GET', 'PUT'])
def sft_data():
    file_path = './sft_data.json'
    if request.method == 'GET':
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        return jsonify({'message': 'SFT data updated successfully'})

@app.route('/dpo_data.json', methods=['GET', 'PUT'])
def dpo_data():
    file_path = './dpo_data.json'
    if request.method == 'GET':
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        return jsonify({'message': 'DPO data updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=7272)