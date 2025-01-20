document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('overlay');
    const openOverlay = document.getElementById('edit-btn');
    const closeOverlay = document.getElementById('close-btn');

    openOverlay.addEventListener('click', () => {
        overlay.style.display =  'flex';
    });

    closeOverlay.addEventListener('click', () => {
        overlay.style.display = 'none';
    });
});