document.addEventListener("DOMContentLoaded", () => {
    const collectButton = document.getElementById("collect-points");
    const days = document.querySelectorAll(".day");
    const today = new Date().getDay();
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    // Fetch streak data and total points from the backend
    fetch('/get_user_data')
        .then(response => response.json())
        .then(data => {
            const streakData = data.streakData || {};
            let totalPoints = data.totalPoints || 0;

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
                    // Mark the current day as completed
                    streakData[currentDay] = true;

                    // Update the total points
                    totalPoints += 2;

                    // Send updated data to the backend
                    fetch('/update_user_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            streakData: streakData,
                            totalPoints: totalPoints,
                            lastSpinDate: data.lastSpinDate // Keep the last spin date intact
                        })
                    }).then(response => response.json())
                      .then(() => {
                          // Update UI with the new streak and points
                          const currentCircle = document.querySelector(`.day[data-day="${currentDay}"] .circle`);
                          currentCircle.classList.add("completed");
                          currentCircle.textContent = "✔";

                          const pointsDisplay = document.getElementById("user-points");
                          pointsDisplay.textContent = `Points: ${totalPoints}`;

                          alert("You collected 2 points for today!");
                      }).catch(err => {
                          console.error("Error updating data: ", err);
                          alert("Something went wrong while updating your points.");
                      });
                } else {
                    alert("You already collected points for today!");
                }
            });

            // Display the points on page load
            const pointsDisplay = document.getElementById("user-points");
            pointsDisplay.textContent = `Points: ${totalPoints}`;
        }).catch(err => {
            console.error("Error fetching user data: ", err);
            alert("Something went wrong while fetching your data.");
        });

    // Spin the Wheel functionality
    const spinButton = document.getElementById("spin-button");
    const wheel = document.getElementById("wheel");
    const spinResult = document.getElementById("spin-result");
    let isSpinning = false;

    // Fetch the last spin date to decide if the button should be disabled
    fetch('/get_user_data')
        .then(response => response.json())
        .then(data => {
            const lastSpinDate = data.lastSpinDate;
            const todayDate = new Date().toDateString();

            if (lastSpinDate === todayDate) {
                spinButton.disabled = true;
                spinButton.style.backgroundColor = "#cccccc";
                spinResult.textContent = "You've already spun the wheel today!";
            } else {
                spinButton.disabled = false;
                spinButton.style.backgroundColor = "#8c5a3f";
            }
        }).catch(err => {
            console.error("Error fetching spin data: ", err);
            alert("Something went wrong while checking your spin status.");
        });

    spinButton.addEventListener("click", () => {
        if (isSpinning) return;
        isSpinning = true;
        spinResult.textContent = "Spin Result: ";

        const spinAngle = Math.floor(3600 + Math.random() * 360);
        wheel.style.transform = `rotate(${spinAngle}deg)`;

        setTimeout(() => {
            const normalizedAngle = spinAngle % 360;
            const correctedAngle = (360 - normalizedAngle + 90) % 360;
            const segmentIndex = Math.floor(correctedAngle / 72);
            const outcomes = [2, 3, 5, 10, 0];
            const result = outcomes[segmentIndex];

            spinResult.textContent = `Spin Result: You won ${result} points!`;

            // Update points and save to backend
            fetch('/get_user_data')
                .then(response => response.json())
                .then(data => {
                    let totalPoints = data.totalPoints + result;

                    fetch('/update_user_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            streakData: data.streakData,
                            totalPoints: totalPoints,
                            lastSpinDate: new Date().toDateString()  // Update the last spin date
                        })
                    }).then(() => {
                        const pointsDisplay = document.getElementById("user-points");
                        pointsDisplay.textContent = `Points: ${totalPoints}`;

                        spinButton.disabled = true;
                        spinButton.style.backgroundColor = "#cccccc";
                    }).catch(err => {
                        console.error("Error updating spin result: ", err);
                        alert("Something went wrong while updating your spin result.");
                    });
                }).catch(err => {
                    console.error("Error fetching user data for spin: ", err);
                    alert("Something went wrong while fetching your data for the spin.");
                });
        }, 4000);
    });
});
