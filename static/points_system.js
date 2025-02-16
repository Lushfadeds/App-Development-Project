document.addEventListener("DOMContentLoaded", function () {
        fetch("/get_user_data")
            .then(response => response.json())
            .then(data => {
                if (data.newUser) {
                    alert("🎉 Welcome to the platform! You've received 500 bonus points! 🎊");
                }
                document.getElementById("points").textContent = data.points;
                document.getElementById("streak").textContent = data.streak;
            })
            .catch(error => console.error("Error fetching user data:", error));
    });


document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded ✅");

    // Get the elements
    const collectButton = document.getElementById("collect-points");
    const spinButton = document.getElementById("spin-button");
    const spinResultDisplay = document.getElementById("spin-result");
    const userPointsDisplay = document.getElementById("user-points");
    const streakDisplay = document.getElementById("streak");
    const dayElements = document.querySelectorAll(".day");

    const todayIndex = new Date().getDay(); // 0 = Sunday, 6 = Saturday
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const todayName = dayNames[todayIndex];

    // Debugging: Check which elements are missing
    if (!collectButton) console.error("❌ Missing: #collect-points (button)");
    if (!spinButton) console.error("❌ Missing: #spin-button (button)");
    if (!userPointsDisplay) console.error("❌ Missing: #user-points (points display)");
    if (!streakDisplay) console.error("❌ Missing: #streak (streak display)");
    if (!spinResultDisplay) console.error("❌ Missing: #spin-result (spin display)");

    // Stop execution if any essential elements are missing
    if (!collectButton || !spinButton || !userPointsDisplay || !streakDisplay || !spinResultDisplay) {
        console.error("Missing essential elements! ❌ JavaScript stopped.");
        return;
    }

    console.log("✅ All essential elements found!");

    // ✅ Function to fetch and update user streak & spin data
    function fetchUserData() {
        fetch('/get_user_data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                console.log("✅ Streak Data Received:", data.streakData);

                userPointsDisplay.textContent = `Points: ${data.points}`;
                streakDisplay.textContent = `Streak: ${data.streak}`;

                let streakData = data.streakData;

                // ✅ Ensure collected days are ticked
                dayElements.forEach(dayElement => {
                    let day = dayElement.getAttribute("data-day");
                    let circle = dayElement.querySelector(".circle");

                    // Reset previous styles
                    circle.classList.remove("collected", "today");
                    circle.style.backgroundColor = "";
                    circle.textContent = "";

                    if (streakData[day]) {
                        console.log(`✅ Marking ${day} as collected.`); // Debugging
                        circle.classList.add("collected");
                        circle.style.backgroundColor = "#4CAF50"; // Green
                        circle.textContent = "✔";
                    }

                    // Ensure today's circle is highlighted in orange if not collected yet
                    if (day === todayName) {
    if (streakData[todayName]) {
        console.log(`✅ Today (${todayName}) has been collected.`);
        circle.classList.add("collected");
        circle.style.backgroundColor = "#4CAF50"; // Green
        circle.textContent = "✔";
    } else {
        console.log(`🔲 Today (${todayName}) is uncollected but remains blank.`);
        circle.classList.remove("collected", "today"); // Ensure it's blank
        circle.style.backgroundColor = ""; // No color
        circle.textContent = ""; // No text
    }
}

                });

                // ✅ Disable the spin button if the user already spun today
                if (data.spunToday) {
                    console.log("⚠️ User already spun the wheel today.");
                    spinButton.disabled = true;
                    spinResultDisplay.textContent = "You have already spun today!";
                } else {
                    spinButton.disabled = false; // Ensure it's enabled for the next day
                }
            })
            .catch(error => console.error('Error fetching user data:', error));
    }

    // Load user data on page load
    fetchUserData();

    // ✅ Button click event to collect points
    collectButton.addEventListener("click", function () {
        console.log("Collect Points Button Clicked ✅");

        fetch('/collect_points', {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            console.log("✅ Points Collected:", data.points);

            // Update UI
            userPointsDisplay.textContent = `Points: ${data.points}`;
            streakDisplay.textContent = `Streak: ${data.streak}`;
            alert(`You collected ${data.message}!`);

            // ✅ Mark today as collected
            let todayElement = document.querySelector(`.day[data-day="${todayName}"] .circle`);
            todayElement.classList.add("collected");
            todayElement.style.backgroundColor = "#4CAF50"; // Green
            todayElement.textContent = "✔";

            // Refresh streak data
            fetchUserData();
        })
        .catch(err => console.error("Error collecting points:", err));
    });

    // ✅ Function to spin the wheel
    function spinWheel() {
        console.log("Spin Button Clicked ✅");

        fetch('/spin', {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            console.log("✅ Spin Result:", data.result);
            spinResultDisplay.textContent = `You won ${data.result} points!`;
            userPointsDisplay.textContent = `Points: ${data.points}`;

            // ✅ Disable button after spinning
            spinButton.disabled = true;
        })
        .catch(err => console.error("Error spinning the wheel:", err));
    }

    // ✅ Add event listener for the spin button
    spinButton.addEventListener("click", spinWheel);
});
