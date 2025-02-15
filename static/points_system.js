document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded ✅");

    const collectButton = document.getElementById("collect-points");
    const userPointsDisplay = document.getElementById("user-points");

    if (!collectButton || !userPointsDisplay) {
        console.error("Missing essential elements! ❌");
        return;
    }

    const dayElements = document.querySelectorAll(".day");
    const todayIndex = new Date().getDay(); // 0 = Sunday, 6 = Saturday
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const todayName = dayNames[todayIndex];

    // ** Fetch user streak data on page load ✅**
    fetch('/get_user_data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // ✅ Update Points & Streak Count
            userPointsDisplay.textContent = `Points: ${data.points}`;
            document.getElementById("streak").textContent = data.streak;

            let streakData = data.streakData;

            // ✅ Check each day and apply checkmark if collected
            dayElements.forEach(dayElement => {
                let day = dayElement.getAttribute("data-day");
                let circle = dayElement.querySelector(".circle");

                if (streakData[day]) {
                    // ✅ Keep previously collected days ticked
                    circle.classList.add("collected");
                    circle.style.backgroundColor = "#4CAF50"; // Green
                    circle.textContent = "✔";
                }

                // ✅ Ensure today is visible (either green if collected, or orange if not)
                if (day === todayName) {
                    if (streakData[day]) {
                        circle.classList.add("collected");
                        circle.style.backgroundColor = "#4CAF50";
                        circle.textContent = "✔";
                    } else {
                        circle.classList.add("today");
                        circle.style.backgroundColor = "orange";
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching user data:', error));

    // ** Collect Points Button Click Event ✅**
    collectButton.addEventListener("click", function () {
        console.log("Collect Points Button Clicked ✅");
        fetch('/collect_points', { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // ✅ Update points immediately
                userPointsDisplay.textContent = `Points: ${data.points}`;
                alert(`You collected ${data.message}!`);

                // ✅ Ensure today is ticked and marked ✅
                let todayElement = document.querySelector(`.day[data-day="${todayName}"] .circle`);
                todayElement.classList.add("collected");
                todayElement.style.backgroundColor = "#4CAF50"; // Green
                todayElement.textContent = "✔";

                // ✅ Update Streak Count
                document.getElementById("streak").textContent = data.streak;
            })
            .catch(err => console.error("Error collecting points:", err));
    });
});
