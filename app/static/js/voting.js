// ============================================
// SISTEMA UNIFICADO: Votación, Registro, Resultados
// ============================================

// ============== TOKEN MANAGEMENT ==============
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
}

// ============== PARTICIPANTE LOGIN ==============
function submitParticipantLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        alert('Por favor, completa todos los campos');
        return;
    }
    
    fetch('/api/participant-auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
    .then(r => r.json())
    .then(data => {
        if (data.access_token) {
            setToken(data.access_token);
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('participantLoginModal'));
            if (modal) modal.hide();
            // Limpiar campos
            document.getElementById('loginEmail').value = '';
            document.getElementById('loginPassword').value = '';
            // Cargar votación
            setTimeout(() => loadVotingTab(), 500);
        } else {
            alert('Error: ' + (data.error || 'No se pudo iniciar sesión'));
        }
    })
    .catch(e => {
        console.error('Error:', e);
        alert('Error de conexión');
    });
}

function showParticipantLogin() {
    const modal = new bootstrap.Modal(document.getElementById('participantLoginModal'));
    modal.show();
}

// ============== VOTACIÓN ==============
function loadVotingTab() {
    const token = getToken();
    
    if (!token) {
        // Sin sesión: mostrar previsualización
        document.getElementById('votingLoginRequired').style.display = 'block';
        document.getElementById('votingSurveys').style.display = 'none';
        loadExampleCandidates();
        return;
    }
    
    // Con sesión: cargar candidatos reales
    document.getElementById('votingLoginRequired').style.display = 'none';
    document.getElementById('votingSurveys').style.display = 'block';
    
    const container = document.getElementById('surveysContainer');
    container.innerHTML = '<div class="col-12 text-center"><div class="spinner-border text-primary"></div><p class="mt-2">Cargando candidatos...</p></div>';
    
    console.log('Cargando encuestas con token:', token ? 'Presente' : 'Ausente');
    
    fetch('/api/voting/active-surveys', {
        headers: { 
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    })
    .then(r => {
        console.log('Respuesta del servidor:', r.status);
        if (r.status === 401) {
            console.warn('Token inválido o expirado');
            clearToken();
            loadVotingTab();
            return null;
        }
        if (r.status === 404) {
            console.error('Endpoint no encontrado - verificar blueprint');
            container.innerHTML = '<div class="col-12 alert alert-danger">Error de configuración del servidor. Contacte al administrador.</div>';
            return null;
        }
        if (!r.ok) {
            console.error('Error en la respuesta:', r.status);
            throw new Error('Error del servidor: ' + r.status);
        }
        return r.json();
    })
    .then(data => {
        if (!data) return;
        
        console.log('Datos recibidos:', data);
        
        if (!data.surveys || data.surveys.length === 0) {
            container.innerHTML = '<div class="col-12 alert alert-warning">No hay encuestas disponibles en este momento</div>';
            return;
        }
        
        container.innerHTML = '';
        const survey = data.surveys[0];
        
        if (!survey.positions || survey.positions.length === 0) {
            container.innerHTML = '<div class="col-12 alert alert-warning">No hay posiciones disponibles para votar</div>';
            return;
        }
        
        survey.positions.forEach(pos => {
            container.innerHTML += createPositionVoting(pos);
        });
        
        document.getElementById('submitVotesBtn').style.display = 'block';
        document.getElementById('submitVotesBtn').onclick = submitVotes;
    })
    .catch(e => {
        console.error('Error completo:', e);
        container.innerHTML = '<div class="col-12 alert alert-danger">Error al cargar candidatos. Intente nuevamente.</div>';
    });
}

function createPositionVoting(position) {
    let html = '<div class="col-12"><div class="position-voting-section">';
    html += '<div class="position-voting-title">' + (position.name || 'Posición') + '</div>';
    
    if (position.description) {
        html += '<p style="color: #666; margin-bottom: 15px;">' + position.description + '</p>';
    }
    
    html += '<div class="candidates-grid">';
    
    if (position.candidates && position.candidates.length > 0) {
        position.candidates.forEach(c => {
            html += '<div class="candidate-card position-' + position.id + '" data-pos="' + position.id + '" data-cand="' + c.id + '" onclick="selectCandidate(event)">';
            html += '<div class="candidate-card-header">';
            html += '<input type="radio" name="pos_' + position.id + '" value="' + c.id + '" class="candidate-checkbox" onclick="event.stopPropagation();">';
            html += '</div>';
            html += '<div class="candidate-photo-container">';
            if (c.photo_url) {
                html += '<img src="' + c.photo_url + '" alt="' + c.name + '" class="candidate-photo">';
            } else {
                html += '<div class="candidate-photo-placeholder"><i class="fas fa-user-circle"></i></div>';
            }
            html += '</div>';
            html += '<div class="candidate-name">' + (c.name || 'Candidato') + '</div>';
            if (c.party) {
                html += '<div class="candidate-party">Partido: ' + c.party + '</div>';
            }
            if (c.description) {
                html += '<div class="candidate-description">' + c.description + '</div>';
            }
            html += '</div>';
        });
    } else {
        html += '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #999;">No hay candidatos</div>';
    }
    
    html += '</div></div></div>';
    return html;
}

function selectCandidate(event) {
    const card = event.currentTarget;
    const posId = card.getAttribute('data-pos');
    
    // Deseleccionar otras tarjetas de esta posición
    document.querySelectorAll('.candidate-card.position-' + posId).forEach(c => {
        c.classList.remove('selected');
    });
    
    // Seleccionar actual
    card.classList.add('selected');
    const radio = card.querySelector('input[type="radio"]');
    if (radio) radio.checked = true;
}

function submitVotes() {
    const token = getToken();
    if (!token) {
        alert('Por favor, inicia sesión');
        return;
    }
    
    const votes = {};
    document.querySelectorAll('input[type="radio"]:checked').forEach(r => {
        const posId = r.name.replace('pos_', '');
        votes[posId] = {
            type: 'candidate',
            candidate_id: parseInt(r.value)
        };
    });
    
    if (Object.keys(votes).length === 0) {
        alert('Selecciona al menos un candidato');
        return;
    }
    
    // Mostrar confirmación
    let confirmHtml = '<div style="text-align: left;"><strong>Confirma tus votos:</strong><ul>';
    Object.keys(votes).forEach(posId => {
        const radio = document.querySelector('input[name="pos_' + posId + '"]:checked');
        if (radio) {
            const card = radio.closest('.candidate-card');
            const posTitle = card.closest('.position-voting-section').querySelector('.position-voting-title').textContent;
            const candName = card.querySelector('.candidate-name').textContent;
            confirmHtml += '<li>' + posTitle + ': <strong>' + candName + '</strong></li>';
        }
    });
    confirmHtml += '</ul></div>';
    document.getElementById('voteConfirmDetails').innerHTML = confirmHtml;
    
    const modal = new bootstrap.Modal(document.getElementById('voteConfirmModal'));
    modal.show();
    
    document.getElementById('confirmVotesBtn').onclick = function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        
        fetch('/api/voting/submit-votes', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ votes })
        })
        .then(r => r.json())
        .then(data => {
            if (data.message) {
                modal.hide();
                const alert = document.createElement('div');
                alert.className = 'alert alert-success alert-dismissible fade show mt-3';
                alert.innerHTML = '<i class="fas fa-check-circle"></i> ¡Votos registrados exitosamente! Redirigiendo a resultados... <button class="btn-close" data-bs-dismiss="alert"></button>';
                document.getElementById('votingContent').insertBefore(alert, document.getElementById('votingContent').firstChild);
                
                // Cambiar a la pestaña de Resultados
                setTimeout(() => {
                    const resultadosTab = document.querySelector('a[href="#resultados"]');
                    if (resultadosTab) {
                        const tab = new bootstrap.Tab(resultadosTab);
                        tab.show();
                    }
                }, 2000);
            } else {
                alert('Error: ' + (data.error || 'No se registraron los votos'));
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Votos';
            }
        })
        .catch(e => {
            console.error('Error:', e);
            alert('Error al enviar votos');
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Votos';
        });
    };
}

