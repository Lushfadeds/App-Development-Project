document.addEventListener("DOMContentLoaded", () => {
    const collectButton = document.getElementById("collect-points");
    const days = document.querySelectorAll(".day");
    const today = new Date().getDay(); // Sunday = 0, Monday = 1, ..., Saturday = 6
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Load streak data from localStorage
    const streakData = JSON.parse(localStorage.getItem("streakData")) || {};

    // Update the UI based on streak data
    days.forEach((day, index) => {
        const dayName = day.dataset.day;
        const circle = day.querySelector(".circle");
        if (streakData[dayName]) {
            circle.classList.add("completed");
            circle.textContent = "✔";
        }
        if (index === today - 1 || (today === 0 && index === 6)) {
            day.classList.add("current");
        }
    });

    // Button click event to collect points
    collectButton.addEventListener("click", () => {
        const currentDay = dayNames[today];
        if (!streakData[currentDay]) {
            streakData[currentDay] = true;
            localStorage.setItem("streakData", JSON.stringify(streakData));
            const currentCircle = document.querySelector(`.day[data-day="${currentDay}"] .circle`);
            currentCircle.classList.add("completed");
            currentCircle.textContent = "✔";
            alert("You collected 2 points for today!");
        } else {
            alert("You already collected points for today!");
        }
    });
});
