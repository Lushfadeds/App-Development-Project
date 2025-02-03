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