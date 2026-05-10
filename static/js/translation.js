/* ============================================================================
   Translation System - Multi-language Support
   ============================================================================ */

class TranslationManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.translations = {
            'en': {
                'Macro Overview': 'Macro Overview',
                'Geopolitical Radar': 'Geopolitical Radar',
                'Sector Scorecard': 'Sector Scorecard',
                'Fed Funds Rate': 'Fed Funds Rate',
                'CPI': 'CPI',
                'GDP Growth': 'GDP Growth',
                'Unemployment Rate': 'Unemployment Rate',
                'Weekly Commentary': 'Weekly Commentary',
                'Risk Assessment': 'Risk Assessment',
                'Latest News': 'Latest News',
                'YTD': 'YTD',
                '1M': '1M',
                '1W': '1W',
                'Real-time institutional investment dashboard': 'Real-time institutional investment dashboard',
                'Data for informational purposes only. Not investment advice.': 'Data for informational purposes only. Not investment advice.',
                'Rank': 'Rank',
                'Sector': 'Sector',
                'Current Price': 'Current Price',
                'Return': 'Return'
            },
            'ja': {
                'Macro Overview': 'マクロ概況',
                'Geopolitical Radar': '地政学リスク',
                'Sector Scorecard': 'セクタースコアカード',
                'Fed Funds Rate': 'FF金利',
                'CPI': 'CPI',
                'GDP Growth': 'GDP成長',
                'Unemployment Rate': '失業率',
                'Weekly Commentary': '週次コメント',
                'Risk Assessment': 'リスク評価',
                'Latest News': '最新ニュース',
                'YTD': '年初来',
                '1M': '1ヶ月',
                '1W': '1週間',
                'Real-time institutional investment dashboard': 'リアルタイム機関投資家向けダッシュボード',
                'Data for informational purposes only. Not investment advice.': '情報提供目的のみ。投資助言ではありません。',
                'Rank': 'ランク',
                'Sector': 'セクター',
                'Current Price': '現在価格',
                'Return': 'リターン'
            }
        };
        this.init();
    }

    init() {
        // Apply current language
        this.setLanguage(this.currentLanguage);
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('language', lang);
        this.applyTranslations();
        this.updateButtonText();
    }

    applyTranslations() {
        // Apply translations to all elements with data attributes
        document.querySelectorAll('[data-en][data-ja]').forEach(element => {
            const text = this.currentLanguage === 'en' ? 
                element.getAttribute('data-en') : 
                element.getAttribute('data-ja');
            if (text) {
                element.textContent = text;
            }
        });
    }

    updateButtonText() {
        const button = document.getElementById('languageToggle');
        if (button) {
            button.textContent = this.currentLanguage === 'en' ? '日本語' : 'English';
        }
    }

    toggleLanguage() {
        const newLang = this.currentLanguage === 'en' ? 'ja' : 'en';
        this.setLanguage(newLang);
    }

    getLanguage() {
        return this.currentLanguage;
    }
}

// Initialize translation manager globally
const translationManager = new TranslationManager();
