// ============================================
// FUNCIONES COMUNES
// ============================================

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function formatNumber(number) {
    return new Intl.NumberFormat('es-ES').format(number);
}

function truncateText(text, length = 50) {
    if (text.length > length) {
        return text.substring(0, length) + '...';
    }
    return text;
}

// ============================================
// VALIDACIÓN DE FORMULARIOS
// ============================================

function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else if (input.type === 'email' && !validateEmail(input.value)) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// ============================================
// LOADING SPINNER
// ============================================

function showLoadingSpinner() {
    const spinner = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 text-muted">Cargando datos...</p>
        </div>
    `;
    return spinner;
}

// ============================================
// TABLA DINÁMICA
// ============================================

function createTable(columns, data) {
    let html = '<div class="table-responsive"><table class="table table-hover">';
    
    // Encabezado
    html += '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${col.label}</th>`;
    });
    html += '</tr></thead>';
    
    // Cuerpo
    html += '<tbody>';
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            let value = row[col.field] || '';
            if (col.render) {
                value = col.render(value, row);
            }
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    
    return html;
}

// ============================================
// DESCARGA DE ARCHIVOS
// ============================================

function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================
// MANEJO DE CLIPBOARD
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado al portapapeles', 'success');
    }).catch(() => {
        showNotification('Error al copiar', 'danger');
    });
}

// ============================================
// FORMATEO DE DATOS
// ============================================

function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

// ============================================
// COLORES PARA GRÁFICOS
// ============================================

const CHART_COLORS = [
    '#4361ee', // Azul primario
    '#3a0ca3', // Púrpura
    '#06a77d', // Verde
    '#f77f00', // Naranja
    '#d62828', // Rojo
    '#f1c40f', // Amarillo
    '#3498db', // Azul cielo
    '#e74c3c', // Rojo oscuro
    '#2ecc71', // Verde claro
    '#9b59b6'  // Púrpura claro
];

function getChartColor(index) {
    return CHART_COLORS[index % CHART_COLORS.length];
}

// ============================================
// ANIMACIONES DE NÚMEROS
// ============================================

function animateNumber(element, target, duration = 1000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

// ============================================
// UTILIDADES DE VALIDACIÓN
// ============================================

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// ============================================
// DEBOUNCE Y THROTTLE
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// GESTIÓN DE LOCAL STORAGE CON EXPIRACIÓN
// ============================================

function setStorageWithExpiry(key, value, expiryInMinutes) {
    const now = new Date();
    const item = {
        value: value,
        expiry: now.getTime() + (expiryInMinutes * 60 * 1000)
    };
    localStorage.setItem(key, JSON.stringify(item));
}

function getStorageWithExpiry(key) {
    const item = localStorage.getItem(key);
    if (!item) return null;
    
    const data = JSON.parse(item);
    const now = new Date();
    
    if (now.getTime() > data.expiry) {
        localStorage.removeItem(key);
        return null;
    }
    
    return data.value;
}

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
