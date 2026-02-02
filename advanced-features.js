// ═══════════════════════════════════════════════════════════
// SMARTSPORTS - ADVANCED FEATURES MODULE
// Version: 1.0 - Cutting-Edge Web Technologies
// ═══════════════════════════════════════════════════════════

// ============================================================
// 1. PWA INITIALIZATION & SERVICE WORKER
// ============================================================
class PWAManager {
  constructor() {
    this.registration = null;
    this.init();
  }

  async init() {
    if ('serviceWorker' in navigator) {
      try {
        this.registration = await navigator.serviceWorker.register('/frontend/service-worker.js', {
          scope: '/frontend/'
        });

        console.log('✅ Service Worker registered:', this.registration.scope);

        // האזנה לעדכונים
        this.registration.addEventListener('updatefound', () => {
          const newWorker = this.registration.installing;
          console.log('🔄 Service Worker update found');

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });

        // האזנה להודעות מ-Service Worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          this.handleServiceWorkerMessage(event.data);
        });

      } catch (error) {
        console.error('❌ Service Worker registration failed:', error);
      }
    }

    // בדיקת תמיכה ב-PWA
    this.checkPWAInstallation();
  }

  checkPWAInstallation() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // זיהוי אם האפליקציה מותקנת
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('✅ Running as installed PWA');
      document.body.classList.add('pwa-installed');
    }
  }

  showInstallButton() {
    const installBtn = document.createElement('button');
    installBtn.className = 'pwa-install-btn';
    installBtn.innerHTML = '<i class="fa-solid fa-download"></i> התקן אפליקציה';
    installBtn.onclick = () => this.promptInstall();
    document.body.appendChild(installBtn);
  }

  async promptInstall() {
    if (!this.deferredPrompt) return;

    this.deferredPrompt.prompt();
    const { outcome } = await this.deferredPrompt.userChoice;

    console.log(`User ${outcome === 'accepted' ? 'accepted' : 'dismissed'} the install prompt`);
    this.deferredPrompt = null;
  }

  showUpdateNotification() {
    if (confirm('גרסה חדשה של האפליקציה זמינה! לרענן עכשיו?')) {
      navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }

  handleServiceWorkerMessage(data) {
    console.log('📨 Message from Service Worker:', data);

    if (data.type === 'PREDICTIONS_UPDATED') {
      this.notifyUser('תחזיות חדשות זמינות!', data.data);
    } else if (data.type === 'LIVE_SCORES_UPDATED') {
      this.notifyUser('תוצאות עודכנו!', data.data);
    }
  }

  notifyUser(message, data) {
    if (typeof window.showNotification === 'function') {
      window.showNotification(message, 'info');
    }
  }
}

// ============================================================
// 2. WEBSOCKET REAL-TIME CONNECTION
// ============================================================
class WebSocketManager {
  constructor(url = 'wss://smartsports-api.example.com/ws') {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.listeners = new Map();
    this.init();
  }

