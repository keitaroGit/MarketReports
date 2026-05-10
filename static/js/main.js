/* ============================================================================
   Market Reports Dashboard - Main JavaScript
   ============================================================================ */

class DashboardManager {
    constructor() {
        this.baseUrl = '/api';
        this.refreshInterval = 30 * 60 * 1000; // 30 minutes
        this.autoRefreshTimer = null;
        this.currentSectorPeriod = 'ytd';
        this.init();
    }

    init() {
        // Setup event listeners
        this.setupEventListeners();
        
        // Initial data load
        this.loadDashboardData();
        
        // Auto-refresh data
        this.startAutoRefresh();
        
        // Update last refresh time
        this.updateLastRefreshTime();
    }

    setupEventListeners() {
        // Language toggle
        const langButton = document.getElementById('languageToggle');
        if (langButton) {
            langButton.addEventListener('click', () => {
                translationManager.toggleLanguage();
                // Reload data with new language
                this.loadDashboardData();
            });
        }

        // Manual refresh
        const refreshButton = document.getElementById('refreshButton');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Sector tabs
        document.querySelectorAll('.sector-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.sector-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.currentSectorPeriod = tab.dataset.period;
                this.renderSectorScorecard();
            });
        });
    }

    startAutoRefresh() {
        this.autoRefreshTimer = setInterval(() => {
            this.loadDashboardData();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }
    }

    async loadDashboardData() {
        const language = translationManager.getLanguage();
        
        try {
            const response = await fetch(`${this.baseUrl}/dashboard?language=${language}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.macro_overview) {
                    this.renderMacroOverview(data.macro_overview);
                }
                if (data.geopolitical_radar) {
                    this.renderGeopoliticalRadar(data.geopolitical_radar);
                }
                if (data.sector_scorecard) {
                    this.cachedSectorData = data.sector_scorecard;
                    this.renderSectorScorecard();
                }
                
                this.updateLastRefreshTime();
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async refreshData() {
        const refreshButton = document.getElementById('refreshButton');
        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.style.opacity = '0.5';
        }

        try {
            const response = await fetch(`${this.baseUrl}/refresh`, { method: 'POST' });
            if (response.ok) {
                // Wait a moment and reload
                setTimeout(() => {
                    this.loadDashboardData();
                }, 1000);
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to refresh data');
        } finally {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.style.opacity = '1';
            }
        }
    }

    renderMacroOverview(data) {
        const content = document.getElementById('macroContent');
        const loader = document.getElementById('macroLoader');
        const commentary = document.getElementById('macroCommentary');
        const commentaryText = document.getElementById('macroCommentaryText');

        if (data.error) {
            this.showError('Failed to load Macro Overview');
            loader.classList.add('hidden');
            return;
        }

        // Hide loader
        loader.classList.add('hidden');
        content.classList.remove('hidden');

        // Render macro cards
        const macroData = data.data || {};
        
        const ffRate = document.getElementById('ffRate');
        const cpi = document.getElementById('cpi');
        const gdp = document.getElementById('gdp');
        const unemployment = document.getElementById('unemployment');

        if (ffRate) ffRate.textContent = macroData.FF_RATE ? macroData.FF_RATE.toFixed(2) : '-';
        if (cpi) cpi.textContent = macroData.CPI ? macroData.CPI.toFixed(2) : '-';
        const cpiMom = document.getElementById('cpiMom');
        if (cpiMom && macroData.CPI_MOM != null) {
            const sign = macroData.CPI_MOM >= 0 ? '+' : '';
            cpiMom.textContent = `MoM: ${sign}${macroData.CPI_MOM.toFixed(1)}%`;
        }        
        if (gdp) gdp.textContent = macroData.GDP ? macroData.GDP.toFixed(2) : '-';
        if (unemployment) unemployment.textContent = macroData.UNEMPLOYMENT ? macroData.UNEMPLOYMENT.toFixed(2) : '-';

        // Render commentary
        if (data.commentary) {
            commentary.classList.remove('hidden');
            commentaryText.textContent = data.commentary;
        }
    }

    renderGeopoliticalRadar(data) {
        const content = document.getElementById('geoContent');
        const loader = document.getElementById('geoLoader');
        const summary = document.getElementById('geoSummaryText');
        const newsList = document.getElementById('newsList');

        if (data.error) {
            this.showError('Failed to load Geopolitical Radar');
            loader.classList.add('hidden');
            return;
        }

        // Hide loader
        loader.classList.add('hidden');
        content.classList.remove('hidden');

        // Render summary
        if (data.summary) {
            summary.textContent = data.summary;
        }

        // Render news items
        if (data.news && data.news.length > 0) {
            newsList.innerHTML = data.news.map((item, index) => `
                <div class="news-item" onclick="window.open('${item.url}', '_blank')">
                    <div class="news-headline">${item.title}</div>
                    <div class="news-description">${item.description || ''}</div>
                    <div class="news-meta">
                        <span>${item.source || 'News'}</span>
                        <span>${new Date(item.publishedAt).toLocaleDateString()}</span>
                    </div>
                </div>
            `).join('');
        }
    }

    renderSectorScorecard() {
        const content = document.getElementById('sectorContent');
        const loader = document.getElementById('sectorLoader');
        const table = document.getElementById('sectorTable');

        if (!this.cachedSectorData) {
            return;
        }

        if (this.cachedSectorData.error) {
            this.showError('Failed to load Sector Scorecard');
            loader.classList.add('hidden');
            return;
        }

        // Hide loader
        loader.classList.add('hidden');
        content.classList.remove('hidden');

        const language = translationManager.getLanguage();
        const sectors = this.cachedSectorData.sectors || [];

        // Render sector rows based on selected period
        const periodKey = this.currentSectorPeriod;
        
        table.innerHTML = sectors.map((sector, index) => {
            const returnValue = sector[periodKey] || 0;
            const returnClass = returnValue >= 0 ? 'return-positive' : 'return-negative';
            const prevPrice = periodKey === 'ytd' ? sector.ytd_start_price :
                  periodKey === 'monthly' ? sector.month_ago_price :
                  sector.week_ago_price;
            const returnSign = returnValue >= 0 ? '+' : '';
            const displayName = language === 'ja' ? sector.ja_name : sector.name;

            return `
    <div class="sector-row">
        <div class="sector-name">
            <div class="sector-rank">${index + 1}</div>
            <div>
                <div class="sector-ticker">${sector.ticker}</div>
                <div class="sector-full-name">${displayName}</div>
            </div>
        </div>
        <div class="sector-price">
            $${sector.current_price}
            <span class="sector-prev-price">← $${prevPrice}</span>
        </div>
        <div class="sector-return ${returnClass}">
            ${returnSign}${returnValue.toFixed(2)}%
        </div>
    </div>
`;
        }).join('');
    }

    updateLastRefreshTime() {
        const element = document.getElementById('lastUpdate');
        if (element) {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            element.textContent = `Updated: ${timeString}`;
        }
    }

    showError(message) {
        console.error(message);
        // Could be enhanced with a proper notification system
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Auto-update last refresh time every minute
setInterval(() => {
    if (window.dashboardManager) {
        window.dashboardManager.updateLastRefreshTime();
    }
}, 60000);
