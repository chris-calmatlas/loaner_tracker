document.addEventListener('DOMContentLoaded', function() {
    const buttonSave = document.getElementById('button_save');
    const buttonCancel = document.getElementById('button_cancel');
    const buttonEdit = document.getElementById('button_edit');
    const buttonBack = document.getElementById('button_back');
    const status = document.getElementById('id_status');
    const assigned_to = document.getElementById('id_assigned_to');

    if (buttonCancel) {
        buttonCancel.addEventListener('click', function() {
            const fieldSet = document.querySelector('#thing_form .authFieldset')
            fieldSet.disabled = true
            fieldSet.parentNode.reset()
        });
    }

    if (buttonEdit) {
        buttonEdit.addEventListener('click', function() {
            const fieldSet = document.querySelector('#thing_form .authFieldset')
            fieldSet.disabled = false
        });
    }

    if (assigned_to) {
        assigned_to.addEventListener('input', function(e) {
            if (e.target.value != "") {
                status.querySelector('option[value="assigned"]').selected = true;
            }
        });
    }

    if (status) {
        status.addEventListener('change', validateStatus);
    }

    validateStatus()

    function validateStatus() {
        if (status.value != "assigned") {
            assigned_to.value = "";
        }
        if (status.value == "missing") {
            assigned_to.disabled = true;
        } else {
            assigned_to.disabled = false;
        }
    }
});