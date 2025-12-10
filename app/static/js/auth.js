// ============================================
// FUNCIONES DE AUTENTICACIÓN
// ============================================

class AuthManager {
    constructor() {
        this.tokenKey = 'auth_token';
        this.userKey = 'auth_user';
    }
    
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }
    
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }
    
    setUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }
    
    getUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    }
    
    isAuthenticated() {
        return this.getToken() !== null;
    }
    
    logout() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
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
        }
        
        return headers;
    }
    
    async request(method, endpoint, data = null) {
        try {
            const options = {
                method: method,
                headers: this.getHeaders()
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            
            // Manejar token expirado
            if (response.status === 401) {
                authManager.logout();
                return null;
            }
            
            // Verificar si la respuesta es JSON
            const contentType = response.headers.get('content-type');
            let result;
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                // Si no es JSON, es probablemente un error del servidor (HTML)
                const text = await response.text();
                console.error('Server response is not JSON:', text.substring(0, 200));
                throw new Error('Error del servidor. Por favor intenta de nuevo.');
            }
            
            if (!response.ok) {
                throw new Error(result.error || 'Error en la solicitud');
            }
            
            return result;
            
        } catch (error) {
            console.error('Error:', error);
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
