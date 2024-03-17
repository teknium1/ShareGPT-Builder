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
    let allFieldsFilled = true;

    if (tabName === 'sft' && document.getElementsByClassName('turn').length <= 1) {
        showToast("Please add at least one turn.", 'error');
        return;
    }

    for (let i = 0; i < formElements.length; i++) {
        if (formElements[i].tagName === 'TEXTAREA' && formElements[i].value.trim() === '') {
            allFieldsFilled = false;
            break;
        }
    }

    if (allFieldsFilled) {
        fetch(form.action, {
            method: form.method,
            body: new FormData(form)
        })
        .then(response => {
            if (response.ok) {
                openTab(tabName);
                history.pushState({}, "", "/");
                form.reset();
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

function openTab(tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tablink");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    const buttonElement = document.querySelector(`.tablink[onclick="openTab('${tabName}', this)"]`);
    if (buttonElement) {
        buttonElement.className += " active";
    }

    const jsonModal = document.getElementById('jsonModal');
    jsonModal.style.display = 'none';
}

document.getElementById("defaultOpen").click();

function addTurn() {
    const turns = document.getElementById('turns');
    const newTurn = document.createElement('div');
    newTurn.classList.add("turn");
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
    turns.appendChild(newTurn);
    turns.scrollTop = turns.scrollHeight;
}

function deleteTurn(button) {
    const turn = button.closest('.turn');
    turn.remove();
}

function openJsonModal(type) {
    const jsonModal = document.getElementById('jsonModal');
    const jsonViewer = document.getElementById('jsonViewer');
    const editJsonBtn = document.getElementById('editJsonBtn');
    const saveJsonBtn = document.getElementById('saveJsonBtn');

    fetch(`/${type}_data.json`)
        .then(response => response.json())
        .then(data => {
            jsonViewer.textContent = JSON.stringify(data, null, 2);
            hljs.highlightElement(jsonViewer);
            jsonModal.style.display = 'flex';

            editJsonBtn.onclick = () => {
                jsonViewer.contentEditable = true;
                jsonViewer.focus();
                editJsonBtn.style.display = 'none';
                saveJsonBtn.style.display = 'inline-block';
            };

            saveJsonBtn.onclick = () => {
                const updatedData = JSON.parse(jsonViewer.textContent);
                fetch(`/${type}_data.json`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedData, null, 2)
                })
                .then(() => {
                    jsonViewer.contentEditable = false;
                    editJsonBtn.style.display = 'inline-block';
                    saveJsonBtn.style.display = 'none';
                    showToast('JSON data updated successfully!', 'success');
                })
                .catch(error => {
                    console.error('Error updating JSON data:', error);
                    showToast('Failed to update JSON data.', 'error');
                });
            };
        })
        .catch(error => {
            console.error('Error fetching JSON data:', error);
            showToast('Failed to fetch JSON data.', 'error');
        });
}

const closeBtn = document.getElementsByClassName('close')[0];
closeBtn.onclick = () => {
    const jsonModal = document.getElementById('jsonModal');
    jsonModal.style.display = 'none';
};

window.onclick = (event) => {
    const jsonModal = document.getElementById('jsonModal');
    if (event.target === jsonModal) {
        jsonModal.style.display = 'none';
    }
};