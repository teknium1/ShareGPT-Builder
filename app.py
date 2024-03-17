from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os

app = Flask(__name__)

def clean_entry(entry):
    return entry.strip().replace("\r", "").replace(" \n", "\n")

@app.route('/', defaults={'active_tab': 'sft'})
@app.route('/<active_tab>')
def index(active_tab):
    return render_template('index.html', active_tab=active_tab)

@app.route('/sft', methods=['POST'])
def form():
    system_prompt = clean_entry(request.form.get('system'))
    user_prompts = [clean_entry(prompt) for prompt in request.form.getlist('user[]')]
    gpt_responses = [clean_entry(response) for response in request.form.getlist('gpt[]')]

    data_to_append = {
        'conversations': [{'from': 'system', 'value': system_prompt}],
        'source': 'manual'
    }

    for user_prompt, gpt_response in zip(user_prompts, gpt_responses):
        data_to_append['conversations'].extend([
            {'from': 'human', 'value': user_prompt},
            {'from': 'gpt', 'value': gpt_response}
        ])

    addJsonData('./sft_data.json', data_to_append)

    return redirect(url_for('index', active_tab='sft'))

@app.route('/dpo', methods=['POST'])
def dpo_form():
    system_prompt = clean_entry(request.form.get('system'))
    prompts = request.form.getlist('prompt')
    chosen_responses = request.form.getlist('chosen')
    rejected_responses = request.form.getlist('rejected')

    data_to_append = {
        'system': system_prompt,
        'conversations': [],
        'source': 'manual'
    }

    for prompt, chosen, rejected in zip(prompts, chosen_responses, rejected_responses):
        data_to_append['conversations'].append({
            'prompt': clean_entry(prompt),
            'chosen': clean_entry(chosen),
            'rejected': clean_entry(rejected)
        })

    addJsonData('./dpo_data.json', data_to_append)

    return "Success", 200

def addJsonData(file_path, data_to_append):
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data.append(data_to_append)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([data_to_append], file, indent=4)

@app.route('/<type>_data.json', methods=['GET', 'PUT'])
def data(type):
    file_path = f'./{type}_data.json'
    if request.method == 'GET':
        with open(file_path, 'r', encoding='utf-8') as file:
            return jsonify(json.load(file))
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(request.get_json(), file, indent=4, sort_keys=False)
        return jsonify({'message': f'{type.upper()} data updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=7272)