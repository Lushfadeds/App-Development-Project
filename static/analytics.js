document.addEventListener("DOMContentLoaded", () => {
    const openPopup = document.getElementById('openPopup');
    const closePopup = document.getElementById('closePopup');
    const popupOverlay = document.getElementById('popupOverlay');
    // Open the popup
    openPopup.addEventListener('click', () => {
        popupOverlay.classList.add('show');
    });
    // Close the popup
    closePopup.addEventListener('click', () => {
        popupOverlay.classList.remove('show');
    });
    // Close the popup when clicking outside the popup box
    popupOverlay.addEventListener('click', (e) => {
        if (e.target === popupOverlay) {
            popupOverlay.classList.remove('show');
        }
    });
})


