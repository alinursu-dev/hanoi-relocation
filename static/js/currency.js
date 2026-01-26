/**
 * Currency Module - Handles multi-currency support
 *
 * Base currency: RON (Romanian Leu)
 * Supported currencies: RON, EUR, USD, VND
 *
 * All amounts in the database are stored in RON.
 * This module handles conversion and display.
 */

const Currency = {
    // Default base currency
    baseCurrency: 'RON',

    // User's preferred display currency
    displayCurrency: 'RON',

    // Exchange rates (1 unit = X RON)
    rates: {
        RON: 1,
        EUR: 4.97,    // Default fallback
        USD: 4.55,    // Default fallback
        VND: 0.00018  // Default fallback
    },

    // Rate date
    rateDate: null,

    // Currency symbols and formatting
    currencies: {
        RON: { symbol: 'lei', locale: 'ro-RO', decimals: 2 },
        EUR: { symbol: '€', locale: 'de-DE', decimals: 2 },
        USD: { symbol: '$', locale: 'en-US', decimals: 2 },
        VND: { symbol: '₫', locale: 'vi-VN', decimals: 0 }
    },

    /**
     * Initialize currency module
     * Loads rates and user preference
     */
    async init() {
        try {
            // Load exchange rates
            await this.loadRates();

            // Load user preference from settings
            await this.loadPreference();

            console.log('Currency module initialized');
            console.log('Display currency:', this.displayCurrency);
            console.log('Rates:', this.rates);
        } catch (error) {
            console.warn('Currency init error, using defaults:', error);
        }
    },

    /**
     * Load exchange rates from API
     */
    async loadRates() {
        try {
            const response = await fetch('/api/currency.php?action=rates');
            const data = await response.json();

            if (data.rates) {
                this.rates = { ...this.rates, ...data.rates };
                this.rateDate = data.date;
            }
        } catch (error) {
            console.warn('Failed to load rates:', error);
        }
    },

    /**
     * Load user's preferred currency from settings
     */
    async loadPreference() {
        try {
            const settings = await API.settings.get();
            if (settings.preferred_currency) {
                this.displayCurrency = settings.preferred_currency;
            }
        } catch (error) {
            // Use default or localStorage fallback
            const saved = localStorage.getItem('preferred_currency');
            if (saved && this.currencies[saved]) {
                this.displayCurrency = saved;
            }
        }
    },

    /**
     * Set display currency
     * @param {string} currency - Currency code (RON, EUR, USD, VND)
     */
    async setDisplayCurrency(currency) {
        if (!this.currencies[currency]) {
            console.error('Invalid currency:', currency);
            return;
        }

        this.displayCurrency = currency;
        localStorage.setItem('preferred_currency', currency);

        // Save to server if authenticated
        try {
            await API.settings.update({ preferred_currency: currency });
        } catch (error) {
            console.warn('Could not save currency preference:', error);
        }

        // Dispatch event for UI updates
        window.dispatchEvent(new CustomEvent('currencyChanged', {
            detail: { currency }
        }));
    },

    /**
     * Convert amount from one currency to another
     * @param {number} amount - Amount to convert
     * @param {string} from - Source currency
     * @param {string} to - Target currency
     * @returns {number} Converted amount
     */
    convert(amount, from = 'RON', to = this.displayCurrency) {
        if (from === to) return amount;

        const fromRate = this.rates[from] || 1;
        const toRate = this.rates[to] || 1;

        // Convert to RON first, then to target
        const amountInRon = amount * fromRate;
        return amountInRon / toRate;
    },

    /**
     * Convert amount from RON to display currency
     * @param {number} amountInRon - Amount in RON
     * @returns {number} Amount in display currency
     */
    fromRon(amountInRon) {
        return this.convert(amountInRon, 'RON', this.displayCurrency);
    },

    /**
     * Convert amount from display currency to RON
     * @param {number} amount - Amount in display currency
     * @returns {number} Amount in RON
     */
    toRon(amount) {
        return this.convert(amount, this.displayCurrency, 'RON');
    },

    /**
     * Format amount for display
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency code (defaults to display currency)
     * @param {boolean} showSymbol - Whether to show currency symbol
     * @returns {string} Formatted amount
     */
    format(amount, currency = this.displayCurrency, showSymbol = true) {
        const config = this.currencies[currency];
        if (!config) return amount.toString();

        const formatted = new Intl.NumberFormat(config.locale, {
            minimumFractionDigits: config.decimals,
            maximumFractionDigits: config.decimals
        }).format(amount);

        if (!showSymbol) return formatted;

        // Position symbol based on currency
        if (currency === 'RON') {
            return `${formatted} ${config.symbol}`;
        } else if (currency === 'VND') {
            return `${formatted}${config.symbol}`;
        } else {
            return `${config.symbol}${formatted}`;
        }
    },

    /**
     * Format amount in RON as display currency
     * @param {number} amountInRon - Amount in RON
     * @param {boolean} showSymbol - Whether to show currency symbol
     * @returns {string} Formatted amount in display currency
     */
    formatFromRon(amountInRon, showSymbol = true) {
        const converted = this.fromRon(amountInRon);
        return this.format(converted, this.displayCurrency, showSymbol);
    },

    /**
     * Get exchange rate display string
     * @returns {string} e.g., "1 EUR = 4.97 RON"
     */
    getRateDisplay() {
        if (this.displayCurrency === 'RON') return '';

        const rate = this.rates[this.displayCurrency];
        return `1 ${this.displayCurrency} = ${rate.toFixed(4)} RON`;
    },

    /**
     * Create currency selector HTML
     * @param {string} id - Element ID
     * @returns {string} HTML string
     */
    createSelector(id = 'currencySelector') {
        return `
            <select id="${id}" class="form-control" onchange="Currency.setDisplayCurrency(this.value)">
                ${Object.keys(this.currencies).map(code => `
                    <option value="${code}" ${code === this.displayCurrency ? 'selected' : ''}>
                        ${code} (${this.currencies[code].symbol})
                    </option>
                `).join('')}
            </select>
        `;
    },

    /**
     * Create inline currency toggle buttons
     * @returns {string} HTML string
     */
    createToggle() {
        return `
            <div class="currency-toggle">
                ${Object.keys(this.currencies).map(code => `
                    <button type="button"
                            class="currency-btn ${code === this.displayCurrency ? 'active' : ''}"
                            onclick="Currency.setDisplayCurrency('${code}')">
                        ${code}
                    </button>
                `).join('')}
            </div>
        `;
    },

    /**
     * Create an inline currency selector for input forms
     * @param {string} id - Element ID
     * @param {string} defaultCurrency - Default selected currency
     * @returns {string} HTML string
     */
    createInputSelector(id = 'inputCurrency', defaultCurrency = null) {
        const selected = defaultCurrency || this.displayCurrency;
        return `
            <select id="${id}" class="form-control currency-input-selector">
                ${Object.keys(this.currencies).map(code => `
                    <option value="${code}" ${code === selected ? 'selected' : ''}>
                        ${code}
                    </option>
                `).join('')}
            </select>
        `;
    },

    /**
     * Convert amount from a specific currency to RON
     * @param {number} amount - Amount to convert
     * @param {string} fromCurrency - Source currency code
     * @returns {number} Amount in RON
     */
    convertToRon(amount, fromCurrency) {
        if (fromCurrency === 'RON') return amount;
        const rate = this.rates[fromCurrency] || 1;
        return amount * rate;
    },

    /**
     * Convert amount from RON to a specific currency
     * @param {number} amountInRon - Amount in RON
     * @param {string} toCurrency - Target currency code
     * @returns {number} Amount in target currency
     */
    convertFromRon(amountInRon, toCurrency) {
        if (toCurrency === 'RON') return amountInRon;
        const rate = this.rates[toCurrency] || 1;
        return amountInRon / rate;
    },

    /**
     * Get the symbol for a currency
     * @param {string} currency - Currency code
     * @returns {string} Currency symbol
     */
    getSymbol(currency) {
        return this.currencies[currency]?.symbol || currency;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Currency;
}
