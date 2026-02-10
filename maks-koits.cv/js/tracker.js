/**
 * Легковесный JavaScript трекер для maks-koits.cv
 * Отправляет данные о посещениях на сервер аналитики
 */

(function() {
    'use strict';
    
    // URL сервера аналитики
    // Используем прокси через основной сайт, чтобы избежать блокировки блокировщиками
    const ANALYTICS_URL = window.location.origin + '/api/track';
    
    // Собираем данные о посещении
    const trackData = {
        path: window.location.pathname + window.location.search,
        referer: document.referrer,
        userAgent: navigator.userAgent,
        language: navigator.language || navigator.userLanguage,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timestamp: new Date().toISOString()
    };
    
    // Отправляем данные (используем fetch с keepalive для надежности)
    function sendTracking() {
        const data = JSON.stringify(trackData);
        
        // Используем fetch с keepalive для надежной отправки
        fetch(ANALYTICS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: data,
            keepalive: true,
            mode: 'cors',
            credentials: 'omit'
        }).then(function(response) {
            if (!response.ok) {
                console.warn('Analytics tracking failed:', response.status, response.statusText);
            }
        }).catch(function(err) {
            console.warn('Analytics tracking error:', err);
        });
    }
    
    // Отслеживаем загрузку страницы
    if (document.readyState === 'complete') {
        sendTracking();
    } else {
        window.addEventListener('load', sendTracking);
    }
    
    // Отслеживаем переходы на SPA (если используется)
    let lastPath = trackData.path;
    const observer = new MutationObserver(function() {
        const currentPath = window.location.pathname + window.location.search;
        if (currentPath !== lastPath) {
            lastPath = currentPath;
            trackData.path = currentPath;
            trackData.referer = window.location.href;
            sendTracking();
        }
    });
    
    // Наблюдаем за изменениями в DOM (для SPA)
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Отслеживаем уход со страницы
    window.addEventListener('beforeunload', function() {
        sendTracking();
    });
})();
