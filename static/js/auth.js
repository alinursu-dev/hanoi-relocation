/**
 * Authentication Module - Frontend auth handling
 */

const Auth = {
    /**
     * Check if user is authenticated
     */
    async isAuthenticated() {
        try {
            const result = await API.auth.check();
            return result.authenticated;
        } catch (error) {
            return false;
        }
    },

    /**
     * Get current user info
     */
    async getCurrentUser() {
        try {
            const result = await API.auth.check();
            return result.authenticated ? result.user : null;
        } catch (error) {
            return null;
        }
    },

    /**
     * Register new user
     */
    async register(email, password) {
        return API.auth.register(email, password);
    },

    /**
     * Login user
     */
    async login(email, password) {
        return API.auth.login(email, password);
    },

    /**
     * Logout user
     */
    async logout() {
        await API.auth.logout();
        window.location.href = '/login.html';
    },

    /**
     * Change password
     */
    async changePassword(currentPassword, newPassword) {
        return API.auth.changePassword(currentPassword, newPassword);
    },

    /**
     * Require authentication - redirect to login if not authenticated
     */
    async requireAuth() {
        const authenticated = await this.isAuthenticated();
        if (!authenticated) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    },

    /**
     * Redirect to dashboard if already authenticated
     */
    async redirectIfAuthenticated() {
        const authenticated = await this.isAuthenticated();
        if (authenticated) {
            window.location.href = '/projects/index.html';
            return true;
        }
        return false;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}
