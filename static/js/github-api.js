/**
 * GitHub API Module - Fetches public repositories for portfolio display
 */

const GitHubAPI = {
    // Cache settings
    CACHE_KEY: 'github_repos_cache',
    CACHE_TTL: 60 * 60 * 1000, // 1 hour

    /**
     * Get repositories for a user
     * @param {string} username - GitHub username
     * @returns {Promise<Array>} Array of repository objects
     */
    async getRepos(username) {
        if (!username) {
            console.warn('No GitHub username provided');
            return [];
        }

        // Check cache first
        const cached = this.getFromCache();
        if (cached && cached.username === username) {
            return cached.repos;
        }

        try {
            const url = `https://api.github.com/users/${username}/repos?sort=updated&per_page=30`;
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (!response.ok) {
                if (response.status === 403) {
                    console.warn('GitHub API rate limit exceeded');
                    return cached?.repos || [];
                }
                throw new Error(`GitHub API error: ${response.status}`);
            }

            const repos = await response.json();

            // Transform data
            const transformedRepos = repos.map(repo => ({
                id: repo.id,
                name: repo.name,
                description: repo.description,
                url: repo.html_url,
                homepage: repo.homepage,
                language: repo.language,
                stars: repo.stargazers_count,
                forks: repo.forks_count,
                topics: repo.topics || [],
                updatedAt: repo.updated_at,
                createdAt: repo.created_at,
                isForked: repo.fork
            }));

            // Cache results
            this.saveToCache(username, transformedRepos);

            return transformedRepos;
        } catch (error) {
            console.error('Failed to fetch GitHub repos:', error);
            return cached?.repos || [];
        }
    },

    /**
     * Get Python projects only
     * @param {string} username - GitHub username
     * @returns {Promise<Array>} Array of Python repository objects
     */
    async getPythonRepos(username) {
        const repos = await this.getRepos(username);
        return repos.filter(repo =>
            repo.language === 'Python' ||
            repo.topics.includes('python')
        );
    },

    /**
     * Get repositories filtered by language
     * @param {string} username - GitHub username
     * @param {string} language - Programming language
     * @returns {Promise<Array>} Filtered array of repositories
     */
    async getReposByLanguage(username, language) {
        const repos = await this.getRepos(username);
        if (!language || language === 'all') return repos;
        return repos.filter(repo =>
            repo.language?.toLowerCase() === language.toLowerCase()
        );
    },

    /**
     * Get unique languages from all repos
     * @param {Array} repos - Array of repository objects
     * @returns {Array} Array of unique language strings
     */
    getLanguages(repos) {
        const languages = new Set();
        repos.forEach(repo => {
            if (repo.language) {
                languages.add(repo.language);
            }
        });
        return Array.from(languages).sort();
    },

    /**
     * Get from localStorage cache
     * @returns {Object|null} Cached data or null
     */
    getFromCache() {
        try {
            const cached = localStorage.getItem(this.CACHE_KEY);
            if (!cached) return null;

            const data = JSON.parse(cached);
            const now = Date.now();

            if (now - data.timestamp > this.CACHE_TTL) {
                localStorage.removeItem(this.CACHE_KEY);
                return null;
            }

            return data;
        } catch {
            return null;
        }
    },

    /**
     * Save to localStorage cache
     * @param {string} username - GitHub username
     * @param {Array} repos - Repository data
     */
    saveToCache(username, repos) {
        try {
            localStorage.setItem(this.CACHE_KEY, JSON.stringify({
                username,
                repos,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.warn('Failed to cache GitHub repos:', error);
        }
    },

    /**
     * Clear cache
     */
    clearCache() {
        localStorage.removeItem(this.CACHE_KEY);
    },

    /**
     * Format date for display
     * @param {string} dateStr - ISO date string
     * @returns {string} Formatted date
     */
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short'
        });
    },

    /**
     * Get language color for display
     * @param {string} language - Programming language
     * @returns {string} Hex color code
     */
    getLanguageColor(language) {
        const colors = {
            'Python': '#3572A5',
            'JavaScript': '#f1e05a',
            'TypeScript': '#2b7489',
            'HTML': '#e34c26',
            'CSS': '#563d7c',
            'Shell': '#89e051',
            'Jupyter Notebook': '#DA5B0B',
            'SQL': '#e38c00'
        };
        return colors[language] || '#858585';
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GitHubAPI;
}
