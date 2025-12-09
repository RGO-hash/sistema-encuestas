// ============================================
// GESTOR DE RESULTADOS
// ============================================

class ResultsManager {
    constructor() {
        this.charts = {};
        this.init();
    }
    
    async init() {
        // Verificar autenticación
        if (!authManager.isAuthenticated()) {
            window.location.href = '/';
            return;
        }
        
        await this.loadResults();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        document.getElementById('export-csv-btn')?.addEventListener('click', () => this.exportCSV());
        document.getElementById('export-audit-btn')?.addEventListener('click', () => this.exportAudit());
    }
    
    async loadResults() {
        try {
            const response = await api.get('/voting/results');
            if (response) {
                this.updateStats(response.summary);
                this.renderResults(response.results);
                await this.loadTimeline();
            }
        } catch (error) {
            console.error('Error cargando resultados:', error);
        }
    }
    
    updateStats(summary) {
        document.getElementById('total-stats').textContent = summary.total_participants;
        document.getElementById('voted-stats').textContent = summary.voted_participants;
        document.getElementById('pending-stats').textContent = summary.pending_participants;
        document.getElementById('rate-stats').textContent = summary.participation_rate.toFixed(1) + '%';
        
        // Animar números
        animateNumber(document.getElementById('total-stats'), summary.total_participants);
        animateNumber(document.getElementById('voted-stats'), summary.voted_participants);
        animateNumber(document.getElementById('pending-stats'), summary.pending_participants);
    }
    
    renderResults(results) {
        const container = document.getElementById('results-container');
        container.innerHTML = '';
        
        for (let [positionId, positionData] of Object.entries(results)) {
            const card = this.createResultCard(positionData);
            container.appendChild(card);
        }
    }
    
    createResultCard(positionData) {
        const div = document.createElement('div');
        div.className = 'col-12 mb-4';
        
        const candidateData = [];
        for (let [candId, candData] of Object.entries(positionData.candidates)) {
            candidateData.push({
                label: candData.name,
                votes: candData.votes,
                percentage: candData.percentage
            });
        }
        
        // Ordenar por votos descendentes
        candidateData.sort((a, b) => b.votes - a.votes);
        
        const chartId = `chart_${positionData.position_id}`;
        
        let html = `
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-light">
                    <h4 class="mb-0">
                        <i class="fas fa-poll me-2 text-primary"></i>${positionData.position_name}
                    </h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-lg-6">
                            <canvas id="${chartId}"></canvas>
                        </div>
                        <div class="col-lg-6">
                            <h6 class="mb-3">Resultados Detallados</h6>
                            <div class="list-group">
        `;
        
        // Candidatos
        candidateData.forEach((cand, index) => {
            const percentage = cand.percentage || 0;
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong>${cand.label}</strong>
                        <span class="badge bg-primary">${cand.votes} votos</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar" style="width: ${percentage}%"></div>
                    </div>
                    <small class="text-muted">${percentage.toFixed(2)}%</small>
                </div>
            `;
        });
        
        // Votos especiales
        html += `
                            </div>
                            <h6 class="mt-4 mb-3">Votos Especiales</h6>
                            <table class="table table-sm">
        `;
        
        const specialVotes = [
            { type: 'no_se', label: '❓ No sé' },
            { type: 'ninguno', label: '✋ Ninguno' },
            { type: 'abstencion', label: '⊘ Abstención' },
            { type: 'blanco', label: '⬜ Voto en Blanco' }
        ];
        
        specialVotes.forEach(sv => {
            const data = positionData.special_votes[sv.type];
            const percentage = data.percentage || 0;
            html += `
                <tr>
                    <td>${sv.label}</td>
                    <td class="text-end"><strong>${data.count}</strong></td>
                    <td class="text-end text-muted">${percentage.toFixed(2)}%</td>
                </tr>
            `;
        });
        
        // Ganador
        let winnerHtml = '';
        if (positionData.winner) {
            winnerHtml = `
                <div class="alert alert-success mt-4" role="alert">
                    <i class="fas fa-trophy me-2 text-warning"></i>
                    <strong>Ganador:</strong> ${positionData.winner.candidate_name}
                    <br><small>${positionData.winner.votes} votos (${positionData.winner.percentage.toFixed(2)}%)</small>
                </div>
            `;
        }
        
        html += `
                            </table>
                        </div>
                    </div>
                    ${winnerHtml}
                </div>
            </div>
        `;
        
        div.innerHTML = html;
        
        // Renderizar gráfico después de agregar al DOM
        setTimeout(() => {
            this.createChart(chartId, candidateData, positionData.position_id);
        }, 100);
        
        return div;
    }
    
    createChart(chartId, data, positionId) {
        const ctx = document.getElementById(chartId);
        if (!ctx) return;
        
        const labels = data.map(d => d.label);
        const votes = data.map(d => d.votes);
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: votes,
                    backgroundColor: [
                        '#4361ee',
                        '#3a0ca3',
                        '#06a77d',
                        '#f77f00',
                        '#d62828',
                        '#f1c40f',
                        '#3498db',
                        '#e74c3c',
                        '#2ecc71',
                        '#9b59b6'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: "'Inter', 'Roboto', sans-serif" },
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed || 0) / total * 100).toFixed(2);
                                return `${context.label}: ${context.parsed} votos (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        this.charts[positionId] = chart;
    }
    
    async loadTimeline() {
        try {
            const response = await api.get('/voting/results/timeline');
            if (response && response.timeline) {
                this.createTimelineChart(response.timeline);
            }
        } catch (error) {
            console.error('Error cargando línea de tiempo:', error);
        }
    }
    
    createTimelineChart(timeline) {
        const ctx = document.getElementById('timeline-chart');
        if (!ctx) return;
        
        const dates = timeline.map(d => new Date(d.date).toLocaleDateString('es-ES'));
        const votes = timeline.map(d => d.votes);
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Votos por día',
                    data: votes,
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4361ee',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            font: { family: "'Inter', 'Roboto', sans-serif" },
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: { family: "'Inter', 'Roboto', sans-serif" },
                        bodyFont: { family: "'Inter', 'Roboto', sans-serif" }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
        
        this.charts.timeline = chart;
    }
    
    async exportCSV() {
        try {
            const response = await fetch('/api/voting/results/export-csv', {
                headers: {
                    'Authorization': `Bearer ${authManager.getToken()}`
                }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `encuesta_resultados_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showNotification('CSV descargado exitosamente', 'success');
            }
        } catch (error) {
            console.error('Error descargando CSV:', error);
            showNotification('Error al descargar CSV', 'danger');
        }
    }
    
    async exportAudit() {
        try {
            const response = await fetch('/api/voting/results/export-audit', {
                headers: {
                    'Authorization': `Bearer ${authManager.getToken()}`
                }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `auditoria_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showNotification('Auditoría descargada exitosamente', 'success');
            }
        } catch (error) {
            console.error('Error descargando auditoría:', error);
            showNotification('Error al descargar auditoría', 'danger');
        }
    }
}

// Inicializar al cargar
let resultsManager;
document.addEventListener('DOMContentLoaded', () => {
    resultsManager = new ResultsManager();
});
