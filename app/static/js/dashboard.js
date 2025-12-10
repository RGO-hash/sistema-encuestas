// ============================================
// GESTOR DEL DASHBOARD
// ============================================

class DashboardManager {
    constructor() {
        this.currentPage = 1;
        this.searchTimeout = null;
        this.init();
    }
    
    async init() {
        // Verificar autenticación
        if (!authManager.isAuthenticated()) {
            console.log('Usuario no autenticado, mostrando login');
            this.showLoginModal();
            return;
        }
        
        console.log('Usuario autenticado, inicializando dashboard');
        const token = authManager.getToken();
        console.log('Token presente:', !!token);
        
        this.setupEventListeners();
        
        // Cargar datos después de establecer los event listeners
        try {
            await this.loadParticipants();
            await this.loadPositions();
            await this.loadStats();
        } catch (error) {
            console.error('Error durante la inicialización:', error);
            showNotification('Error cargando datos. Por favor recarga la página.', 'danger');
        }
    }
    
    setupEventListeners() {
        // Participantes
        document.getElementById('participant-form')?.addEventListener('submit', (e) => this.handleParticipantSubmit(e));
        document.getElementById('participants-search')?.addEventListener('input', (e) => this.handleParticipantSearch(e));
        document.getElementById('send-invitations-btn')?.addEventListener('click', () => this.sendInvitations());
        
        // Posiciones
        document.getElementById('position-form')?.addEventListener('submit', (e) => this.handlePositionSubmit(e));
        document.getElementById('position-filter')?.addEventListener('change', (e) => this.loadCandidates(e.target.value));
        
        // Candidatos
        document.getElementById('candidate-form')?.addEventListener('submit', (e) => this.handleCandidateSubmit(e));
        
        // Carga en lote
        document.getElementById('bulk-upload-form')?.addEventListener('submit', (e) => this.handleBulkUpload(e));
    }
    
    async loadStats() {
        try {
            const response = await api.get('/participants/stats');
            if (response) {
                document.getElementById('total-participants').textContent = response.total;
                document.getElementById('voted-participants').textContent = response.voted;
                document.getElementById('pending-participants').textContent = response.pending;
                document.getElementById('participation-rate').textContent = response.participation_rate.toFixed(1) + '%';
                
                // Animar números
                animateNumber(document.getElementById('total-participants'), response.total);
                animateNumber(document.getElementById('voted-participants'), response.voted);
                animateNumber(document.getElementById('pending-participants'), response.pending);
            } else if (!authManager.isAuthenticated()) {
                // Si no hay respuesta y no está autenticado, mostrar login
                console.log('No autenticado, mostrando login');
                this.showLoginModal();
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }
    
    async loadParticipants(page = 1) {
        try {
            const searchQuery = document.getElementById('participants-search')?.value || '';
            const url = `/participants?page=${page}` + (searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : '');
            
            const response = await api.get(url);
            if (response) {
                this.renderParticipants(response.participants);
            }
        } catch (error) {
            console.error('Error cargando participantes:', error);
        }
    }
    
    renderParticipants(participants) {
        const container = document.getElementById('participants-list');
        
        if (participants.length === 0) {
            container.innerHTML = '<p class="text-center text-muted py-4">No hay participantes</p>';
            return;
        }
        
        let html = '<table class="table table-hover">';
        html += `
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Nombre</th>
                    <th>Estado</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        participants.forEach(p => {
            const status = p.has_voted 
                ? '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Votó</span>'
                : '<span class="badge bg-warning"><i class="fas fa-hourglass-half me-1"></i>Pendiente</span>';
            
            html += `
                <tr>
                    <td><small>${p.email}</small></td>
                    <td>${p.first_name} ${p.last_name}</td>
                    <td>${status}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="dashboardManager.editParticipant(${p.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="dashboardManager.deleteParticipant(${p.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }
    
    async handleParticipantSubmit(e) {
        e.preventDefault();
        
        if (!validateForm(e.target)) {
            showNotification('Por favor completa todos los campos requeridos', 'warning');
            return;
        }
        
        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            field1: formData.get('field1') || '',
            field2: formData.get('field2') || '',
            field3: formData.get('field3') || ''
        };
        
        const response = await api.post('/participants', data);
        if (response) {
            showNotification('Participante creado exitosamente', 'success');
            e.target.reset();
            bootstrap.Modal.getInstance(document.getElementById('addParticipantModal')).hide();
            await this.loadParticipants();
            await this.loadStats();
        }
    }
    
    handleParticipantSearch(e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadParticipants(1);
        }, 500);
    }
    
    async deleteParticipant(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este participante?')) {
            return;
        }
        
        const response = await api.delete(`/participants/${id}`);
        if (response) {
            showNotification('Participante eliminado exitosamente', 'success');
            await this.loadParticipants();
            await this.loadStats();
        }
    }
    
