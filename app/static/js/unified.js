// ============================================
// FUNCIONALIDAD UNIFICADA: Registro, Votación, Resultados
// ============================================

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function clearToken() {
    localStorage.removeItem('access_token');
}

// ============================================
// REGISTRO DE PARTICIPANTES
// ============================================

function initializeRegistrationForm() {
    const passwordField = document.getElementById('regPassword');
    const emailField = document.getElementById('regEmail');
    const registrationForm = document.getElementById('registrationForm');

    if (passwordField) {
        passwordField.addEventListener('input', validatePassword);
    }

    if (emailField) {
        let emailCheckTimeout;
        emailField.addEventListener('input', function() {
            clearTimeout(emailCheckTimeout);
            const email = this.value.trim();
            const errorDiv = document.getElementById('emailError');
            const validDiv = document.getElementById('emailValid');
            
            errorDiv.style.display = 'none';
            validDiv.style.display = 'none';

            if (!email) return;

            emailCheckTimeout = setTimeout(() => {
                checkEmailAvailability(email);
            }, 500);
        });
    }

    if (registrationForm) {
        registrationForm.addEventListener('submit', submitRegistration);
    }
}

function validatePassword() {
    const password = document.getElementById('regPassword').value;
    
    const checks = {
        'req-length': password.length >= 8,
        'req-upper': /[A-Z]/.test(password),
        'req-lower': /[a-z]/.test(password),
        'req-number': /[0-9]/.test(password)
    };

    Object.keys(checks).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.toggle('met', checks[id]);
            element.classList.toggle('unmet', !checks[id]);
        }
    });

    const passwordConfirm = document.getElementById('regConfirm');
    if (passwordConfirm && passwordConfirm.value) {
        validatePasswordMatch();
    }
}

function validatePasswordMatch() {
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regConfirm').value;
    const errorDiv = document.getElementById('passwordMatchError');

    if (confirm && password !== confirm) {
        errorDiv.textContent = 'Las contraseñas no coinciden';
        errorDiv.style.display = 'block';
        return false;
    } else {
        errorDiv.style.display = 'none';
        return true;
    }
}

function checkEmailAvailability(email) {
    fetch('/api/participant-auth/check-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        const errorDiv = document.getElementById('emailError');
        const validDiv = document.getElementById('emailValid');
        
        if (data.exists) {
            errorDiv.textContent = 'Este email ya está registrado';
            errorDiv.style.display = 'block';
            validDiv.style.display = 'none';
        } else {
            validDiv.style.display = 'block';
            errorDiv.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error al validar email:', error);
    });
}

function submitRegistration(e) {
    e.preventDefault();

    if (!validatePasswordMatch()) {
        return;
    }

    const formData = {
        email: document.getElementById('regEmail').value,
        first_name: document.getElementById('regFirstName').value,
        last_name: document.getElementById('regLastName').value,
        password: document.getElementById('regPassword').value,
        password_confirm: document.getElementById('regConfirm').value,
        phone: document.getElementById('regPhone').value || null
    };

    fetch('/api/participant-auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        const alertDiv = document.getElementById('registroAlert');
        
        if (data.message && data.message.includes('éxito') || data.message && data.message.includes('success') || data.access_token) {
            // Auto-login
            if (data.access_token) {
                setToken(data.access_token);
                alertDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> ¡Registro exitoso! Bienvenido.</div>';
                document.getElementById('registrationForm').reset();
                setTimeout(() => {
                    document.getElementById('votacion-tab').click();
                }, 2000);
            }
        } else if (data.error) {
            alertDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ' + data.error + '</div>';
        } else {
            alertDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error en el registro</div>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('registroAlert').innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error de conexión</div>';
    });
}

// ============================================
// VOTACIÓN
// ============================================

