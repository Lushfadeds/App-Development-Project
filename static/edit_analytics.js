const openEdit = document.getElementById('openEdit');
const addEdit = document.getElementById('addEdit');
const doneEdit = document.getElementById('closeEdit');
const dataEdit = document.getElementById('dataEdit');

openEdit.addEventListener('click', () => {
    const icons = document.querySelectorAll('.fa-regular');
    icons.forEach(function(icon) {
        icon.classList.toggle('d-none');
    });

    editToggle();

});

doneEdit.addEventListener('click', () => {
    const icons = document.querySelectorAll('.fa-regular');
    icons.forEach(function(icon) {
        icon.classList.toggle('d-none');
    });

    editToggle();

});

function editToggle() {
    addEdit.classList.toggle('d-none');
    openEdit.classList.toggle('d-none');
    doneEdit.classList.toggle('d-none');
    dataEdit.classList.toggle('d-none')
}

document.addEventListener("DOMContentLoaded", function() {
    const icons = document.querySelectorAll('.fa-regular.fa-square-minus');

    icons.forEach(icon => {
        icon.addEventListener('click', function() {
            const parentDiv = icon.closest('.col');
            parentDiv.classList.toggle('d-none');
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const openEdit = document.getElementById('openEdit');
    const closeEdit = document.getElementById('closeEdit');
    const addEdit = document.getElementById('addEdit');
    const overlay = document.getElementById('overlay');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.container-fluid');

    // Function to toggle delete icons
    function toggleDeleteIcons(show) {
        document.querySelectorAll('.fa-square-minus').forEach(icon => {
            icon.classList.toggle('d-none', !show);
        });
    }

    // Open Edit Mode
    openEdit.addEventListener('click', () => {
        overlay.classList.remove('d-none');
        closeEdit.classList.remove('d-none');
        addEdit.classList.remove('d-none');
        openEdit.classList.add('d-none');
        toggleDeleteIcons(true);

        // Make items draggable
        document.querySelectorAll('.col').forEach(item => {
            item.draggable = true;
            item.classList.add('draggable');
        });

        // Make template cards draggable
        const templateCards = document.querySelectorAll('.template-item');
        templateCards.forEach(card => {
            card.draggable = true;
        });

        // Initialize row handlers
        initializeRowDragHandlers();
    });

    // Close Edit Mode
    if (closeEdit && sidebar && mainContent) {
        closeEdit.addEventListener('click', async () => {
            console.log('Close Edit button clicked');

            const layout = captureLayout();

            try {
                const response = await fetch('/save_layout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(layout)
                });

                const data = await response.json();
                if (data.status === 'success') {
                    console.log('Layout saved successfully');
                }
            } catch (error) {
                console.error('Error saving layout:', error);
            }

            // Close edit mode
            overlay.classList.add('d-none');
            closeEdit.classList.add('d-none');
            addEdit.classList.add('d-none');
            openEdit.classList.remove('d-none');
            sidebar.classList.add('d-none');
            console.log('Sidebar should be hidden now');
            toggleDeleteIcons(false);

            // Remove draggable attributes
            document.querySelectorAll('.draggable').forEach(item => {
                item.classList.remove('draggable');
                item.draggable = false;
            });

            // Make template cards not draggable
            const templateCards = document.querySelectorAll('.template-item');
            templateCards.forEach(card => {
                card.draggable = false;
            });
        });
    } else {
        console.error('One or more elements not found:', {
            closeEdit,
            sidebar,
            mainContent
        });
    }

    // Toggle Sidebar
    addEdit.addEventListener('click', () => {
        sidebar.classList.toggle('d-none');
        mainContent.classList.toggle('content-shift');
    });

    // Function to capture the current layout
    function captureLayout() {
        // Only capture the analytics section
        const analyticsSection = document.querySelector('.analytics-section') || mainContent;
        const rows = analyticsSection.querySelectorAll('.row');
        const layout = [];

        rows.forEach(row => {
            const rowCards = [];
            row.querySelectorAll('.col').forEach(card => {
                const title = card.querySelector('h5');
                const content = card.querySelector('div:not(.card)');

                if (title && content) {
                    rowCards.push({
                        type: title.textContent.trim(),
                        content: content.innerHTML.trim(),
                    });
                }
            });
            if (rowCards.length > 0) {
                layout.push(rowCards);
            }
        });

        return layout;
    }

    // Function to apply loaded layout
    function applyLayout(layout) {
        // Find the analytics section
        const analyticsSection = document.querySelector('.analytics-section') || mainContent;
        if (!analyticsSection) return;

        // Store the analytics title and buttons
        const analyticsHeader = analyticsSection.querySelector('h1, .analytics-header');
        const headerContent = analyticsHeader ? analyticsHeader.outerHTML : '';

        // Clear existing content but keep the header
        analyticsSection.innerHTML = headerContent;

        // Create rows and add cards
        layout.forEach(rowCards => {
            const row = document.createElement('div');
            row.className = 'row g-3 mt-3';

            rowCards.forEach(cardData => {
                const colDiv = document.createElement('div');
                colDiv.className = 'col';

                const cardDiv = document.createElement('div');
                cardDiv.className = 'card p-3 shadow-sm';

                // Special handling for different card types
                if (cardData.type === 'Daily Report') {
                    cardDiv.innerHTML = `
                        <h5>${cardData.type}</h5>
                        <div class="dropdown position-absolute top-0 end-0">
                            <button class="btn" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fa-solid fa-ellipsis-vertical"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#">Daily</a></li>
                                <li><a class="dropdown-item" href="#">Monthly</a></li>
                            </ul>
                        </div>
                        ${cardData.content}
                    `;
                } else {
                    const title = document.createElement('h5');
                    title.className = 'card-title';
                    title.textContent = cardData.type;

                    const content = document.createElement('div');
                    content.innerHTML = cardData.content;

                    cardDiv.appendChild(title);
                    cardDiv.appendChild(content);
                }

                colDiv.appendChild(cardDiv);
                row.appendChild(colDiv);
            });

            analyticsSection.appendChild(row);
        });

        // Reinitialize any necessary event listeners or functionality
        initializeCardFunctionality();
    }

    function initializeCardFunctionality() {
        // Reinitialize any charts or interactive elements
        // This might need to be customized based on your specific card types
    }

    // Function to save layout to database
    async function saveLayout() {
        const layout = captureLayout();
        console.log('Saving layout:', layout);

        try {
            const response = await fetch('/save_layout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(layout)
            });

            const data = await response.json();

            if (data.status === 'success') {
                console.log('Layout saved successfully!');
            } else {
                console.error('Error saving layout:', data.message);
            }
        } catch (error) {
            console.error('Error saving layout:', error);
        }
    }

    // Function to load saved layout
    async function loadSavedLayout() {
        try {
            const response = await fetch('/get_layout');
            const data = await response.json();

            if (data.status === 'success' && data.layout) {
                console.log('Loading layout:', data.layout);
                applyLayout(data.layout);
            }
        } catch (error) {
            console.error('Error loading layout:', error);
        }
    }

    // Add drag and drop functionality
    document.addEventListener('dragstart', (e) => {
        if (e.target.classList.contains('draggable')) {
            e.target.classList.add('dragging');
        }
    });

    document.addEventListener('dragend', (e) => {
        if (e.target.classList.contains('draggable')) {
            e.target.classList.remove('dragging');
        }
    });

    // Handle dropping template cards into rows
    function initializeRowDragHandlers() {
        document.querySelectorAll('.row').forEach(row => {
            row.addEventListener('dragover', (e) => {
                e.preventDefault();
                const draggable = document.querySelector('.dragging');
                if (!draggable) return;

                // Get the current row's cards
                const currentCards = row.querySelectorAll('.col').length;

                // Check if it's a template card or existing card
                if (draggable.classList.contains('template-item')) {
                    // Don't add if row is full
                    if (currentCards >= 4) {
                        return;
                    }
                    // Only create and add the new card on drop, not on dragover
                } else {
                    // For existing cards, check if moving would exceed limits
                    const sourceRow = draggable.closest('.row');
                    if (sourceRow !== row) {
                        // Moving between rows
                        if (currentCards >= 4 || sourceRow.querySelectorAll('.col').length <= 1) {
                            return;
                        }
                    }
                    const afterElement = getDragAfterElement(row, e.clientX);
                    if (afterElement) {
                        row.insertBefore(draggable, afterElement);
                    } else {
                        row.appendChild(draggable);
                    }
                }
            });

            // Add drop event listener
            row.addEventListener('drop', (e) => {
                e.preventDefault();
                const draggable = document.querySelector('.dragging');
                if (!draggable || !draggable.classList.contains('template-item')) return;

                const currentCards = row.querySelectorAll('.col').length;
                if (currentCards < 4) {
                    const newCard = createNewCard(draggable);
                    const afterElement = getDragAfterElement(row, e.clientX);
                    if (afterElement) {
                        row.insertBefore(newCard, afterElement);
                    } else {
                        row.appendChild(newCard);
                    }
                    setupDeleteIcons();
                }
            });
        });
    }

    function getDragAfterElement(container, x) {
        const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = x - box.left - box.width / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // Setup delete functionality for all cards
    function setupDeleteIcons() {
        document.querySelectorAll('.fa-square-minus').forEach(icon => {
            icon.addEventListener('click', () => {
                const card = icon.closest('.col');
                const row = card.closest('.row');
                if (row.querySelectorAll('.col').length > 1) {
                    card.remove();
                } else {
                    alert('Cannot delete the last card in a row');
                }
            });
        });
    }

    // Initialize delete functionality
    setupDeleteIcons();

    // Load saved layout when page loads
    loadSavedLayout();

    // Add drag functionality for template cards
    const templateCards = document.querySelectorAll('.template-item');
    templateCards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            card.classList.add('dragging');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });

    // Function to create new card from template
    function createNewCard(template) {
        const colDiv = document.createElement('div');
        colDiv.className = 'col draggable-item';
        colDiv.draggable = true;

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card p-3 shadow-sm h-100';

        // Copy the inner content from the template
        const title = template.querySelector('.card-title').cloneNode(true);
        const content = template.querySelector('.card-title').nextElementSibling.cloneNode(true);

        // Add delete icon
        const deleteIcon = document.createElement('i');
        deleteIcon.className = 'fa-regular fa-square-minus position-absolute top-0 end-0 p-2 fs-4';
        // Setup delete functionality for the new icon
        setupDeleteIcon(deleteIcon);

        cardDiv.appendChild(title);
        cardDiv.appendChild(content);
        cardDiv.appendChild(deleteIcon);
        colDiv.appendChild(cardDiv);

        // Add drag events to new card
        colDiv.addEventListener('dragstart', (e) => {
            colDiv.classList.add('dragging');
        });

        colDiv.addEventListener('dragend', () => {
            colDiv.classList.remove('dragging');
        });

        return colDiv;
    }

    // Function to setup delete icon
    function setupDeleteIcon(icon) {
        icon.addEventListener('click', (e) => {
            const card = icon.closest('.draggable-item');
            if (card) {
                const row = card.closest('.row');
                // Check if this is the last card in the row
                if (row.querySelectorAll('.draggable-item').length > 1) {
                    card.remove();
                } else {
                    e.preventDefault(); // Prevent the default action
                    e.stopPropagation(); // Stop event propagation
                    alert('Cannot delete the last card in a row');
                    return false;
                }
            }
        });
    }

    // Setup existing delete icons
    document.querySelectorAll('.fa-square-minus').forEach(setupDeleteIcon);
});