    async loadPositions() {
        try {
            const response = await api.get('/survey/positions');
            if (response) {
                this.renderPositions(response.positions);
                this.loadPositionFilters(response.positions);
            }
        } catch (error) {
            console.error('Error cargando posiciones:', error);
        }
    }
    
    renderPositions(positions) {
        const container = document.getElementById('positions-list');
        
        if (positions.length === 0) {
            container.innerHTML = '<p class="text-center text-muted py-4">No hay posiciones</p>';
            return;
        }
        
        let html = '<div class="row">';
        
        positions.forEach(p => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card border-left-primary">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 class="card-title">${p.name}</h5>
                                    <p class="card-text text-muted">${p.description || 'Sin descripción'}</p>
                                    <small class="text-info"><i class="fas fa-users me-1"></i>${p.candidate_count} candidatos</small>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-primary" onclick="dashboardManager.editPosition(${p.id})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="dashboardManager.deletePosition(${p.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    loadPositionFilters(positions) {
        const select = document.getElementById('candidate_position');
        if (!select) return;
        
        select.innerHTML = '<option value="">Selecciona una posición...</option>';
        positions.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.name;
            select.appendChild(option);
        });
    }
    
    async handlePositionSubmit(e) {
        e.preventDefault();
        
        const data = {
            name: document.getElementById('position_name').value,
            description: document.getElementById('position_description').value,
            order: parseInt(document.getElementById('position_order').value),
            is_active: document.getElementById('position_active').checked
        };
        
        const response = await api.post('/survey/positions', data);
        if (response) {
            showNotification('Posición creada exitosamente', 'success');
            e.target.reset();
            bootstrap.Modal.getInstance(document.getElementById('addPositionModal')).hide();
            await this.loadPositions();
        }
    }
    
    async deletePosition(id) {
        if (!confirm('¿Estás seguro?')) return;
        
        const response = await api.delete(`/survey/positions/${id}`);
        if (response) {
            showNotification('Posición eliminada exitosamente', 'success');
            await this.loadPositions();
        }
    }
    
    async loadCandidates(positionId) {
        try {
            const url = positionId ? `/survey/candidates?position_id=${positionId}` : '/survey/candidates';
            const response = await api.get(url);
            if (response) {
                this.renderCandidates(response.candidates);
            }
        } catch (error) {
            console.error('Error cargando candidatos:', error);
        }
    }
    
    renderCandidates(candidates) {
        const container = document.getElementById('candidates-list');
        
        if (candidates.length === 0) {
            container.innerHTML = '<p class="text-center text-muted py-4">No hay candidatos</p>';
            return;
        }
        
        let html = '<table class="table table-hover">';
        html += `
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        candidates.forEach(c => {
            html += `
                <tr>
                    <td><strong>${c.name}</strong></td>
                    <td><small>${truncateText(c.description || '', 50)}</small></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="dashboardManager.editCandidate(${c.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="dashboardManager.deleteCandidate(${c.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }
    
    async handleCandidateSubmit(e) {
        e.preventDefault();
        
        const data = {
            position_id: parseInt(document.getElementById('candidate_position').value),
            name: document.getElementById('candidate_name').value,
            description: document.getElementById('candidate_description').value,
            order: parseInt(document.getElementById('candidate_order').value)
        };
        
        const response = await api.post('/survey/candidates', data);
        if (response) {
            showNotification('Candidato creado exitosamente', 'success');
            e.target.reset();
            bootstrap.Modal.getInstance(document.getElementById('addCandidateModal')).hide();
            await this.loadCandidates();
        }
    }
    
    async deleteCandidate(id) {
        if (!confirm('¿Estás seguro?')) return;
        
        const response = await api.delete(`/survey/candidates/${id}`);
        if (response) {
            showNotification('Candidato eliminado exitosamente', 'success');
            await this.loadCandidates();
        }
    }
    
    async handleBulkUpload(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('csv-file');
        const file = fileInput.files[0];
        
        if (!file) {
            showNotification('Por favor selecciona un archivo', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const token = authManager.getToken();
            const response = await fetch('/api/participants/bulk-upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showNotification(`${result.created} participantes cargados exitosamente`, 'success');
                e.target.reset();
                await this.loadParticipants();
                await this.loadStats();
                
                if (result.errors.length > 0) {
                    showNotification(`${result.errors.length} filas con errores`, 'warning');
                }
            } else {
                showNotification(result.error || 'Error al cargar archivo', 'danger');
            }
        } catch (error) {
            showNotification('Error al procesar archivo', 'danger');
        }
    }
    
    async sendInvitations() {
        if (!confirm('¿Enviar invitaciones a todos los participantes que aún no han votado?')) {
            return;
        }
        
        const response = await api.post('/participants/send-invitations', {
            participant_ids: []
        });
        
        if (response) {
            showNotification(
                `Invitaciones enviadas: ${response.success_count} exitosas, ${response.failed_count} fallidas`,
                'success'
            );
        }
    }
    
    showLoginModal() {
        // Mostrar formulario de login
        const html = `
            <div class="container">
                <div class="row justify-content-center mt-5">
                    <div class="col-md-6">
                        <div class="card shadow-lg">
                            <div class="card-body p-5">
                                <h2 class="text-center mb-4">
                                    <i class="fas fa-lock text-primary"></i> Sistema de Encuestas
                                </h2>
                                <form id="login-form">
                                    <div class="mb-3">
                                        <label for="login-email" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="login-email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="login-password" class="form-label">Contraseña</label>
                                        <input type="password" class="form-control" id="login-password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">
                                        <i class="fas fa-sign-in-alt me-2"></i>Ingresar
                                    </button>
                                </form>
                                <div class="alert alert-info mt-3" role="alert">
                                    <small>
                                        <strong>Demostración:</strong> admin@encuestas.com / admin123
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.querySelector('main').innerHTML = html;
        
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;
            
            console.log('=== INICIO DE SESIÓN ===');
            console.log('Email:', email);
            
            const data = { email, password };
            
            const response = await api.post('/auth/login', data);
            console.log('Response de login:', response);
            
            if (response && response.access_token) {
                console.log('✓ Login exitoso');
                console.log('Token recibido:', response.access_token.substring(0, 20) + '...');
                
                // Guardar token y usuario
                authManager.setToken(response.access_token);
                authManager.setUser(response.user);
                
                // Verificar que se guardó
                const savedToken = authManager.getToken();
                const savedUser = authManager.getUser();
                console.log('✓ Token guardado:', !!savedToken);
                console.log('✓ Usuario guardado:', !!savedUser);
                
                if (savedToken && savedUser) {
                    console.log('Recargando página...');
                    window.location.reload();
                } else {
                    showNotification('Error: No se pudo guardar la sesión.', 'danger');
                    console.error('Fallo al guardar sesión');
                }
            } else {
                console.error('✗ Login falló');
                showNotification('Credenciales inválidas o error de conexión', 'danger');
            }
        });
    }
}

// Inicializar al cargar la página
let dashboardManager;
document.addEventListener('DOMContentLoaded', () => {
    dashboardManager = new DashboardManager();
});