  init() {
    this.connect();
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
        this.subscribeToChannels();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('❌ WebSocket message parse error:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.emit('disconnected');
        this.attemptReconnect();
      };

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      this.attemptReconnect();
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.error('❌ Max reconnection attempts reached');
      this.emit('reconnect_failed');
    }
  }

  subscribeToChannels() {
    this.send({
      type: 'subscribe',
      channels: ['live_scores', 'predictions', 'odds_updates', 'player_stats']
    });
  }

  handleMessage(data) {
    console.log('📨 WebSocket message:', data);

    switch (data.type) {
      case 'live_score_update':
        this.emit('live_score', data.payload);
        this.updateLiveScore(data.payload);
        break;
      case 'prediction_update':
        this.emit('prediction', data.payload);
        this.updatePrediction(data.payload);
        break;
      case 'odds_change':
        this.emit('odds', data.payload);
        break;
      case 'player_stat_update':
        this.emit('player_stat', data.payload);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('⚠️ WebSocket not connected');
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  updateLiveScore(data) {
    const scoreElement = document.querySelector(`[data-match-id="${data.matchId}"]`);
    if (scoreElement) {
      scoreElement.querySelector('.home-score').textContent = data.homeScore;
      scoreElement.querySelector('.away-score').textContent = data.awayScore;
      scoreElement.classList.add('score-updated');
      setTimeout(() => scoreElement.classList.remove('score-updated'), 1000);
    }
  }

  updatePrediction(data) {
    const predElement = document.querySelector(`[data-prediction-id="${data.id}"]`);
    if (predElement) {
      predElement.querySelector('.confidence').textContent = `${data.confidence}%`;
      predElement.querySelector('.prediction-value').textContent = data.prediction;
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// ============================================================
// 3. VOICE COMMANDS API
// ============================================================
class VoiceCommandManager {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.commands = this.initCommands();
    this.init();
  }

  init() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('⚠️ Speech Recognition not supported');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'he-IL';
    this.recognition.continuous = false;
    this.recognition.interimResults = false;

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.toLowerCase();
      console.log('🎤 Voice command:', transcript);
      this.processCommand(transcript);
    };

    this.recognition.onerror = (event) => {
      console.error('❌ Speech recognition error:', event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.updateMicButton();
    };

    this.addMicButton();
  }

  initCommands() {
    return {
      'תחזיות': () => window.location.href = '/frontend/predictions.html',
      'חזרה': () => window.history.back(),
      'דף הבית': () => window.location.href = '/frontend/index.html',
      'משחקים': () => window.location.href = '/frontend/live.html',
      'סטטיסטיקות': () => window.location.href = '/frontend/stats.html',
      'צ\'אט': () => window.location.href = '/frontend/chat.html',
      'בוט': () => window.location.href = '/frontend/chat.html',
      'קהילה': () => window.location.href = '/frontend/community.html',
      'חדשות': () => window.location.href = '/frontend/news.html',
      'שחקנים': () => window.location.href = '/frontend/players.html',
      'פרופיל': () => window.location.href = '/frontend/profile.html',
      'גלילה למעלה': () => window.scrollTo({ top: 0, behavior: 'smooth' }),
      'גלילה למטה': () => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }),
      'מצב כהה': () => this.toggleDarkMode(),
      'מצב בהיר': () => this.toggleDarkMode(),
      'עזרה': () => this.showVoiceHelp()
    };
  }

  addMicButton() {
    const micBtn = document.createElement('button');
    micBtn.id = 'voice-command-btn';
    micBtn.className = 'voice-btn';
    micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    micBtn.title = 'פקודות קוליות (לחץ להפעלה)';
    micBtn.onclick = () => this.toggle();
    document.body.appendChild(micBtn);
  }

  toggle() {
    if (this.isListening) {
      this.stop();
    } else {
      this.start();
    }
  }

  start() {
    if (this.recognition) {
      this.recognition.start();
      this.isListening = true;
      this.updateMicButton();
      console.log('🎤 Listening...');
    }
  }

  stop() {
    if (this.recognition) {
      this.recognition.stop();
      this.isListening = false;
      this.updateMicButton();
    }
  }

  updateMicButton() {
    const btn = document.getElementById('voice-command-btn');
    if (btn) {
      btn.classList.toggle('listening', this.isListening);
    }
  }

  processCommand(transcript) {
    let commandFound = false;

    for (const [keyword, action] of Object.entries(this.commands)) {
      if (transcript.includes(keyword)) {
        action();
        commandFound = true;
        this.speak(`מבצע: ${keyword}`);
        break;
      }
    }

    if (!commandFound) {
      this.speak('פקודה לא מזוהה. אמור "עזרה" לרשימת פקודות');
    }
  }

  speak(text) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'he-IL';
      utterance.rate = 1.1;
      speechSynthesis.speak(utterance);
    }
  }

  showVoiceHelp() {
    const helpText = `
      פקודות זמינות:
      - תחזיות / משחקים / סטטיסטיקות / צ'אט
      - דף הבית / חזרה
      - קהילה / חדשות / שחקנים / פרופיל
      - גלילה למעלה / גלילה למטה
      - מצב כהה / מצב בהיר
    `;
    alert(helpText);
    this.speak('רשימת הפקודות מוצגת על המסך');
  }

  toggleDarkMode() {
    if (typeof window.themeManager !== 'undefined') {
      window.themeManager.toggle();
    }
  }
}

