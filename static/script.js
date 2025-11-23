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
            if (data.success && data.results) {
                showResults(data.results);
            }
        })
        .catch(error => console.error('Error stopping session:', error));
}

function showResults(results) {
    // Check if health failed
    if (results.health_failed) {
        showHealthFailed(results);
        return;
    }

    // Check if challenge failed
    if (results.challenge_failed) {
        showChallengeFailed(results);
        return;
    }

    // Populate results data
    document.getElementById('results-course-name').textContent = results.course || 'Study Session';

    // Format duration
    const minutes = Math.floor(results.duration_seconds / 60);
    const seconds = results.duration_seconds % 60;
    document.getElementById('results-duration').textContent =
        minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

    // Show results overlay first
    document.getElementById('session-results').style.display = 'flex';

    // Animate XP counter from 0 to earned amount
    const xpElement = document.getElementById('results-xp');
    animateCounter(xpElement, 0, results.xp_earned, 1500, '+', ' XP');

    // Show streak bonus if applicable
    if (results.streak_bonus && results.streak_bonus > 0) {
        document.getElementById('streak-bonus-display').style.display = 'block';
        document.getElementById('results-streak').textContent = results.current_streak;
        document.getElementById('results-base-xp').textContent = results.base_xp;
        document.getElementById('results-streak-bonus').textContent = results.streak_bonus;
    } else {
        document.getElementById('streak-bonus-display').style.display = 'none';
    }

    // XP progress bar - calculate and animate
    const xpInCurrentLevel = results.new_xp % 100;
    const xpProgress = (xpInCurrentLevel / 100) * 100;

    // Set current level in badge
    document.getElementById('results-current-level').textContent = results.new_level;

    // Set initial XP values to 0
    document.getElementById('results-xp-current').textContent = 0;
    document.getElementById('results-xp-next').textContent = 100;

    // Animate XP counter
    const xpCurrentElement = document.getElementById('results-xp-current');
    setTimeout(() => {
        animateCounter(xpCurrentElement, 0, xpInCurrentLevel, 1200, '', '');
    }, 500);

    // Animate XP bar after a delay
    setTimeout(() => {
        document.getElementById('results-xp-fill').style.width = `${xpProgress}%`;
    }, 800);

    // Show level-up banner with animation if leveled up
    if (results.levels_gained > 0) {
        setTimeout(() => {
            const banner = document.getElementById('level-up-banner');
            banner.style.display = 'block';
            document.getElementById('old-level').textContent = results.old_level;
            document.getElementById('new-level').textContent = results.new_level;

            // Add extra animation class
            banner.classList.add('level-up-animate');
            setTimeout(() => {
                banner.classList.remove('level-up-animate');
            }, 1000);
        }, 1200);
    } else {
        document.getElementById('level-up-banner').style.display = 'none';
    }
}

