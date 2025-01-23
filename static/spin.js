document.addEventListener("DOMContentLoaded", () => {
    const spinButton = document.getElementById("spin-button");
    const wheel = document.getElementById("wheel");
    const spinResult = document.getElementById("spin-result");
    let isSpinning = false;

    spinButton.addEventListener("click", () => {
        if (isSpinning) return; // Prevent multiple spins at the same time
        isSpinning = true;
        spinResult.textContent = ""; // Clear previous result

        // Randomly determine the spin angle
        const spinAngle = Math.floor(3600 + Math.random() * 360); // At least 10 full rotations
        const normalizedAngle = spinAngle % 360; // Get the final position angle
        const segmentSize = 72; // Each segment covers 72 degrees
        const outcomes = [2, 3, 5, 10, 0]; // Values on the wheel

        // Rotate the wheel
        wheel.style.transform = `rotate(${spinAngle}deg)`;

        // Calculate the result based on the normalized angle
        setTimeout(() => {
            // Determine the segment based on the normalized angle
            const segmentIndex = Math.floor((360 - normalizedAngle + segmentSize / 2) % 360 / segmentSize) % outcomes.length;
            const result = outcomes[segmentIndex];

            // Display the result
            fetch("/spin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            })
                .then(response => response.json())
                .then(data => {
                    spinResult.textContent = `You won ${result} points! Total points: ${data.points}`;
                })
                .catch(err => console.error("Error updating points:", err));

            isSpinning = false;
        }, 4000); // Match the CSS transition duration
    });
});
