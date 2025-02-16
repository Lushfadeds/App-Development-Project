document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_user_data")
        .then(response => response.json())
        .then(data => {
            if (data.newUser) {
                showFlashMessage("🎉 Welcome to the platform! You've received 500 bonus points! 🎊");
            }
            document.getElementById("points").textContent = data.points;
            document.getElementById("streak").textContent = data.streak;
        })
        .catch(error => console.error("Error fetching user data:", error));
    });


function showFlashMessage(message, type){
    let flashContainer = document.getElementById("flash-container");

    // Create message div
    let flashMessage = document.createElement("div");
    flashMessage.className = `flash-message ${type}`;
    flashMessage.textContent = message;

    // Append to container
    flashContainer.appendChild(flashMessage);

    // Show message with animation
    setTimeout(() => {
        flashMessage.classList.add("show");
    }, 100);

    // Auto-remove message after 5 seconds
    setTimeout(() => {
        flashMessage.style.opacity = "0";
        setTimeout(() => {
            flashMessage.remove();
        }, 500);
    }, 5000);
}


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
    // ✅ Button click event to collect points
collectButton.addEventListener("click", function () {
    fetch('/collect_points', { method: "POST", headers: { "Content-Type": "application/json" } })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showFlashMessage(data.error, "error");
            return;
        }

        // ✅ Show flash message for points collected
        showFlashMessage(`🎉 You collected ${data.message}!`, "success");

        // ✅ Update UI immediately
        userPointsDisplay.textContent = `Points: ${data.points}`;
        streakDisplay.textContent = `Streak: ${data.streak}`;

        // ✅ Update streak tracker UI
        let todayName = new Date().toLocaleDateString('en-US', { weekday: 'long' });
        let todayElement = document.querySelector(`.day[data-day="${todayName}"] .circle`);

        if (todayElement) {
            todayElement.classList.add("collected");
            todayElement.style.backgroundColor = "#4CAF50"; // Green
            todayElement.textContent = "✔";
            console.log(`✅ Updated UI: Marked ${todayName} as collected.`);
        } else {
            console.warn(`⚠️ Unable to find streak circle for ${todayName}`);
        }
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
