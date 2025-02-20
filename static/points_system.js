document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded ✅");

    // Get elements
    const collectButton = document.getElementById("collect-points");
    const spinButton = document.getElementById("spin-button");
    const spinResultDisplay = document.getElementById("spin-result");
    const userPointsDisplay = document.getElementById("user-points");
    const streakDisplay = document.getElementById("streak");
    const flashContainer = document.getElementById("flash-container");
    const wheel = document.getElementById("wheel");
    const dayElements = document.querySelectorAll(".day");

    const todayIndex = new Date().getDay(); // 0 = Sunday, 6 = Saturday
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const todayName = dayNames[todayIndex];

    // ✅ Function to show flash messages
    function showFlashMessage(message, type) {
        let flashMessage = document.createElement("div");
        flashMessage.className = `flash-message ${type}`;
        flashMessage.textContent = message;
        flashContainer.appendChild(flashMessage);

        setTimeout(() => {
            flashMessage.classList.add("show");
        }, 100);

        setTimeout(() => {
            flashMessage.style.opacity = "0";
            setTimeout(() => {
                flashMessage.remove();
            }, 500);
        }, 5000);
    }
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

                // ✅ Ensure today's tick is updated correctly
                if (day === todayName && streakData[todayName]) {
                    console.log(`✅ Today (${todayName}) has been collected.`);
                    circle.classList.add("collected");
                    circle.style.backgroundColor = "#4CAF50"; // Green
                    circle.textContent = "✔";
                }
            });

            // ✅ Disable the spin button if the user already spun today
            if (data.spunToday) {
                console.log("⚠️ User already spun the wheel today.");
                spinButton.disabled = true;
                spinResultDisplay.textContent = "You have already spun today!";
            } else {
                spinButton.disabled = false;
            }
        })
        .catch(error => console.error('Error fetching user data:', error));
}

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

        // ✅ Instantly mark today as collected
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

        // ✅ Update streak data so refresh isn't needed
        fetchUserData(); // Fetch latest data again to persist UI state
    })
    .catch(err => console.error("Error collecting points:", err));
});


  function spinWheel() {
    console.log("Spin Button Clicked ✅");

    // Disable button while spinning
    spinButton.disabled = true;
    spinResultDisplay.textContent = "Spinning... 🎡";

    fetch('/spin', {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            spinResultDisplay.textContent = data.error;
            spinButton.disabled = false;
            return;
        }

        console.log("✅ Spin Result:", data.result);

        // ✅ Ensure correct mapping (Match these values with your backend)
        const angles = {
            0: 0,   // 0 points
            2: 72,  // 2 points
            3: 144, // 3 points
            5: 216, // 5 points
            10: 288 // 10 points
        };

        let finalAngle = angles[data.result] || 0; // Default to 0 if not found
        let extraSpins = 5 * 360; // Full rotations before stopping
        let totalRotation = extraSpins + finalAngle;

        // ✅ Animate the wheel
        wheel.style.transition = "transform 3s ease-out";
        wheel.style.transform = `rotate(${totalRotation}deg)`;

        // ✅ Keep track of the last rotation to prevent reset
        localStorage.setItem("wheelLastRotation", totalRotation);

        // ✅ Update result after animation ends
        setTimeout(() => {
            spinResultDisplay.textContent = `🎉 You won ${data.result} points!`;
            userPointsDisplay.textContent = `Points: ${data.points}`;
        }, 3100); // Slightly longer than animation
    })
    .catch(err => {
        console.error("Error spinning the wheel:", err);
        spinButton.disabled = false;
    });
}

// ✅ Keep the wheel in the last position when revisiting the page
document.addEventListener("DOMContentLoaded", function () {
    let lastRotation = localStorage.getItem("wheelLastRotation");
    if (lastRotation) {
        wheel.style.transform = `rotate(${lastRotation}deg)`;
    }
});





    // Attach event listener for spin
    spinButton.addEventListener("click", spinWheel);

    // ✅ Load user data on page load (ONLY ONCE)
    fetchUserData();
});
