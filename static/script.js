function showToast(message, type) {
    const toast = document.getElementById('toast');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function submitForm(e, tabName) {
    e.preventDefault();
    const form = document.getElementById(tabName === 'sft' ? 'sftForm' : 'dpoForm');
    const formElements = form.elements;
    const allFieldsFilled = Array.from(formElements).every(el => {
        if (el.tagName === 'TEXTAREA') {
            if (el.id === 'system') {
                return true;
            } else {
                return el.value.trim() !== '';
            }
        }
        return true;
    });

    const turns = document.getElementById(tabName + 'Turns');
    const turnElements = turns.getElementsByClassName('turn');
    if (turnElements.length  === 0) {
        showToast("Please add at least one turn.", 'error');
        return;
    }

    if (allFieldsFilled) {
        fetch(form.action, {
            method: form.method,
            body: new FormData(form)
        })
        .then(response => {
            if (response.ok) {
                resetForm(tabName);
                openJsonModal(tabName);
                showToast("Submitted successfully!", 'success');
            } else {
                showToast("Form submission failed.", 'error');
            }
        })
        .catch(error => console.error('Error:', error));
    } else {
        showToast("Fill all the fields.", 'error');
    }
}

function resetForm(formType) {
    const form = document.getElementById(formType === 'sft' ? 'sftForm' : 'dpoForm');
    const turns = document.getElementById(formType + 'Turns');
    const turnElements = turns.getElementsByClassName('turn');

    form.reset()
    while (turnElements.length > 1) {
        turnElements[turnElements.length - 1].remove();
    }

    showToast("Form Resetted", 'success')
}

function openTab(tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    Array.from(tabcontent).forEach(el => el.style.display = "none");

    const tablinks = document.getElementsByClassName("tablink");
    Array.from(tablinks).forEach(el => el.className = el.className.replace(" active", ""));

    document.getElementById(tabName).style.display = "block";
    const buttonElement = document.querySelector(`.tablink[onclick="openTab('${tabName}', this)"]`);
    if (buttonElement) {
        buttonElement.className += " active";
    }

    openJsonModal(tabName);
}

document.getElementById("defaultOpen").click();

function addTurn(formType) {
    const turns = document.getElementById(formType + 'Turns');
    const newTurn = document.createElement('div');
    newTurn.classList.add("turn");
    
    if (formType === 'sft') {
        newTurn.innerHTML = `
            <div>
                <label for="user">User:</label>
                <textarea id="user" name="user[]"></textarea>
            </div>
            <div>
                <label for="gpt">GPT:</label>
                <textarea id="gpt" name="gpt[]"></textarea>
            </div>
            <button type="button" class="delete-turn" onclick="deleteTurn(this)">Delete</button>
        `;
    } else {
        newTurn.innerHTML = `
            <div>
                <label for="prompt">Prompt:</label>
                <textarea id="prompt" name="prompt"></textarea>
            </div>
            <div>
                <label for="chosen">Chosen:</label>
                <textarea id="chosen" name="chosen"></textarea>
            </div>
            <div>
                <label for="rejected">Rejected:</label>
                <textarea id="rejected" name="rejected"></textarea>
            </div>
            <button type="button" class="delete-turn" onclick="deleteTurn(this)">Delete</button>
        `;
    }
    
    turns.appendChild(newTurn);
    turns.scrollTop = turns.scrollHeight;
}

function deleteTurn(button) {
    const turn = button.closest('.turn');
    turn.remove();
}

async function openJsonModal(type) {
    const jsonViewer = document.getElementById('jsonViewer');
    const editJsonBtn = document.getElementById('editJsonBtn');
    const saveJsonBtn = document.getElementById('saveJsonBtn');

    const propertyOrder = type === 'dpo' ? ['system', 'conversations', 'prompt', 'chosen', 'rejected', 'source'] : ['conversations', 'from', 'value', 'source'];

    try {
        const response = await fetch(`/${type}_data.json`);
        const data = await response.json();
        jsonViewer.textContent = JSON.stringify(data, propertyOrder, 2);
        hljs.highlightElement(jsonViewer);

        editJsonBtn.onclick = () => {
            jsonViewer.contentEditable = true;
            jsonViewer.focus();
            editJsonBtn.style.display = 'none';
            saveJsonBtn.style.display = 'inline-block';
        };

        saveJsonBtn.onclick = async () => {
            try {
                const updatedData = JSON.parse(jsonViewer.textContent);
                await fetch(`/${type}_data.json`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedData, propertyOrder, 2)
                });
                jsonViewer.contentEditable = false;
                editJsonBtn.style.display = 'inline-block';
                saveJsonBtn.style.display = 'none';
                showToast('JSON data updated successfully!', 'success');
            } catch (error) {
                console.error('Error updating JSON data:', error);
                showToast('Failed to update JSON data.', 'error');
            }
        };
    } catch (error) {
        console.error('Error fetching JSON data:', error);
        showToast('Failed to fetch JSON data.', 'error');
    }
}