function loadExampleCandidates() {
    const data = {
        surveys: [{
            positions: [
                {
                    id: 1,
                    name: 'Presidente',
                    description: 'Candidatos para Presidente',
                    candidates: [
                        { id: 1, name: 'Juan Pérez García', party: 'Partido Azul', description: 'Ingeniero con 15 años de experiencia' },
                        { id: 2, name: 'María López Rodríguez', party: 'Partido Rojo', description: 'Abogada especializada en derecho constitucional' },
                        { id: 3, name: 'Carlos Martínez Silva', party: 'Partido Verde', description: 'Economista con enfoque en desarrollo sostenible' }
                    ]
                },
                {
                    id: 2,
                    name: 'Vicepresidente',
                    description: 'Candidatos para Vicepresidente',
                    candidates: [
                        { id: 4, name: 'Ana Sánchez Flores', party: 'Partido Azul', description: 'Administradora pública con amplia experiencia' },
                        { id: 5, name: 'Roberto González Díaz', party: 'Partido Rojo', description: 'Contador con especialidad en finanzas públicas' }
                    ]
                }
            ]
        }]
    };
    
    const container = document.getElementById('exampleCandidatesContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (data.surveys && data.surveys.length > 0) {
        const survey = data.surveys[0];
        
        survey.positions.forEach(pos => {
            let html = '<div class="col-12"><div class="position-voting-section">';
            html += '<div class="position-voting-title">' + pos.name + '</div>';
            if (pos.description) {
                html += '<p style="color: #666; margin-bottom: 15px;">' + pos.description + '</p>';
            }
            html += '<div class="candidates-grid" style="opacity: 0.7;">';
            
            if (pos.candidates) {
                pos.candidates.forEach(c => {
                    html += '<div class="candidate-card" style="cursor: default; opacity: 0.8;">';
                    html += '<div class="candidate-card-header"><div class="badge bg-secondary">Previsualización</div></div>';
                    html += '<div class="candidate-photo-container"><div class="candidate-photo-placeholder"><i class="fas fa-user-circle"></i></div></div>';
                    html += '<div class="candidate-name">' + c.name + '</div>';
                    if (c.party) html += '<div class="candidate-party">Partido: ' + c.party + '</div>';
                    if (c.description) html += '<div class="candidate-description">' + c.description + '</div>';
                    html += '</div>';
                });
            }
            
            html += '</div></div></div>';
            container.innerHTML += html;
        });
    }
}