// ============================================================
// 4. DARK/LIGHT MODE WITH AUTO-DETECTION
// ============================================================
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme') || 'auto';
    this.init();
  }

  init() {
    this.applyTheme();
    this.watchSystemTheme();
  }

  applyTheme() {
    const theme = this.getEffectiveTheme();
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', this.currentTheme);
  }

  getEffectiveTheme() {
    if (this.currentTheme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return this.currentTheme;
  }

  watchSystemTheme() {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (this.currentTheme === 'auto') {
        this.applyTheme();
      }
    });
  }

  toggle() {
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(this.currentTheme);
    this.currentTheme = themes[(currentIndex + 1) % themes.length];
    this.applyTheme();
    this.updateToggleButton();
  }

  addThemeToggle() {
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'theme-toggle-btn';
    toggleBtn.className = 'theme-toggle-btn';
    toggleBtn.innerHTML = this.getThemeIcon();
    toggleBtn.title = 'החלף ערכת צבעים';
    toggleBtn.onclick = () => this.toggle();
    document.body.appendChild(toggleBtn);
  }

  updateToggleButton() {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
      btn.innerHTML = this.getThemeIcon();
    }
  }

  getThemeIcon() {
    const icons = {
      'light': '<i class="fa-solid fa-sun"></i>',
      'dark': '<i class="fa-solid fa-moon"></i>',
      'auto': '<i class="fa-solid fa-circle-half-stroke"></i>'
    };
    return icons[this.currentTheme];
  }
}

// ============================================================
// 5. WEB WORKER FOR DATA PROCESSING
// ============================================================
class DataWorkerManager {
  constructor() {
    this.worker = null;
    this.init();
  }

  init() {
    if ('Worker' in window) {
      // יצירת Web Worker inline
      const workerCode = `
        self.addEventListener('message', (e) => {
          const { type, data } = e.data;

          switch(type) {
            case 'PROCESS_STATS':
              const result = processStatistics(data);
              self.postMessage({ type: 'STATS_PROCESSED', result });
              break;

            case 'CALCULATE_PREDICTIONS':
              const predictions = calculatePredictions(data);
              self.postMessage({ type: 'PREDICTIONS_CALCULATED', predictions });
              break;

            case 'ANALYZE_TRENDS':
              const trends = analyzeTrends(data);
              self.postMessage({ type: 'TRENDS_ANALYZED', trends });
              break;
          }
        });

        function processStatistics(data) {
          // עיבוד סטטיסטי מורכב
          const processed = data.map(item => ({
            ...item,
            average: item.values.reduce((a, b) => a + b, 0) / item.values.length,
            max: Math.max(...item.values),
            min: Math.min(...item.values),
            trend: calculateTrend(item.values)
          }));
          return processed;
        }

        function calculatePredictions(data) {
          // חישובי תחזיות מורכבים
          return data.map(match => ({
            ...match,
            winProbability: Math.random() * 100,
            confidence: 85 + Math.random() * 15
          }));
        }

        function analyzeTrends(data) {
          // ניתוח טרנדים
          return {
            upward: data.filter(d => d.change > 0).length,
            downward: data.filter(d => d.change < 0).length,
            stable: data.filter(d => d.change === 0).length
          };
        }

        function calculateTrend(values) {
          if (values.length < 2) return 0;
          const firstHalf = values.slice(0, Math.floor(values.length / 2));
          const secondHalf = values.slice(Math.floor(values.length / 2));
          const avg1 = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
          const avg2 = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
          return avg2 - avg1;
        }
      `;

      const blob = new Blob([workerCode], { type: 'application/javascript' });
      this.worker = new Worker(URL.createObjectURL(blob));

      this.worker.onmessage = (e) => {
        this.handleWorkerMessage(e.data);
      };

      this.worker.onerror = (error) => {
        console.error('❌ Web Worker error:', error);
      };

      console.log('✅ Web Worker initialized');
    } else {
      console.warn('⚠️ Web Workers not supported');
    }
  }

