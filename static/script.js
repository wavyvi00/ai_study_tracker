// Session Management Functions
function getCourseInput() {
    const courseInput = document.getElementById('course-input');
    return courseInput ? courseInput.value.trim() : '';
}

function clearCourseInput() {
    const courseInput = document.getElementById('course-input');
    if (courseInput) {
        courseInput.value = '';
    }
}

function startNormalMode() {
    const course = getCourseInput();

    // Validate course is not empty
    if (!course || course.trim() === '') {
        alert('⚠️ Please enter a course name before starting a session!');
        document.getElementById('course-input').focus();
        return;
    }

    fetch('/api/session/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mode: 'normal',
            course: course
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Normal mode started', data.course ? `for course: ${data.course}` : '');
                clearCourseInput();
            }
        })
        .catch(error => console.error('Error starting normal mode:', error));
}

function startChallengeMode(minutes) {
    const duration = minutes * 60; // Convert to seconds
    const course = getCourseInput();

    // Validate course is not empty
    if (!course || course.trim() === '') {
        alert('⚠️ Please enter a course name before starting a session!');
        document.getElementById('course-input').focus();
        return;
    }

    fetch('/api/session/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mode: 'challenge',
            duration: duration,
            course: course
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`Challenge mode started: ${minutes} minutes`, data.course ? `for course: ${data.course}` : '');
                clearCourseInput();
            }
        })
        .catch(error => console.error('Error starting challenge mode:', error));
}

function stopSession() {
    fetch('/api/session/stop', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Session stopped');
            }
        })
        .catch(error => console.error('Error stopping session:', error));
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