// ============== RESULTADOS ==============
function loadResultsTab() {
    fetch('/api/results/summary')
    .then(r => r.json())
    .then(data => {
        // Actualizar estadísticas generales
        if (data.summary) {
            document.getElementById('totalVotes').textContent = data.summary.total_votes_cast || 0;
        }
        
        // Cargar resultados por posición
        const resultsContainer = document.getElementById('resultsContainer');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';
        
        if (!data.results || data.results.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info col-12">Sin resultados disponibles aún</div>';
            return;
        }
        
        data.results.forEach(pos => {
            let html = '<div class="col-lg-6 mb-4"><div class="card"><div class="card-header bg-primary text-white">';
            html += '<h5 class="mb-0">' + (pos.position_name || 'Posición') + '</h5>';
            if (pos.position_description) {
                html += '<small>' + pos.position_description + '</small>';
            }
            html += '</div><div class="card-body">';
            
            if (pos.candidates && pos.candidates.length > 0) {
                html += '<div class="voting-results">';
                
                // Mostrar candidatos con sus votos
                pos.candidates.forEach(c => {
                    const percentage = c.percentage || 0;
                    const voteCount = c.vote_count || 0;
                    
                    html += '<div class="result-item mb-3">';
                    html += '<div class="result-header d-flex justify-content-between">';
                    html += '<span class="result-name">' + (c.name || 'Candidato') + '</span>';
                    html += '<span class="result-votes"><strong>' + voteCount + ' votos</strong></span>';
                    html += '</div>';
                    html += '<div class="progress" style="height: 25px;">';
                    html += '<div class="progress-bar bg-success" style="width: ' + percentage + '%" role="progressbar">';
                    html += '<span style="color: white; font-weight: bold;">' + percentage + '%</span>';
                    html += '</div>';
                    html += '</div>';
                    html += '</div>';
                });
                
                // Mostrar votos en blanco/abstención si existen
                if (pos.votes_by_type) {
                    const blanco = pos.votes_by_type.blanco || 0;
                    const abstencion = pos.votes_by_type.abstencion || 0;
                    const ninguno = pos.votes_by_type.ninguno || 0;
                    
                    if (blanco > 0 || abstencion > 0 || ninguno > 0) {
                        html += '<hr><div class="text-muted small">';
                        if (blanco > 0) html += '<p>Votos en blanco: ' + blanco + '</p>';
                        if (abstencion > 0) html += '<p>Abstenciones: ' + abstencion + '</p>';
                        if (ninguno > 0) html += '<p>Ninguno: ' + ninguno + '</p>';
                        html += '</div>';
                    }
                }
                
                html += '</div>';
            }
            
            html += '<div class="card-footer text-muted small">';
            html += 'Total votos en esta posición: <strong>' + (pos.total_votes || 0) + '</strong>';
            html += '</div>';
            html += '</div></div>';
            resultsContainer.innerHTML += html;
        });
    })
    .catch(e => {
        console.error('Error:', e);
        const resultsContainer = document.getElementById('votingResults');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="alert alert-danger col-12">Error al cargar resultados</div>';
        }
    });
}

// ============== INICIALIZACIÓN ==============
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar cuando se cambia de tab
    const votacionTab = document.getElementById('votacion-tab');
    const resultadosTab = document.getElementById('resultados-tab');
    
    if (votacionTab) {
        votacionTab.addEventListener('shown.bs.tab', loadVotingTab);
    }
    
    if (resultadosTab) {
        resultadosTab.addEventListener('shown.bs.tab', loadResultsTab);
    }
});