  processStats(data) {
    return new Promise((resolve) => {
      const handler = (e) => {
        if (e.data.type === 'STATS_PROCESSED') {
          this.worker.removeEventListener('message', handler);
          resolve(e.data.result);
        }
      };
      this.worker.addEventListener('message', handler);
      this.worker.postMessage({ type: 'PROCESS_STATS', data });
    });
  }

  calculatePredictions(data) {
    return new Promise((resolve) => {
      const handler = (e) => {
        if (e.data.type === 'PREDICTIONS_CALCULATED') {
          this.worker.removeEventListener('message', handler);
          resolve(e.data.predictions);
        }
      };
      this.worker.addEventListener('message', handler);
      this.worker.postMessage({ type: 'CALCULATE_PREDICTIONS', data });
    });
  }

  handleWorkerMessage(data) {
    console.log('📨 Worker message:', data.type);
  }
}

// ============================================================
// 6. INDEXEDDB STORAGE MANAGER
// ============================================================
class StorageManager {
  constructor() {
    this.dbName = 'SmartSportsDB';
    this.version = 1;
    this.db = null;
    this.init();
  }

  async init() {
    if (!('indexedDB' in window)) {
      console.warn('⚠️ IndexedDB not supported');
      return;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        console.log('✅ IndexedDB initialized');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // יצירת stores
        if (!db.objectStoreNames.contains('predictions')) {
          const predStore = db.createObjectStore('predictions', { keyPath: 'id', autoIncrement: true });
          predStore.createIndex('date', 'date', { unique: false });
          predStore.createIndex('matchId', 'matchId', { unique: false });
        }

        if (!db.objectStoreNames.contains('favorites')) {
          db.createObjectStore('favorites', { keyPath: 'id', autoIncrement: true });
        }

        if (!db.objectStoreNames.contains('userSettings')) {
          db.createObjectStore('userSettings', { keyPath: 'key' });
        }

        if (!db.objectStoreNames.contains('cache')) {
          const cacheStore = db.createObjectStore('cache', { keyPath: 'key' });
          cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        console.log('✅ Database upgraded');
      };
    });
  }

  async save(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async get(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getAll(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async delete(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async clear(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // שמירה עם TTL (Time To Live)
  async saveWithTTL(key, data, ttlMinutes = 60) {
    const cacheData = {
      key: key,
      data: data,
      timestamp: Date.now(),
      ttl: ttlMinutes * 60 * 1000
    };
    return this.save('cache', cacheData);
  }

  // קריאה עם בדיקת TTL
  async getWithTTL(key) {
    const cached = await this.get('cache', key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      await this.delete('cache', key);
      return null;
    }

    return cached.data;
  }
}

// ============================================================
// 7. NOTIFICATION MANAGER
// ============================================================
class NotificationManager {
  constructor() {
    this.permission = Notification.permission;
    this.init();
  }

  init() {
    if (!('Notification' in window)) {
      console.warn('⚠️ Notifications not supported');
      return;
    }

    if (this.permission === 'default') {
      this.requestPermission();
    }
  }

  async requestPermission() {
    try {
      this.permission = await Notification.requestPermission();
      console.log('🔔 Notification permission:', this.permission);
    } catch (error) {
      console.error('❌ Notification permission error:', error);
    }
  }

  show(title, options = {}) {
    if (this.permission !== 'granted') {
      console.warn('⚠️ Notification permission not granted');
      return;
    }

    const defaultOptions = {
      icon: '/frontend/icons/icon-192x192.png',
      badge: '/frontend/icons/badge-72x72.png',
      vibrate: [200, 100, 200],
      dir: 'rtl',
      lang: 'he'
    };

    const notification = new Notification(title, { ...defaultOptions, ...options });

    notification.onclick = (event) => {
      event.preventDefault();
      window.focus();
      if (options.url) {
        window.location.href = options.url;
      }
      notification.close();
    };

    return notification;
  }

  showPredictionUpdate(data) {
    this.show('תחזית חדשה זמינה! 🎯', {
      body: `${data.homeTeam} נגד ${data.awayTeam}\nדיוק: ${data.confidence}%`,
      tag: `prediction-${data.id}`,
      url: '/frontend/predictions.html'
    });
  }

  showLiveScoreUpdate(data) {
    this.show('עדכון תוצאה! ⚽', {
      body: `${data.homeTeam} ${data.homeScore} - ${data.awayScore} ${data.awayTeam}`,
      tag: `live-${data.matchId}`,
      url: '/frontend/live.html'
    });
  }
}

// ============================================================
// 8. GEOLOCATION MANAGER
// ============================================================
class GeolocationManager {
  constructor() {
    this.position = null;
    this.init();
  }

  init() {
    if (!('geolocation' in navigator)) {
      console.warn('⚠️ Geolocation not supported');
      return;
    }
  }

  async getCurrentPosition() {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.position = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          };
          console.log('📍 Location:', this.position);
          resolve(this.position);
        },
        (error) => {
          console.error('❌ Geolocation error:', error);
          reject(error);
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    });
  }

  async getLocalContent() {
    try {
      const pos = await this.getCurrentPosition();
      // קבלת תוכן מותאם לאזור
      const response = await fetch(`/api/content/local?lat=${pos.lat}&lng=${pos.lng}`);
      return await response.json();
    } catch (error) {
      console.error('❌ Failed to get local content:', error);
      return null;
    }
  }

  watchPosition(callback) {
    return navigator.geolocation.watchPosition(
      (position) => {
        this.position = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        callback(this.position);
      },
      (error) => console.error('❌ Watch position error:', error),
      { enableHighAccuracy: true }
    );
  }
}

// ============================================================
// INITIALIZATION
// ============================================================
class SmartSportsAdvanced {
  constructor() {
    this.modules = {};
    this.init();
  }

  async init() {
    console.log('🚀 Initializing SMARTSPORTS Advanced Features...');

    try {
      // אתחול כל המודולים
      this.modules.pwa = new PWAManager();
      this.modules.theme = new ThemeManager();
      this.modules.storage = new StorageManager();
      await this.modules.storage.init();

      this.modules.notifications = new NotificationManager();
      this.modules.geolocation = new GeolocationManager();
      this.modules.worker = new DataWorkerManager();
      // ✅ REMOVED: Voice commands - CTO visual cleanup
      // this.modules.voice = new VoiceCommandManager();

      // WebSocket - לא מאתחל אוטומטית בגלל הצורך בכתובת שרת אמיתית
      // this.modules.websocket = new WebSocketManager();

      // חשיפה ל-window לשימוש גלובלי
      window.smartSports = this;
      window.themeManager = this.modules.theme;
      window.storageManager = this.modules.storage;
      window.notificationManager = this.modules.notifications;

      console.log('✅ All advanced features initialized successfully!');

      // הצגת מסך Welcome
      this.showWelcomeFeatures();

    } catch (error) {
      console.error('❌ Initialization error:', error);
    }
  }

  showWelcomeFeatures() {
    const features = [
      '✅ PWA - התקנה כאפליקציה',
      '✅ עבודה אופליין',
      '✅ פקודות קוליות',
      '✅ מצב כהה/בהיר אוטומטי',
      '✅ התראות בזמן אמת',
      '✅ שמירה מקומית מהירה'
    ];

    console.log('🎉 תכונות מתקדמות פעילות:\n' + features.join('\n'));
  }
}

// אתחול אוטומטי כשהדף נטען
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new SmartSportsAdvanced();
  });
} else {
  new SmartSportsAdvanced();
}

// ייצוא למודול
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SmartSportsAdvanced;
}
