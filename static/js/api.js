/**
 * API Module - Handles all communication with the PHP backend
 */

const API = {
    baseUrl: '/api',

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/${endpoint}`;

        const config = {
            credentials: 'include', // Include cookies for session
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // ============ AUTH ============

    auth: {
        async register(email, password) {
            return API.request('auth.php?action=register', {
                method: 'POST',
                body: { email, password }
            });
        },

        async login(email, password) {
            return API.request('auth.php?action=login', {
                method: 'POST',
                body: { email, password }
            });
        },

        async logout() {
            return API.request('auth.php?action=logout', {
                method: 'POST'
            });
        },

        async check() {
            return API.request('auth.php?action=check');
        },

        async changePassword(currentPassword, newPassword) {
            return API.request('auth.php?action=change_password', {
                method: 'POST',
                body: {
                    current_password: currentPassword,
                    new_password: newPassword
                }
            });
        }
    },

    // ============ DASHBOARD ============

    dashboard: {
        async getAll() {
            return API.request('dashboard.php?action=get_all');
        },

        async getStats() {
            return API.request('dashboard.php?action=stats');
        },

        async getToday() {
            return API.request('dashboard.php?action=today');
        }
    },

    // ============ SETTINGS ============

    settings: {
        async get() {
            return API.request('dashboard.php?action=settings');
        },

        async update(settings) {
            return API.request('dashboard.php?action=settings', {
                method: 'PUT',
                body: settings
            });
        }
    },

    // ============ MILESTONES ============

    milestones: {
        async getAll() {
            return API.request('dashboard.php?action=milestones');
        },

        async create(milestone) {
            return API.request('dashboard.php?action=milestones', {
                method: 'POST',
                body: milestone
            });
        },

        async update(id, milestone) {
            return API.request(`dashboard.php?action=milestones&id=${id}`, {
                method: 'PUT',
                body: milestone
            });
        },

        async delete(id) {
            return API.request(`dashboard.php?action=milestones&id=${id}`, {
                method: 'DELETE'
            });
        },

        async toggleComplete(id, completed) {
            return API.request(`dashboard.php?action=milestones&id=${id}`, {
                method: 'PUT',
                body: { completed }
            });
        }
    },

    // ============ PYTHON SESSIONS ============

    python: {
        async getAll() {
            return API.request('dashboard.php?action=python');
        },

        async create(session) {
            return API.request('dashboard.php?action=python', {
                method: 'POST',
                body: {
                    session_date: session.date,
                    hours: session.hours,
                    topic: session.topic,
                    notes: session.notes
                }
            });
        },

        async delete(id) {
            return API.request(`dashboard.php?action=python&id=${id}`, {
                method: 'DELETE'
            });
        }
    },

    // ============ VIETNAMESE SESSIONS ============

    vietnamese: {
        async getAll() {
            return API.request('dashboard.php?action=vietnamese');
        },

        async create(session) {
            return API.request('dashboard.php?action=vietnamese', {
                method: 'POST',
                body: {
                    session_date: session.date,
                    minutes: session.minutes,
                    session_type: session.type,
                    focus_area: session.focus
                }
            });
        },

        async delete(id) {
            return API.request(`dashboard.php?action=vietnamese&id=${id}`, {
                method: 'DELETE'
            });
        }
    },

    // ============ FREELANCE PROJECTS ============

    freelance: {
        async getAll() {
            return API.request('dashboard.php?action=freelance');
        },

        async create(project) {
            return API.request('dashboard.php?action=freelance', {
                method: 'POST',
                body: {
                    title: project.title,
                    project_date: project.date,
                    amount: project.amount,
                    hours: project.hours,
                    platform: project.platform,
                    description: project.description
                }
            });
        },

        async delete(id) {
            return API.request(`dashboard.php?action=freelance&id=${id}`, {
                method: 'DELETE'
            });
        }
    },

    // ============ NOTES ============

    notes: {
        async getAll() {
            return API.request('dashboard.php?action=notes');
        },

        async create(note) {
            return API.request('dashboard.php?action=notes', {
                method: 'POST',
                body: note
            });
        },

        async update(id, note) {
            return API.request(`dashboard.php?action=notes&id=${id}`, {
                method: 'PUT',
                body: note
            });
        },

        async delete(id) {
            return API.request(`dashboard.php?action=notes&id=${id}`, {
                method: 'DELETE'
            });
        }
    },

    // ============ LEARNING PATH ============

    learningPath: {
        async getAll() {
            return API.request('dashboard.php?action=learning_path');
        },

        async updateSkill(skillId, completed, projectUrl = null) {
            return API.request('dashboard.php?action=learning_path', {
                method: 'PUT',
                body: {
                    skill_id: skillId,
                    completed,
                    project_url: projectUrl
                }
            });
        }
    },

    // ============ WEEKLY REVIEWS ============

    weeklyReview: {
        async getAll() {
            return API.request('dashboard.php?action=weekly_review');
        },

        async save(review) {
            return API.request('dashboard.php?action=weekly_review', {
                method: 'POST',
                body: review
            });
        }
    },

    // ============ CURRENCY ============

    currency: {
        async getRates(date = null) {
            const endpoint = date
                ? `currency.php?action=rates&date=${date}`
                : 'currency.php?action=rates';
            return API.request(endpoint);
        },

        async convert(from, to, amount) {
            return API.request(`currency.php?action=convert&from=${from}&to=${to}&amount=${amount}`);
        },

        async getHistory(currency, days = 30) {
            return API.request(`currency.php?action=history&currency=${currency}&days=${days}`);
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
