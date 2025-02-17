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
    dataEdit.classList.toggle('d-none');
}

document.addEventListener('DOMContentLoaded', function() {
    const icons = document.querySelectorAll('.fa-regular.fa-square-minus');

    icons.forEach(icon => {
        icon.addEventListener('click', function() {
            const parentDiv = icon.closest('.col');
            parentDiv.classList.toggle('d-none');
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
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

            // Remove draggable attributes and classes
            document.querySelectorAll('.draggable-item').forEach(item => {
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
        // Only capture the main content section
        const mainContent = document.querySelector('.mainContent');
        const rows = mainContent.querySelectorAll('.row');
        const layout = [];

            rows.forEach(row => {
                const rowCards = [];
                row.querySelectorAll('.col').forEach(card => {
                const title = card.querySelector('h5');
                const numericContent = card.querySelector('.fw-bold.fs-1');
                const graphContent = card.querySelector('.graph-container');

                    if (title) {
                        const cardData = {
                            type: title.textContent.trim(),
                    };

                        // Include numeric content if it exists
                        if (numericContent) {
                            cardData.content = numericContent.innerHTML.trim();
                    }

                        // Include graph content if it exists
                        if (graphContent) {
                            cardData.graph = graphContent.innerHTML.trim();
                    }

                        // Only add the card if it has either numeric or graph content
                        if (numericContent || graphContent) {
                            rowCards.push(cardData);
                    }
                }
            });

                if (rowCards.length > 0) {
                    layout.push(rowCards);
                }
        });

        console.log(layout);
        return layout;
    }


    // Function to apply loaded layout
    function applyLayout(layout) {
        return
        console.log(layout);

        // Find the main content section
        const analyticsSection = document.querySelector('.mainContent');
        if (!analyticsSection) return;

        // Clear existing content
        analyticsSection.innerHTML = '';

        // Create rows and add cards
        layout.forEach(rowCards => {
            const row = document.createElement('div');
            row.className = 'row g-3 mt-3';

            rowCards.forEach(cardData => {
                const colDiv = document.createElement('div');
                colDiv.className = 'col';

                const cardDiv = document.createElement('div');
                cardDiv.className = 'card p-3 shadow-sm';

                const title = document.createElement('h5');
                title.className = 'card-title';
                title.textContent = cardData.type;

                // Create content section if it exists
                const content = document.createElement('div');
                if (cardData.content) {
                    content.classList.add('ctmText')
                    content.innerHTML = cardData.content;
                }

                // Create graph container if it exists
                const graphContainer = document.createElement('div');
                if (cardData.graph) {
                    graphContainer.classList.add('graph-container'); // Add the graph-container class
                    graphContainer.innerHTML = cardData.graph; // Set the graph content (this could be Plotly HTML)
                }

                // Append the title, content, and graph to the card
                cardDiv.appendChild(title);
                if (content) cardDiv.appendChild(content);
                if (graphContainer) cardDiv.appendChild(graphContainer);

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

                // Check if the card already exists in the row
                const existingCards = row.querySelectorAll('.col');
                const cardTitle = draggable.querySelector('.card-title').textContent;

                const cardExists = Array.from(existingCards).some(card => {
                    return card.querySelector('.card-title').textContent === cardTitle;
                });

                if (cardExists) {
                    console.warn(`${cardTitle} already exists in this row.`);
                    return; // Prevent adding the same card again
                }

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

                    // Call saveLayout after adding a new card
                    saveLayout();
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
        colDiv.className = 'col draggable-item width-custom';
        colDiv.draggable = false;

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card p-3 shadow-sm h-100';

        // Safely get the title and content
        const titleElement = template.querySelector('.card-title');
        let contentElement;

        // Check if the title element exists
        if (titleElement) {
            const title = titleElement.cloneNode(true);
            cardDiv.appendChild(title);

            // Try to find the content element in various ways
            contentElement = titleElement.nextElementSibling || titleElement.parentElement.querySelector('.graph-container');
        }

        if (contentElement) {
            const content = contentElement.cloneNode(true);
            cardDiv.appendChild(content);
        } else {
            console.error('Content element not found in the template');
        }

        // Add delete icon
        const deleteIcon = document.createElement('i');
        deleteIcon.className = 'fa-regular fa-square-minus position-absolute top-0 end-0 p-2 fs-4';
        // Setup delete functionality for the new icon
        setupDeleteIcon(deleteIcon);

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