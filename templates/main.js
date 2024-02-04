function submitForm(e, formId, tabName) {
    e.preventDefault();
    var form = document.getElementById(formId);
    fetch(form.action, {
        method: form.method,
        body: new FormData(form)
    })
    .then(response => {
        if (response.ok) {
            // On success, open the specified tab, update the URL, and refresh the page
            openTab(tabName);
            history.pushState({}, "", "/");
            location.reload();  // Add this line to refresh the page
        } else {
            alert("Form submission failed.");
        }
    })
    .catch(error => console.error('Error:', error));
}