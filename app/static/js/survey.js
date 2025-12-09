// ============================================
// GESTOR DE ENCUESTA
// ============================================

class SurveyManager {
    constructor() {
        this.participantEmail = this.getEmailFromUrl();
        this.token = this.getTokenFromUrl();
        this.votes = {};
        this.init();
    }
    
    getEmailFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('email') || '';
    }
    
    getTokenFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('token') || '';
    }
    
    async init() {
        if (!this.participantEmail || !this.token) {
            showNotification('Enlace de encuesta inválido o expirado', 'danger');
            document.getElementById('survey-form').style.display = 'none';
            return;
        }
        
        await this.loadSurvey();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const form = document.getElementById('survey-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
            form.addEventListener('reset', () => this.clearVotes());
        }
    }
    
    async loadSurvey() {
        try {
            const url = `/api/voting/public/positions?email=${encodeURIComponent(this.participantEmail)}&token=${encodeURIComponent(this.token)}`;
            const response = await fetch(url);
            
            if (response.status === 404) {
                showNotification('Participante no encontrado', 'danger');
                document.getElementById('survey-form').style.display = 'none';
                return;
            }
            
            if (response.status === 403) {
                showNotification('Ya has votado en esta encuesta', 'warning');
                document.getElementById('survey-form').style.display = 'none';
                return;
            }
            
            const data = await response.json();
            this.renderSurvey(data);
            this.updateParticipantInfo(data.participant);
            
        } catch (error) {
            console.error('Error cargando encuesta:', error);
            showNotification('Error al cargar la encuesta', 'danger');
        }
    }
    
    renderSurvey(data) {
        const container = document.getElementById('positions-container');
        container.innerHTML = '';
        
        data.positions.forEach((position, index) => {
            const card = this.createPositionCard(position);
            container.appendChild(card);
        });
    }
    
    createPositionCard(position) {
        const card = document.createElement('div');
        card.className = 'survey-card';
        card.innerHTML = `
            <div class="position-title">
                <h3 class="mb-0">${position.name}</h3>
                <small>${position.description || ''}</small>
            </div>
            <div class="card-body">
                ${this.createVoteOptions(position)}
            </div>
        `;
        
        return card;
    }
    
    createVoteOptions(position) {
        let html = '';
        
        // Opciones de candidatos
        position.candidates.forEach(candidate => {
            html += `
                <label class="vote-option" data-position="${position.id}" data-type="candidate">
                    <input type="radio" name="position_${position.id}" value="${candidate.id}" 
                           class="vote-radio" data-candidate-id="${candidate.id}">
                    <div class="candidate-name">${candidate.name}</div>
                    ${candidate.description ? `<div class="candidate-description">${candidate.description}</div>` : ''}
                </label>
            `;
        });
        
        // Opciones especiales
        const specialOptions = [
            { value: 'no_se', label: '❓ No sé', icon: 'fa-question-circle' },
            { value: 'ninguno', label: '✋ Ninguno', icon: 'fa-hand-paper' },
            { value: 'abstencion', label: '⊘ Abstención', icon: 'fa-ban' },
            { value: 'blanco', label: '⬜ Voto en Blanco', icon: 'fa-square' }
        ];
        
        specialOptions.forEach(option => {
            html += `
                <label class="vote-option" data-position="${position.id}" data-type="${option.value}">
                    <input type="radio" name="position_${position.id}" value="special_${option.value}" 
                           class="vote-radio" data-vote-type="${option.value}">
                    <span class="ms-2">${option.label}</span>
                </label>
            `;
        });
        
        // Agregar event listeners a los radios
        html += `
            <script>
                document.querySelectorAll('input[name="position_${position.id}"]').forEach(radio => {
                    radio.addEventListener('change', function() {
                        const label = this.closest('.vote-option');
                        document.querySelectorAll('label[data-position="${position.id}"]').forEach(l => {
                            l.classList.remove('selected');
                        });
                        label.classList.add('selected');
                    });
                });
            </script>
        `;
        
        return html;
    }
    
    updateParticipantInfo(participant) {
        const infoEl = document.getElementById('participant-info');
        if (infoEl) {
            infoEl.textContent = `${participant.name} (${participant.email})`;
        }
        
        const nameEl = document.getElementById('participant-name');
        if (nameEl) {
            nameEl.textContent = participant.name;
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const form = document.getElementById('survey-form');
        const votes = this.collectVotes(form);
        
        if (Object.keys(votes).length === 0) {
            showNotification('Por favor selecciona al menos un voto', 'warning');
            return;
        }
        
        // Mostrar resumen de confirmación
        this.showConfirmModal(votes);
    }
    
    collectVotes(form) {
        const votes = {};
        const formData = new FormData(form);
        
        for (let [name, value] of formData) {
            if (name.startsWith('position_')) {
                const positionId = name.replace('position_', '');
                
                // Encontrar el tipo de voto
                const radio = form.querySelector(`input[name="${name}"]:checked`);
                if (radio) {
                    const voteType = radio.dataset.voteType || 'candidate';
                    const candidateId = radio.dataset.candidateId || null;
                    
                    votes[positionId] = {
                        type: voteType,
                        candidate_id: candidateId ? parseInt(candidateId) : null
                    };
                }
            }
        }
        
        return votes;
    }
    
    showConfirmModal(votes) {
        const summaryEl = document.getElementById('confirm-summary');
        let summary = '<ul class="list-unstyled">';
        
        for (let [posId, vote] of Object.entries(votes)) {
            const label = this.getVoteLabel(vote);
            summary += `<li class="mb-2"><strong>Posición:</strong> ${label}</li>`;
        }
        
        summary += '</ul>';
        summaryEl.innerHTML = summary;
        
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        modal.show();
        
        document.getElementById('confirm-submit-btn').onclick = () => this.submitVote(votes, modal);
    }
    
    getVoteLabel(vote) {
        if (vote.type === 'candidate') {
            // Buscar nombre del candidato
            const candidateId = vote.candidate_id;
            const radioButtons = document.querySelectorAll(`input[data-candidate-id="${candidateId}"]`);
            if (radioButtons.length > 0) {
                return radioButtons[0].closest('.vote-option').querySelector('.candidate-name').textContent;
            }
        } else {
            const labels = {
                'no_se': 'No sé',
                'ninguno': 'Ninguno',
                'abstencion': 'Abstención',
                'blanco': 'Voto en Blanco'
            };
            return labels[vote.type] || vote.type;
        }
        return 'Desconocido';
    }
    
    async submitVote(votes, modal) {
        try {
            const response = await fetch('/api/voting/public/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: this.participantEmail,
                    token: this.token,
                    votes: votes
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                modal.hide();
                
                // Mostrar mensaje de éxito
                const successHtml = `
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="fas fa-check-circle text-success" style="font-size: 5rem;"></i>
                        </div>
                        <h2 class="text-success mb-3">¡Gracias por tu voto!</h2>
                        <p class="text-muted mb-4">Tu voto ha sido registrado exitosamente y es completamente anónimo.</p>
                        <div class="alert alert-info" role="alert">
                            <i class="fas fa-info-circle me-2"></i>
                            Puedes cerrar esta ventana ahora.
                        </div>
                    </div>
                `;
                
                document.getElementById('survey-form').style.display = 'none';
                document.querySelector('main > .container').innerHTML = successHtml;
                
                showNotification('¡Voto registrado exitosamente!', 'success', 3000);
                
            } else {
                showNotification(data.error || 'Error al registrar voto', 'danger');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error al registrar voto', 'danger');
        }
    }
    
    clearVotes() {
        document.querySelectorAll('.vote-option').forEach(option => {
            option.classList.remove('selected');
        });
    }
}

// Inicializar al cargar
let surveyManager;
document.addEventListener('DOMContentLoaded', () => {
    surveyManager = new SurveyManager();
});