let sessionWasActive = false;
let lastSessionComplete = false;

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Toggle between mode selection and session view
            const modeSelection = document.getElementById('mode-selection');
            const sessionView = document.getElementById('session-view');

            if (data.session_active) {
                modeSelection.style.display = 'none';
                sessionView.style.display = 'block';
                sessionWasActive = true;
            } else {
                modeSelection.style.display = 'block';
                sessionView.style.display = 'none';

                // Show completion message if session just ended
                if (sessionWasActive && !lastSessionComplete) {
                    // Session was just stopped
                    sessionWasActive = false;
                }
            }

            // Update mode indicator
            const modeIndicator = document.getElementById('mode-indicator');
            if (data.session_mode === 'normal') {
                modeIndicator.textContent = 'Normal Mode';
            } else if (data.session_mode === 'challenge') {
                modeIndicator.textContent = 'Challenge Mode';
            }

            // Update challenge timer if in challenge mode
            const challengeTimerCard = document.getElementById('challenge-timer-card');
            const challengeTimer = document.getElementById('challenge-timer');

            if (data.session_active && data.session_mode === 'challenge') {
                challengeTimerCard.style.display = 'block';
                challengeTimer.textContent = formatTime(data.time_remaining);

                // Check if session just completed
                if (data.time_remaining === 0 && !lastSessionComplete) {
                    lastSessionComplete = true;
                    showCompletionMessage();
                }
            } else {
                challengeTimerCard.style.display = 'none';
                lastSessionComplete = false;
            }

            // Update course display
            const courseDisplay = document.getElementById('course-display');
            const courseName = document.getElementById('course-name');
            if (data.session_active && data.current_course) {
                courseDisplay.style.display = 'block';
                courseName.textContent = data.current_course;
            } else {
                courseDisplay.style.display = 'none';
            }

            // Store courses globally for autocomplete
            window.availableCourses = data.courses || [];

            // Update Dashboard Stats (mode selection screen)
            if (!data.session_active) {
                // Level
                const dashboardLevel = document.getElementById('dashboard-level');
                if (dashboardLevel) {
                    dashboardLevel.textContent = data.level;
                }

                // XP Progress
                const xpForNextLevel = data.level * 100;
                const xpInCurrentLevel = data.xp % 100;
                const xpProgress = (xpInCurrentLevel / 100) * 100;

                const dashboardXpCurrent = document.getElementById('dashboard-xp-current');
                const dashboardXpNext = document.getElementById('dashboard-xp-next');
                const dashboardXpFill = document.getElementById('dashboard-xp-fill');

                if (dashboardXpCurrent) dashboardXpCurrent.textContent = xpInCurrentLevel;
                if (dashboardXpNext) dashboardXpNext.textContent = 100;
                if (dashboardXpFill) dashboardXpFill.style.width = `${xpProgress}%`;

                // Health
                const dashboardHealth = document.getElementById('dashboard-health');
                if (dashboardHealth) {
                    dashboardHealth.textContent = `${Math.round(data.health)}%`;
                }

                // Total Time
                const dashboardTotalTime = document.getElementById('dashboard-total-time');
                if (dashboardTotalTime) {
                    dashboardTotalTime.textContent = data.time_formatted;
                }

                // Sessions
                const dashboardSessions = document.getElementById('dashboard-sessions');
                if (dashboardSessions) {
                    dashboardSessions.textContent = data.total_sessions || 0;
                }
            }

            // Update Timers
            if (data.session_active) {
                // During session: show session time
                document.getElementById('session-timer').textContent = data.session_time_formatted;
            }

            // Mode selection: show total time
            const totalTimeDisplay = document.getElementById('total-time-display');
            if (totalTimeDisplay) {
                totalTimeDisplay.textContent = data.time_formatted;
            }

            // Update Status Badge
            const badge = document.getElementById('status-badge');
            if (data.session_active) {
                if (data.is_studying) {
                    badge.textContent = "Studying 🧠";
                    badge.className = "status-badge studying";
                } else {
                    badge.textContent = "Distracted ⚠️";
                    badge.className = "status-badge distracted";
                }
            } else {
                badge.textContent = "No Active Session";
                badge.className = "status-badge";
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

function showCompletionMessage() {
    // Simple alert for now - could be enhanced with a custom modal
    setTimeout(() => {
        alert('🎉 Challenge Complete! Great work!');
        lastSessionComplete = false;
    }, 100);
}

// Update every second
setInterval(updateStatus, 1000);

// Initial call
updateStatus();

// Custom Autocomplete for Courses
window.availableCourses = [];

function setupCourseAutocomplete() {
    const input = document.getElementById('course-input');
    const dropdown = document.getElementById('course-dropdown');

    if (!input || !dropdown) return;

    // Show dropdown on input
    input.addEventListener('input', function () {
        const value = this.value.toLowerCase().trim();

        if (value === '') {
            dropdown.style.display = 'none';
            return;
        }

        // Filter courses
        const filtered = window.availableCourses.filter(course =>
            course.toLowerCase().includes(value)
        );

        // Render dropdown
        if (filtered.length > 0) {
            dropdown.innerHTML = '';
            filtered.forEach(course => {
                const item = document.createElement('div');
                item.className = 'course-dropdown-item';
                item.textContent = course;
                item.onclick = function () {
                    input.value = course;
                    dropdown.style.display = 'none';
                };
                dropdown.appendChild(item);
            });
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    });

    // Show all courses on focus if input is empty
    input.addEventListener('focus', function () {
        if (this.value.trim() === '' && window.availableCourses.length > 0) {
            dropdown.innerHTML = '';
            window.availableCourses.forEach(course => {
                const item = document.createElement('div');
                item.className = 'course-dropdown-item';
                item.textContent = course;
                item.onclick = function () {
                    input.value = course;
                    dropdown.style.display = 'none';
                };
                dropdown.appendChild(item);
            });
            dropdown.style.display = 'block';
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });

    // Handle Enter key to select first item
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && dropdown.style.display === 'block') {
            const firstItem = dropdown.querySelector('.course-dropdown-item');
            if (firstItem) {
                input.value = firstItem.textContent;
                dropdown.style.display = 'none';
                e.preventDefault();
            }
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
}

// Initialize autocomplete when page loads
setupCourseAutocomplete();
