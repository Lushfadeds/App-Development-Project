document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const searchInput = document.querySelector('input[type="search"]');
    const tableRows = document.querySelectorAll('tbody tr');
    const roleButton = document.querySelector('.dropdown-toggle');

    let selectedRole = 'all'; // Default value to show all roles
    let lastSelectedItem = null; // Store the last selected item

    dropdownItems.forEach(item => {
        if (item.textContent.trim().toLowerCase() === 'all') {
            item.style.display = 'none';
        }
    });

    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            // Show all dropdown items first
            dropdownItems.forEach(i => {
                i.style.display = 'block';
            });

            selectedRole = this.textContent.toLowerCase();
            roleButton.textContent = this.textContent; // Update button text

            this.style.display = 'none'; // Hide the selected item

            filterTable();
        });
    });

    // Add input event to search
    searchInput.addEventListener('input', filterTable);

    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase();

        tableRows.forEach(row => {
            const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const email = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const contact = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
            const role = row.querySelector('td:nth-child(4)').textContent.toLowerCase();

            const matchesSearch = name.includes(searchTerm) ||
                                email.includes(searchTerm) ||
                                contact.includes(searchTerm);

            const matchesRole = selectedRole === 'all' || role === selectedRole;

            // Show row only if it matches both search and role filters
            row.style.display = (matchesSearch && matchesRole) ? '' : 'none';
        });
    }
});

var exampleModal = document.getElementById('staticBackdrop')
exampleModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;
    var recipient = button.getAttribute('data-bs-whatever');
    var userId = button.getAttribute('data-id');  // Get user ID from button
    console.log(userId)

    var modalTitle = exampleModal.querySelector('.modal-title');
    modalTitle.textContent = recipient;

    var modalConfirm = exampleModal.querySelector('#confirm');
    var modalConfirmDel = exampleModal.querySelector('#confirm-del');
    var modalFormConfirm = exampleModal.querySelector('#confirm-form');
    var modalBody = exampleModal.querySelector('.modal-body');
    var modalFooter = exampleModal.querySelector('.modal-footer');
    var modalCreate = exampleModal.querySelector('.modal-create');
    var modalDelete = exampleModal.querySelector('.modal-delete');

    if (recipient === 'Delete User') {
        modalConfirmDel.textContent = 'Delete';
        modalDelete.style.display = 'block'
        modalCreate.style.display = 'none'
        modalConfirmDel.classList.replace('btn-primary', 'btn-danger');
        modalFormConfirm.setAttribute("action", "/delete_user/" + userId);

    } else if (recipient === 'Edit User'){
        modalConfirm.textContent = 'Save Changes';
        modalDelete.style.display = 'none'
        modalCreate.style.display = 'block'
        modalConfirm.classList.replace('btn-danger', 'btn-primary');

        // Get the form and update its action
        const form = exampleModal.querySelector('#register-form');
        form.setAttribute("action", "/admin_edit/" + userId);

        // Get the current row data
        const row = button.closest('tr');
        const name = row.querySelector('td:nth-child(1)').textContent.trim();
        const email = row.querySelector('td:nth-child(2)').textContent.trim();
        const phone = row.querySelector('td:nth-child(3)').textContent.trim();
        const role = row.querySelector('td:nth-child(4)').textContent.toLowerCase().trim();

        // Populate the form fields
        form.querySelector('#name').value = name;
        form.querySelector('#email').value = email;
        form.querySelector('#phone').value = phone;
        form.querySelector(`#${role}`).checked = true;

        // Make profile picture optional for edit
        form.querySelector('#profile').removeAttribute('required');

    } else {
        modalConfirm.textContent = 'Save Changes';
        modalDelete.style.display = 'none'
        modalCreate.style.display = 'block'
        modalConfirm.classList.replace('btn-danger', 'btn-primary')

        // Reset form for create
        const form = exampleModal.querySelector('#register-form');
        form.reset();
        form.setAttribute("action", "/admin_add");
        form.querySelector('#profile').setAttribute('required', '');
    }
});


