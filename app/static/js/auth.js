// ============================================
// FUNCIONES DE AUTENTICACIÓN
// ============================================

class AuthManager {
    constructor() {
        this.tokenKey = 'auth_token';
        this.userKey = 'auth_user';
        // Almacenamiento en memoria como principal
        this.memoryToken = null;
        this.memoryUser = null;
        this.useMemoryOnly = false;
    }
    
    _setInStorage(key, value) {
        // Intentar primero sessionStorage (menos restrictivo)
        try {
            sessionStorage.setItem(key, value);
            return true;
        } catch (e) {
            console.warn('sessionStorage no disponible:', e.message);
        }
        
        // Fallback a localStorage
        try {
            localStorage.setItem(key, value);
            return true;
        } catch (e) {
            console.warn('localStorage no disponible:', e.message);
        }
        
        // Usar solo memoria
        this.useMemoryOnly = true;
        return false;
    }
    
    _getFromStorage(key) {
        // Intentar sessionStorage primero
        try {
            const value = sessionStorage.getItem(key);
            if (value) return value;
        } catch (e) {
            console.warn('sessionStorage no disponible:', e.message);
        }
        
        // Intentar localStorage
        try {
            const value = localStorage.getItem(key);
            if (value) return value;
        } catch (e) {
            console.warn('localStorage no disponible:', e.message);
        }
        
        return null;
    }
    
    _removeFromStorage(key) {
        try {
            sessionStorage.removeItem(key);
        } catch (e) {}
        
        try {
            localStorage.removeItem(key);
        } catch (e) {}
    }
    
    setToken(token) {
        console.log('Guardando token...');
        this.memoryToken = token;
        this._setInStorage(this.tokenKey, token);
        console.log('Token guardado:', !!token);
    }
    
    getToken() {
        // Verificar memoria primero
        if (this.memoryToken) {
            return this.memoryToken;
        }
        
        // Buscar en storage
        const storedToken = this._getFromStorage(this.tokenKey);
        if (storedToken) {
            this.memoryToken = storedToken;
            return storedToken;
        }
        
        return null;
    }
    
    setUser(user) {
        console.log('Guardando usuario...');
        this.memoryUser = user;
        try {
            this._setInStorage(this.userKey, JSON.stringify(user));
        } catch (e) {
            console.error('Error guardando usuario:', e);
        }
        console.log('Usuario guardado:', !!user);
    }
    
    getUser() {
        // Verificar memoria primero
        if (this.memoryUser) {
            return this.memoryUser;
        }
        
        // Buscar en storage
        try {
            const storedUser = this._getFromStorage(this.userKey);
            if (storedUser) {
                this.memoryUser = JSON.parse(storedUser);
                return this.memoryUser;
            }
        } catch (e) {
            console.error('Error parseando usuario:', e);
        }
        
        return null;
    }
    
    isAuthenticated() {
        const token = this.getToken();
        return token !== null && token !== undefined && token.length > 0;
    }
    
    logout() {
        console.log('Desconectando usuario...');
        this.memoryToken = null;
        this.memoryUser = null;
        this._removeFromStorage(this.tokenKey);
        this._removeFromStorage(this.userKey);
        window.location.href = '/';
    }
}

const authManager = new AuthManager();

// ============================================
// MANEJADOR DE SOLICITUDES HTTP
// ============================================

class ApiClient {
    constructor() {
        this.baseUrl = '/api';
    }
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = authManager.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            console.debug('Token añadido al header:', token.substring(0, 20) + '...');
        } else {
            console.debug('Sin token en el header');
        }
        
        return headers;
    }
    
    async request(method, endpoint, data = null) {
        try {
            console.log(`[${method}] ${endpoint}`);
            
            const options = {
                method: method,
                headers: this.getHeaders()
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            console.log(`Response: ${response.status}`);
            
            // Manejar 401 - No autorizado
            if (response.status === 401) {
                console.warn('401 No autorizado, desconectando...');
                showNotification('Tu sesión ha expirado. Por favor inicia sesión de nuevo.', 'warning');
                authManager.logout();
                return null;
            }
            
            // Verificar si la respuesta es JSON
            const contentType = response.headers.get('content-type');
            let result;
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                // Si no es JSON, es probablemente un error del servidor
                const text = await response.text();
                console.error('Response no es JSON:', text.substring(0, 500));
                throw new Error(`Error del servidor (${response.status})`);
            }
            
            if (!response.ok) {
                console.error(`Error ${response.status}:`, result);
                const errorMsg = result.error || `Error ${response.status}`;
                throw new Error(errorMsg);
            }
            
            return result;
            
        } catch (error) {
            console.error('API Error:', error.message);
            showNotification(error.message, 'danger');
            return null;
        }
    }
    
    async get(endpoint) {
        return this.request('GET', endpoint);
    }
    
    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }
    
    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }
    
    async delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
}

const api = new ApiClient();

// ============================================
// NOTIFICACIONES
// ============================================

function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('flash-container');
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show m-3" role="alert" style="position: fixed; top: 80px; right: 20px; z-index: 1050; min-width: 300px;">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-cerrar después de la duración especificada
    setTimeout(() => {
        const alerts = container.querySelectorAll('.alert');
        if (alerts.length > 0) {
            const alert = alerts[alerts.length - 1];
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, duration);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ============================================
// LOGIN
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Verificar si estamos en la página de encuesta
    const isNotSurveyPage = !window.location.pathname.includes('/survey');
    
    if (isNotSurveyPage && !window.location.pathname.includes('/results')) {
        // Verificar autenticación en páginas protegidas
        if (authManager.isAuthenticated()) {
            updateUserInfo();
        } else if (document.getElementById('participant-form')) {
            // No redirigir si es página de encuesta
            // Mostrar login si es necesario
        }
    }
    
    // Event listener para logout
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            authManager.logout();
        });
    }
});

function updateUserInfo() {
    const user = authManager.getUser();
    const userNameEl = document.getElementById('user-name');
    
    if (user && userNameEl) {
        userNameEl.textContent = user.full_name || user.email;
    }
}

// ============================================
// MODAL DE LOGIN (si es necesario)
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Si el usuario no está autenticado y no está en la página de encuesta,
    // mostrar modal de login
    if (!authManager.isAuthenticated() && !window.location.pathname.includes('/survey')) {
        // Se manejará en dashboard.js
    }
});

// ============================================
// MANEJO DE ERRORES GLOBAL
// ============================================

window.addEventListener('unhandledrejection', event => {
    console.error('Promise rejected:', event.reason);
    showNotification('Error no manejado', 'danger');
});
