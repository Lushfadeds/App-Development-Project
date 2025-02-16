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
            const day = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const productsSold = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const dailySale = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
            const dailyCustomers = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
            const uniqueCustomers = row.querySelector('td:nth-child(5)').textContent.toLowerCase();
            const moneySpent = row.querySelector('td:nth-child(6)').textContent.toLowerCase();

            const matchesSearch = day.includes(searchTerm) ||
                                productsSold.includes(searchTerm) ||
                                dailySale.includes(searchTerm) ||
                                dailyCustomers.includes(searchTerm) ||
                                uniqueCustomers.includes(searchTerm) ||
                                moneySpent.includes(searchTerm);

            const matchesRole = selectedRole === 'all' || selectedRole === 'someRole'; // Add role-based logic here if necessary

            // Show row only if it matches both search and role filters
            row.style.display = (matchesSearch && matchesRole) ? '' : 'none';
        });
    }
});

var exampleModal = document.getElementById('staticBackdrop');

exampleModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;
    var recipient = button.getAttribute('data-bs-whatever');
    var recordId = button.getAttribute('data-id'); // Get the record ID from the button
    console.log(recordId);

    var modalTitle = exampleModal.querySelector('.modal-title');
    modalTitle.textContent = recipient;

    var modalConfirm = exampleModal.querySelector('#confirm');
    var modalConfirmDel = exampleModal.querySelector('#confirm-del');
    var modalFormConfirm = exampleModal.querySelector('#confirm-form');
    var modalBody = exampleModal.querySelector('.modal-body');
    var modalFooter = exampleModal.querySelector('.modal-footer');
    var modalCreate = exampleModal.querySelector('.modal-create');
    var modalDelete = exampleModal.querySelector('.modal-delete');

    if (recipient === 'Delete Data') {
        modalConfirmDel.textContent = 'Delete';
        modalDelete.style.display = 'block';
        modalCreate.style.display = 'none';
        modalConfirmDel.classList.replace('btn-primary', 'btn-danger');
        modalFormConfirm.setAttribute("action", "/delete_analytics/" + recordId);

    } else if (recipient === 'Edit Data') {
        modalConfirm.textContent = 'Save Changes';
        modalDelete.style.display = 'none';
        modalCreate.style.display = 'block';
        modalConfirm.classList.replace('btn-danger', 'btn-primary');

        // Get the form and update its action
        const form = exampleModal.querySelector('#stats-form');
        form.setAttribute("action", "/update_analytics/" + recordId);

        // Get the current row data
        const row = button.closest('tr');
        const day = row.querySelector('td:nth-child(1)').textContent.trim();
        const productsSold = row.querySelector('td:nth-child(2)').textContent.trim();
        const dailySale = row.querySelector('td:nth-child(3)').textContent.trim();
        const dailyCustomers = row.querySelector('td:nth-child(4)').textContent.trim();
        const uniqueCustomers = row.querySelector('td:nth-child(5)').textContent.trim();
        const moneySpent = row.querySelector('td:nth-child(6)').textContent.trim();
        const expenses = row.querySelector('td:nth-child(7)').textContent.trim();
        const laborCosts = row.querySelector('td:nth-child(8)').textContent.trim();
        const energyCosts = row.querySelector('td:nth-child(9)').textContent.trim();

        // Populate the form fields
        form.querySelector('#day').value = day;
        form.querySelector('#products_sold').value = productsSold;
        form.querySelector('#daily_sale').value = dailySale;
        form.querySelector('#daily_customers').value = dailyCustomers;
        form.querySelector('#daily_unique_customers').value = uniqueCustomers;
        form.querySelector('#money_spent_customer').value = moneySpent;
        form.querySelector('#expenses').value = expenses;
        form.querySelector('#labor_costs').value = laborCosts;
        form.querySelector('#energy_costs').value = energyCosts;
        console.log('huh')

    } else {
        modalConfirm.textContent = 'Save Changes';
        modalDelete.style.display = 'none';
        modalCreate.style.display = 'block';
        modalConfirm.classList.replace('btn-danger', 'btn-primary');

        // Reset form for creating a new record
        const form = exampleModal.querySelector('#stats-form');
        form.reset();
        form.setAttribute("action", "/analytics_add");
    }
});

