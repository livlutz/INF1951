// Store asset data
let ativosData = {};

function calcularValorAtivo(ativo) {
    // Calculate the asset valuation score based on CIDP ratings
    const cidpValues = [
        ativo.confidencialidade,
        ativo.integridade,
        ativo.disponibilidade,
        ativo.privacidade
    ];

    // Filter out zero values (not yet rated)
    const ratedValues = cidpValues.filter(v => v > 0);

    if (ratedValues.length === 0) {
        return {
            score: 0,
            scoreTxt: '0.0',
            nivel_risco: 'SEM AVALIAÇÃO',
            classe_risco: 'sem-risco'
        };
    }

    const average = ratedValues.reduce((a, b) => a + b, 0) / ratedValues.length;
    const score = parseFloat(average.toFixed(1));

    // Determine risk level based on score
    let nivel_risco = 'MUITO BAIXO';
    let classe_risco = 'muito-baixo';

    if (score >= 4.5) {
        nivel_risco = 'MUITO ALTO';
        classe_risco = 'muito-alto';
    } else if (score >= 3.5) {
        nivel_risco = 'ALTO';
        classe_risco = 'alto';
    } else if (score >= 2.5) {
        nivel_risco = 'MÉDIO';
        classe_risco = 'medio';
    } else if (score >= 1.5) {
        nivel_risco = 'BAIXO';
        classe_risco = 'baixo';
    }

    return {
        score: score,
        scoreTxt: score.toFixed(1),
        nivel_risco: nivel_risco,
        classe_risco: classe_risco
    };
}

function mostrarValorizacao(ativoId) {
    const cidpSection = document.querySelector('.valorizacao-cidp-section');
    const scorSection = document.querySelector('.valuation-score-section');
    const emptyState = document.querySelector('.empty-state');

    if (!ativoId) {
        // Hide all sections and show empty state
        if (cidpSection) cidpSection.style.display = 'none';
        if (scorSection) scorSection.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    const ativo = ativosData[ativoId];
    if (ativo) {
        // Update CIDP values
        document.querySelectorAll('.rating-badge').forEach((badge, index) => {
            const dimensoes = ['confidencialidade', 'integridade', 'disponibilidade', 'privacidade'];
            const valor = ativo[dimensoes[index]] || 0;
            badge.textContent = valor;
        });

        // Update rating displays
        const dimensoes = ['confidencialidade', 'integridade', 'disponibilidade', 'privacidade'];
        const sections = document.querySelectorAll('.criterio-section');

        sections.forEach((section, index) => {
            const valor = ativo[dimensoes[index]];
            const ratingItems = section.querySelectorAll('.rating-item');
            ratingItems.forEach((item, i) => {
                item.classList.remove('active');
                if ((i + 1) == valor) {
                    item.classList.add('active');
                }
            });
        });

        // Update score section
        const valuation = calcularValorAtivo(ativo);
        const scoreValue = document.querySelector('.score-value');
        const riskBadge = document.querySelector('.risk-badge');

        if (scoreValue) {
            scoreValue.textContent = valuation.scoreTxt;
        }

        if (riskBadge) {
            riskBadge.className = `risk-badge ${valuation.classe_risco}`;
            riskBadge.textContent = valuation.nivel_risco;
        }

        // Show sections
        if (cidpSection) cidpSection.style.display = 'block';
        if (scorSection) scorSection.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }
}

function carregarAtivoSelecionado() {
    const select = document.getElementById('ativo-select');
    const ativoId = select.value;
    mostrarValorizacao(ativoId);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load asset data from data attributes
    const dataElement = document.getElementById('ativos-data');
    if (dataElement) {
        ativosData = JSON.parse(dataElement.textContent);
    }

    // Attach change event listener
    const selectElement = document.getElementById('ativo-select');
    if (selectElement) {
        selectElement.addEventListener('change', carregarAtivoSelecionado);

        // If an asset is already selected, display it
        if (selectElement.value) {
            mostrarValorizacao(selectElement.value);
        }
    }
});

