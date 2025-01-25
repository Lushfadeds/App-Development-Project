document.addEventListener("DOMContentLoaded", () => {
    // Streak functionality (unchanged)

    const collectButton = document.getElementById("collect-points");
    const days = document.querySelectorAll(".day");
    const today = new Date().getDay(); // Sunday = 0, Monday = 1, ..., Saturday = 6
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Load streak data and total points from localStorage
    const streakData = JSON.parse(localStorage.getItem("streakData")) || {};
    let totalPoints = parseInt(localStorage.getItem("totalPoints")) || 0;  // Load total points, default to 0 if none

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
            // Mark the current day as completed in the streak data
            streakData[currentDay] = true;
            localStorage.setItem("streakData", JSON.stringify(streakData));

            // Update the total points
            totalPoints += 2; // Add 2 points for today
            localStorage.setItem("totalPoints", totalPoints); // Save updated total points to localStorage

            // Update the UI to reflect the streak completion
            const currentCircle = document.querySelector(`.day[data-day="${currentDay}"] .circle`);
            currentCircle.classList.add("completed");
            currentCircle.textContent = "✔";

            // Display total points in the UI
            const pointsDisplay = document.getElementById("user-points");
            pointsDisplay.textContent = `Points: ${totalPoints}`;  // Update points displayed

            alert("You collected 2 points for today!");
        } else {
            alert("You already collected points for today!");
        }
    });

    // Display the points on page load (in case it's set in localStorage)
    const pointsDisplay = document.getElementById("user-points");
    pointsDisplay.textContent = `Points: ${totalPoints}`;



 // Spin the Wheel functionality

    const spinButton = document.getElementById("spin-button");
    const wheel = document.getElementById("wheel");
    const spinResult = document.getElementById("spin-result");
    let isSpinning = false;

    // Define outcomes for the wheel (values in points)
    const outcomes = [2, 3, 5, 10, 0]; // Example points
    const segmentSize = 72; // Segment size in degrees

    // Check if the wheel has been spun today
    const lastSpinDate = localStorage.getItem('lastSpinDate');
    const todayDate = new Date().toDateString();

    if (lastSpinDate === todayDate) {
        // Disable the spin button if the wheel has been spun today
        spinButton.disabled = true;
        spinButton.style.backgroundColor = "#cccccc"; // Change button color to indicate disabled state
        spinResult.textContent = "You've already spun the wheel today!"; // Show message
    } else {
        // Enable the spin button if not spun today
        spinButton.disabled = false;
        spinButton.style.backgroundColor = "#8c5a3f"; // Set button color to indicate enabled state
    }

    // Handle the click event for the spin button
    spinButton.addEventListener("click", () => {
        if (isSpinning) return; // Prevent multiple spins at the same time
        isSpinning = true;
        spinResult.textContent = "Spin Result: "; // Clear previous result

        // Randomly determine the spin angle
        const spinAngle = Math.floor(3600 + Math.random() * 360); // At least 10 full rotations
        wheel.style.transform = `rotate(${spinAngle}deg)`;

        // Calculate the result based on the normalized angle
        setTimeout(() => {
            const normalizedAngle = spinAngle % 360; // Get the final position angle
            const correctedAngle = (360 - normalizedAngle + 90) % 360; // Adjust for arrow position
            const segmentIndex = Math.floor(correctedAngle / segmentSize) // Determine the segment

            const result = outcomes[segmentIndex]; // Result based on angle
            spinResult.textContent = `Spin Result: You won ${result} points!`;

            // Update total points with the result of the spin
            let totalPoints = parseInt(localStorage.getItem("totalPoints")) || 0;
            totalPoints += result; // Add result points
            localStorage.setItem("totalPoints", totalPoints); // Save updated total points

            // Update the UI with the total points after spin
            const pointsDisplay = document.getElementById("user-points");
            pointsDisplay.textContent = `Points: ${totalPoints}`;

            // Store the current date as the last spin date in localStorage
            localStorage.setItem('lastSpinDate', todayDate);

            // Prevent multiple spins by disabling the button
            spinButton.disabled = true;
            spinButton.style.backgroundColor = "#cccccc"; // Change button color to indicate disabled state


            setTimeout(() => {
                // Optionally re-enable the button after a day or based on your use case
            }, 3000); // Re-enable after 3 seconds

            isSpinning = false;
        }, 4000); // Match the CSS transition duration
    });
});





