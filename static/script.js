function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Update Timer
            document.getElementById('timer').textContent = data.time_formatted;

            // Update Status Badge
            const badge = document.getElementById('status-badge');
            if (data.is_studying) {
                badge.textContent = "Studying 🧠";
                badge.className = "status-badge studying";
            } else {
                badge.textContent = "Distracted ⚠️";
                badge.className = "status-badge distracted";
            }

            // Update Health
            const health = Math.round(data.health);
            document.getElementById('health-text').textContent = `${health}%`;
            const healthBar = document.getElementById('health-bar');
            healthBar.style.width = `${health}%`;

            if (health > 50) {
                healthBar.style.backgroundColor = "var(--accent-green)";
            } else if (health > 20) {
                healthBar.style.backgroundColor = "var(--accent-orange)";
            } else {
                healthBar.style.backgroundColor = "var(--accent-red)";
            }

            // Update XP & Level
            document.getElementById('xp-value').textContent = `${data.xp} XP`;
            document.getElementById('level-value').textContent = data.level;

            // Update App Info
            document.getElementById('app-name').textContent = data.app_name;
            document.getElementById('window-title').textContent = data.window_title || "...";

            // Permission Warning
            const warning = document.getElementById('permission-warning');
            if (data.has_permissions === false) {
                warning.style.display = 'block';
            } else {
                warning.style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching status:', error));
}

// Update every second
setInterval(updateStatus, 1000);

// Initial call
updateStatus();