// Animate a number counter
function animateCounter(element, start, end, duration, prefix = '', suffix = '') {
    const startTime = performance.now();
    const range = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + (range * easeOutQuart));

        element.textContent = `${prefix}${current}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = `${prefix}${end}${suffix}`;
        }
    }

    requestAnimationFrame(update);
}

function dismissResults() {
    // Hide the results overlay
    const resultsOverlay = document.getElementById('session-results');
    if (resultsOverlay) {
        resultsOverlay.style.display = 'none';
    }
    // Reset XP bar for next time
    document.getElementById('results-xp-fill').style.width = '0%';

    // Reset title to default
    const title = document.querySelector('.results-title');
    title.textContent = 'Session Complete! 🎉';
    title.style.background = 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))';
    title.style.webkitBackgroundClip = 'text';
    title.style.webkitTextFillColor = 'transparent';

    // Show XP progress display again
    document.querySelector('.xp-progress-display').style.display = 'block';

    // Hide failure message if it exists
    const failureMsg = document.getElementById('failure-message');
    if (failureMsg) {
        failureMsg.style.display = 'none';
    }

    // Switch back to mode selection
    document.getElementById('active-session').style.display = 'none';
    document.getElementById('mode-selection').style.display = 'block';
}

function showChallengeFailed(results) {
    // Show results overlay
    document.getElementById('session-results').style.display = 'flex';

    // Change title to "Challenge Failed"
    const title = document.querySelector('.results-title');
    title.textContent = 'Challenge Failed 😔';
    title.style.background = 'linear-gradient(135deg, #c17a5c, #a8956b)';
    title.style.webkitBackgroundClip = 'text';
    title.style.webkitTextFillColor = 'transparent';

    // Show course name
    document.getElementById('results-course-name').textContent = results.course || 'Study Session';

    // Format times
    const completedMins = Math.floor(results.duration_seconds / 60);
    const completedSecs = results.duration_seconds % 60;
    const requiredMins = Math.floor(results.challenge_duration / 60);

    // Update duration to show what was completed
    document.getElementById('results-duration').textContent =
        `${completedMins}m ${completedSecs}s / ${requiredMins}m`;

    // Show 0 XP earned
    document.getElementById('results-xp').textContent = '+0 XP';

    // Hide level-up banner
    document.getElementById('level-up-banner').style.display = 'none';

    // Hide XP progress display
    document.querySelector('.xp-progress-display').style.display = 'none';

    // Add failure message
    const resultsCard = document.querySelector('.results-card');
    let failureMsg = document.getElementById('failure-message');
    if (!failureMsg) {
        failureMsg = document.createElement('div');
        failureMsg.id = 'failure-message';
        failureMsg.className = 'failure-message';
        failureMsg.innerHTML = '💪 Don\'t give up! Try again and complete the full challenge to earn XP.';
        resultsCard.insertBefore(failureMsg, document.querySelector('.continue-btn'));
    }
    failureMsg.style.display = 'block';
}

function showHealthFailed(results) {
    // Show results overlay
    document.getElementById('session-results').style.display = 'flex';

    // Change title to "Health Depleted"
    const title = document.querySelector('.results-title');
    title.textContent = 'Health Depleted! 💔';
    title.style.background = 'linear-gradient(135deg, #c17a5c, #8b7355)';
    title.style.webkitBackgroundClip = 'text';
    title.style.webkitTextFillColor = 'transparent';

    // Show course name
    document.getElementById('results-course-name').textContent = results.course || 'Study Session';

    // Format duration
    const minutes = Math.floor(results.duration_seconds / 60);
    const seconds = results.duration_seconds % 60;
    document.getElementById('results-duration').textContent =
        minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

    // Show 0 XP earned
    document.getElementById('results-xp').textContent = '+0 XP';

    // Hide level-up banner
    document.getElementById('level-up-banner').style.display = 'none';

    // Hide XP progress display
    document.querySelector('.xp-progress-display').style.display = 'none';

    // Hide streak bonus
    document.getElementById('streak-bonus-display').style.display = 'none';

    // Add failure message
    const resultsCard = document.querySelector('.results-card');
    let failureMsg = document.getElementById('failure-message');
    if (!failureMsg) {
        failureMsg = document.createElement('div');
        failureMsg.id = 'failure-message';
        failureMsg.className = 'failure-message';
        resultsCard.insertBefore(failureMsg, document.querySelector('.continue-btn'));
    }
    failureMsg.innerHTML = '💔 Too many distractions! Stay focused to maintain your health and earn XP.';
    failureMsg.style.display = 'block';
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
            const resultsOverlay = document.getElementById('session-results');

            // Don't switch views if results are being shown
            const resultsVisible = resultsOverlay && resultsOverlay.style.display === 'flex';

            // Toggle views
            if (data.session_active) {
                modeSelection.style.display = 'none';
                document.getElementById('active-session').style.display = 'block';
                sessionWasActive = true;
            } else if (!resultsVisible) {
                // Only switch to mode selection if results aren't showing
                // This prevents switching away when health fails or challenge fails
                modeSelection.style.display = 'block';
                document.getElementById('active-session').style.display = 'none';
                sessionWasActive = false;
            } else {
                // Results are showing but session ended - keep session view visible
                // so results overlay can be seen
                document.getElementById('active-session').style.display = 'block';
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

                // Streak display
                if (data.current_streak && data.current_streak > 0) {
                    const streakBadge = document.getElementById('streak-badge');
                    const streakCount = document.getElementById('streak-count');
                    if (streakBadge && streakCount) {
                        streakCount.textContent = data.current_streak;
                        streakBadge.style.display = 'flex';
                    }
                } else {
                    const streakBadge = document.getElementById('streak-badge');
                    if (streakBadge) {
                        streakBadge.style.display = 'none';
                    }
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