function loadVotingTab() {
    const token = getToken();
    const votingContent = document.getElementById('votingContent');

    if (!token) {
        document.getElementById('votingLoginRequired').style.display = 'block';
        document.getElementById('votingSurveys').style.display = 'none';
        
        // Cargar candidatos de ejemplo
        loadExampleCandidates();
        return;
    }

    // Con sesión activa - mostrar ambas secciones
    document.getElementById('votingLoginRequired').style.display = 'none';
    document.getElementById('votingSurveys').style.display = 'block';

    const container = document.getElementById('surveysContainer');
    container.innerHTML = '<div class="col-12 text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div><p class="mt-2">Cargando candidatos...</p></div>';

    // Cargar encuestas
    fetch('/api/voting/active-surveys', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => {
        if (response.status === 401) {
            clearToken();
            document.getElementById('votingLoginRequired').style.display = 'block';
            document.getElementById('votingSurveys').style.display = 'none';
            loadExampleCandidates();
            return null;
        }
        if (!response.ok) {
            throw new Error('Error al cargar encuestas');
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        
        const container = document.getElementById('surveysContainer');
        container.innerHTML = '';

        // Transformar estructura: surveys contiene positions, no candidates directamente
        if (data.surveys && data.surveys.length > 0) {
            const survey = data.surveys[0]; // Primera encuesta (general)
            
            if (survey.positions && survey.positions.length > 0) {
                // Renderizar cada posición con sus candidatos
                survey.positions.forEach(position => {
                    const positionHTML = createPositionVoting(position);
                    container.innerHTML += positionHTML;
                });

                document.getElementById('submitVotesBtn').style.display = 'block';
                document.getElementById('submitVotesBtn').onclick = submitVotes;
            } else {
                container.innerHTML = '<div class="col-12"><div class="empty-state"><i class="fas fa-inbox"></i><p>No hay candidatos disponibles para votar</p></div></div>';
                document.getElementById('submitVotesBtn').style.display = 'none';
            }
        } else {
            container.innerHTML = '<div class="col-12"><div class="empty-state"><i class="fas fa-inbox"></i><p>No hay encuestas activas en este momento</p></div></div>';
            document.getElementById('submitVotesBtn').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('surveysContainer').innerHTML = '<div class="col-12"><div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error al cargar las encuestas. Por favor, intenta de nuevo.</div></div>';
        document.getElementById('submitVotesBtn').style.display = 'none';
    });
}

function loadExampleCandidates() {
    const exampleData = {
        surveys: [{
            positions: [
                {
                    id: 1,
                    name: 'Presidente',
                    description: 'Candidatos para Presidente',
                    candidates: [
                        {
                            id: 1,
                            name: 'Juan Pérez García',
                            party: 'Partido Azul',
                            description: 'Ingeniero con 15 años de experiencia en gestión pública'
                        },
                        {
                            id: 2,
                            name: 'María López Rodríguez',
                            party: 'Partido Rojo',
                            description: 'Abogada especializada en derecho constitucional'
                        },
                        {
                            id: 3,
                            name: 'Carlos Martínez Silva',
                            party: 'Partido Verde',
                            description: 'Economista con enfoque en desarrollo sostenible'
                        }
                    ]
                },
                {
                    id: 2,
                    name: 'Vicepresidente',
                    description: 'Candidatos para Vicepresidente',
                    candidates: [
                        {
                            id: 4,
                            name: 'Ana Sánchez Flores',
                            party: 'Partido Azul',
                            description: 'Administradora pública con amplia experiencia'
                        },
                        {
                            id: 5,
                            name: 'Roberto González Díaz',
                            party: 'Partido Rojo',
                            description: 'Contador con especialidad en finanzas públicas'
                        }
                    ]
                }
            ]
        }]
    };

    const container = document.getElementById('exampleCandidatesContainer');
    if (!container) return;

    container.innerHTML = '';

    if (exampleData.surveys && exampleData.surveys.length > 0) {
        const survey = exampleData.surveys[0];
        
        if (survey.positions && survey.positions.length > 0) {
            survey.positions.forEach(position => {
                let candidatesHTML = '<div class="candidates-grid" style="opacity: 0.7;">';
                
                if (position.candidates && position.candidates.length > 0) {
                    position.candidates.forEach(candidate => {
                        candidatesHTML += `
                            <div class="candidate-card" style="cursor: default; opacity: 0.8;">
                                <div class="candidate-card-header">
                                    <div class="badge bg-secondary">Previsualización</div>
                                </div>
                                <div class="candidate-photo-container">
                                    <div class="candidate-photo-placeholder"><i class="fas fa-user-circle"></i></div>
                                </div>
                                <div class="candidate-name">${candidate.name}</div>
                                ${candidate.party ? `<div class="candidate-party">Partido: ${candidate.party}</div>` : ''}
                                ${candidate.description ? `<div class="candidate-description">${candidate.description}</div>` : ''}
                            </div>
                        `;
                    });
                }
                
                candidatesHTML += '</div>';

                const positionHTML = `
                    <div class="col-12">
                        <div class="position-voting-section">
                            <div class="position-voting-title">${position.name}</div>
                            ${position.description ? `<p style="color: #666; margin-bottom: 15px;">${position.description}</p>` : ''}
                            ${candidatesHTML}
                        </div>
                    </div>
                `;

                container.innerHTML += positionHTML;
            });
        }
    }
}


function createPositionVoting(position) {
    let candidatesHTML = '<div class="candidates-grid">';
    
    if (position.candidates && position.candidates.length > 0) {
        position.candidates.forEach(candidate => {
            candidatesHTML += `
                <div class="candidate-card position-${position.id}" data-position-id="${position.id}" data-candidate-id="${candidate.id}" onclick="selectCandidateCard(event, ${position.id}, ${candidate.id})" style="cursor: pointer;">
                    <div class="candidate-card-header">
                        <input type="radio" name="position_${position.id}" value="${candidate.id}" class="candidate-checkbox" onclick="event.stopPropagation();">
                    </div>
                    <div class="candidate-photo-container">
                        ${candidate.photo_url ? 
                            `<img src="${candidate.photo_url}" alt="${candidate.name}" class="candidate-photo">` :
                            `<div class="candidate-photo-placeholder"><i class="fas fa-user-circle"></i></div>`
                        }
                    </div>
                    <div class="candidate-name">${candidate.name}</div>
                    ${candidate.party ? `<div class="candidate-party">Partido: ${candidate.party}</div>` : ''}
                    ${candidate.description ? `<div class="candidate-description">${candidate.description}</div>` : ''}
                </div>
            `;
        });
    } else {
        candidatesHTML += '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #999;">No hay candidatos registrados para esta posición</div>';
    }
    
    candidatesHTML += '</div>';

    return `
        <div class="col-12">
            <div class="position-voting-section">
                <div class="position-voting-title">${position.name}</div>
                ${position.description ? `<p style="color: #666; margin-bottom: 15px;">${position.description}</p>` : ''}
                ${candidatesHTML}
            </div>
        </div>
    `;
}

function selectCandidateCard(event, positionId, candidateId) {
    // Deseleccionar todas las tarjetas de esta posición
    const surveysContainer = document.getElementById('surveysContainer');
    const cards = surveysContainer.querySelectorAll(`.candidate-card.position-${positionId}`);
    
    cards.forEach(card => {
        card.classList.remove('selected');
        const radio = card.querySelector(`input[name="position_${positionId}"]`);
        if (radio) {
            radio.checked = false;
        }
    });
    
    // Seleccionar la tarjeta actual
    const currentCard = event.currentTarget;
    currentCard.classList.add('selected');
    const currentRadio = currentCard.querySelector(`input[name="position_${positionId}"]`);
    if (currentRadio) {
        currentRadio.checked = true;
    }
}

function submitVotes() {
    const token = getToken();
    if (!token) {
        alert('Por favor, inicia sesión');
        return;
    }

    const votes = {};
    const radios = document.querySelectorAll('input[type="radio"]:checked');

    if (radios.length === 0) {
        alert('Por favor, selecciona al menos un candidato');
        return;
    }

    radios.forEach(radio => {
        const positionId = radio.name.replace('position_', '');
        votes[positionId] = {
            type: 'candidate',
            candidate_id: parseInt(radio.value)
        };
    });

    // Mostrar modal de confirmación
    const confirmDiv = document.getElementById('voteConfirmDetails');
    let confirmHTML = '<div style="text-align: left;"><strong>Confirma tus votos:</strong><ul>';
    
    Object.keys(votes).forEach(positionId => {
        const radio = document.querySelector(`input[name="position_${positionId}"]:checked`);
        const candidateName = radio.closest('.candidate-card').querySelector('.candidate-name').textContent;
        confirmHTML += `<li>${radio.closest('.position-voting-section').querySelector('.position-voting-title').textContent}: <strong>${candidateName}</strong></li>`;
    });
    
    confirmHTML += '</ul></div>';
    confirmDiv.innerHTML = confirmHTML;

    const confirmModal = new bootstrap.Modal(document.getElementById('voteConfirmModal'));
    confirmModal.show();

    document.getElementById('confirmVotesBtn').onclick = function() {
        const submitBtn = this;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

        fetch('/api/voting/submit-votes', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ votes: votes })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                confirmModal.hide();
                
                // Mostrar mensaje de éxito
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success alert-dismissible fade show';
                successAlert.innerHTML = `
                    <i class="fas fa-check-circle"></i> <strong>¡Votos registrados exitosamente!</strong>
                    <p class="mt-2 mb-0">Tu voto ha sido contabilizado en el sistema.</p>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.getElementById('votingContent').insertBefore(
                    successAlert, 
                    document.getElementById('votingContent').firstChild
                );
                
                loadVotingTab(); // Recargar
            } else if (data.error) {
                alert('Error: ' + data.error);
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Votos';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al enviar votos');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Votos';
        });
    };
}

// ============================================
// RESULTADOS
// ============================================

function loadResultsTab() {
    // Cargar resultados públicos
    fetch('/api/results/summary')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('resultsContainer');
        container.innerHTML = '';

        if (data.positions && data.positions.length > 0) {
            data.positions.forEach(position => {
                const positionCard = createResultCard(position);
                container.innerHTML += positionCard;
            });
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>No hay resultados disponibles</p></div>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('resultsContainer').innerHTML = '<div class="alert alert-danger">Error al cargar resultados</div>';
    });

    // Cargar estadísticas
    fetch('/api/results/statistics')
    .then(response => response.json())
    .then(data => {
        document.getElementById('totalVotes').textContent = data.total_votes || 0;
        document.getElementById('uniqueVoters').textContent = data.unique_voters || 0;
        document.getElementById('totalPositions').textContent = data.total_positions || 0;
        document.getElementById('totalCandidates').textContent = data.total_candidates || 0;
    })
    .catch(error => console.error('Error:', error));
}

function createResultCard(position) {
    let candidatesHTML = '';
    
    const totalVotes = position.candidates.reduce((sum, c) => sum + (c.votes || 0), 0);

    if (position.candidates && position.candidates.length > 0) {
        position.candidates.forEach(candidate => {
            const percentage = totalVotes > 0 ? ((candidate.votes || 0) / totalVotes) * 100 : 0;
            candidatesHTML += `
                <div class="candidate-result">
                    ${candidate.photo_url ? 
                        `<img src="${candidate.photo_url}" class="candidate-photo" alt="${candidate.name}">` :
                        `<div style="width: 60px; height: 60px; background: #e9ecef; border-radius: 50%; display: flex; align-items: center; justify-content: center;"><i class="fas fa-user"></i></div>`
                    }
                    <div style="flex: 1;">
                        <div class="candidate-vote-name">${candidate.name}</div>
                        ${candidate.party ? `<div class="candidate-vote-party">${candidate.party}</div>` : ''}
                        <div class="vote-bar">
                            <div class="vote-progress" style="width: ${percentage}%">${Math.round(percentage)}%</div>
                        </div>
                        <small style="color: #999;">${candidate.votes || 0} votos</small>
                    </div>
                </div>
            `;
        });
    }

    return `
        <div class="result-card">
            <h5 style="color: #667eea; margin-bottom: 20px;">${position.name}</h5>
            ${candidatesHTML}
        </div>
    `;
}

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay token al cargar
    const token = getToken();
    
    if (token) {
        const votingLoginRequired = document.getElementById('votingLoginRequired');
        if (votingLoginRequired) {
            votingLoginRequired.style.display = 'none';
        }
    }

    // Event listeners para tabs
    const registroTab = document.getElementById('registro-tab');
    const votacionTab = document.getElementById('votacion-tab');
    const resultadosTab = document.getElementById('resultados-tab');

    if (registroTab) {
        registroTab.addEventListener('click', function() {
            setTimeout(initializeRegistrationForm, 100);
        });
    }

    if (votacionTab) {
        votacionTab.addEventListener('click', function() {
            setTimeout(loadVotingTab, 100);
        });
    }

    if (resultadosTab) {
        resultadosTab.addEventListener('click', function() {
            setTimeout(loadResultsTab, 100);
        });
    }

    // Manejar login de participante
    const loginForm = document.getElementById('participantLoginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = {
                email: document.getElementById('loginEmail').value,
                password: document.getElementById('loginPassword').value
            };

            fetch('/api/participant-auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                const alertDiv = document.getElementById('loginAlert');
                
                if (data.access_token) {
                    setToken(data.access_token);
                    alertDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> ¡Bienvenido! Cargando candidatos...</div>';
                    
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('participantLoginModal'));
                        if (modal) modal.hide();
                        loginForm.reset();
                        
                        // Cambiar a pestaña de votación
                        const votacionTab = document.getElementById('votacion-tab');
                        if (votacionTab) {
                            votacionTab.click();
                        }
                        
                        // Cargar candidatos después de cambiar de pestaña
                        setTimeout(() => {
                            loadVotingTab();
                        }, 300);
                    }, 800);
                } else if (data.error) {
                    alertDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ' + data.error + '</div>';
                } else {
                    alertDiv.innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error de autenticación</div>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error de conexión</div>';
            });
        });
    }
});

// ============================================
// PROTECCIÓN DE ÁREA ADMINISTRATIVA
// ============================================

function checkAdminAccess() {
    const adminToken = localStorage.getItem('adminToken');
    const adminTab = document.getElementById('admin-tab');
    const adminContent = document.getElementById('admin-content');
    
    if (!adminToken) {
        // Ocultar pestaña admin si no hay sesión
        if (adminTab) adminTab.style.display = 'none';
        if (adminContent) adminContent.style.display = 'none';
        
        // Redirigir al tab de Registro
        const registroTab = document.getElementById('registro-tab');
        if (registroTab && document.querySelector('.tab-pane.show.active') === adminContent) {
            registroTab.click();
        }
    } else {
        // Mostrar pestaña admin si hay token
        if (adminTab) adminTab.style.display = 'block';
    }
}

// Llamar cuando se carga la página
checkAdminAccess();

// Funciones para mostrar modal de login
function showParticipantLogin() {
    const modal = new bootstrap.Modal(document.getElementById('participantLoginModal'));
    modal.show();
}

function closeLoginAndGoToRegistry() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('participantLoginModal'));
    if (modal) modal.hide();
    setTimeout(() => {
        const registroTab = document.getElementById('registro-tab');
        if (registroTab) registroTab.click();
    }, 300);
}
