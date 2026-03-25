// TEST: JavaScript file is loaded
console.log('JavaScript loaded: analise_valoracao_ativos.js');

// Store asset data
let ativosData = {};
let currentAtivoId = null;
let currentValues = {
    confidencialidade: 0,
    integridade: 0,
    disponibilidade: 0,
    privacidade: 0
};

function showHiddenFieldsStatus() {
    const conf = document.getElementById('cidp-confidencialidade');
    const integ = document.getElementById('cidp-integridade');
    const disp = document.getElementById('cidp-disponibilidade');
    const priv = document.getElementById('cidp-privacidade');

    console.log('Hidden fields status:', {
        conf_exists: !!conf,
        integ_exists: !!integ,
        disp_exists: !!disp,
        priv_exists: !!priv,
        conf_value: conf ? conf.value : 'N/A',
        integ_value: integ ? integ.value : 'N/A',
        disp_value: disp ? disp.value : 'N/A',
        priv_value: priv ? priv.value : 'N/A'
    });
}

function updateHiddenFields() {
    const confidencialidadeField = document.getElementById('cidp-confidencialidade');
    const integridadeField = document.getElementById('cidp-integridade');
    const disponibilidadeField = document.getElementById('cidp-disponibilidade');
    const privacidadeField = document.getElementById('cidp-privacidade');

    if (confidencialidadeField)
        confidencialidadeField.value = currentValues.confidencialidade;
    if (integridadeField)
        integridadeField.value = currentValues.integridade;
    if (disponibilidadeField)
        disponibilidadeField.value = currentValues.disponibilidade;
    if (privacidadeField)
        privacidadeField.value = currentValues.privacidade;

    showHiddenFieldsStatus();
}

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
        currentAtivoId = null;
        return;
    }

    currentAtivoId = ativoId;
    const ativo = ativosData[ativoId];
    if (ativo) {
        // Set current values
        currentValues.confidencialidade = ativo.confidencialidade || 0;
        currentValues.integridade = ativo.integridade || 0;
        currentValues.disponibilidade = ativo.disponibilidade || 0;
        currentValues.privacidade = ativo.privacidade || 0;

        // Update hidden fields
        updateHiddenFields();

        // Update CIDP values
        document.querySelectorAll('.rating-badge').forEach((badge, index) => {
            const dimensoes = ['confidencialidade', 'integridade', 'disponibilidade', 'privacidade'];
            const valor = ativo[dimensoes[index]] || 0;
            badge.textContent = valor;
        });

        // Update rating displays and add click handlers
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

                // Remove old click handlers by cloning the element
                const newItem = item.cloneNode(true);
                item.parentNode.replaceChild(newItem, item);
            });

            // Add click handlers to fresh elements
            const ratingItemsNew = section.querySelectorAll('.rating-item');
            ratingItemsNew.forEach((item, i) => {
                item.style.cursor = 'pointer';
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const newValue = i + 1;
                    const dimensao = dimensoes[index];

                    // Update current values
                    currentValues[dimensao] = newValue;
                    console.log(`Rating clicked: ${dimensao} = ${newValue}`, currentValues);
                    updateHiddenFields();

                    // Update visual display
                    ratingItemsNew.forEach((it, idx) => {
                        it.classList.remove('active');
                        if ((idx + 1) <= newValue) {
                            it.classList.add('active');
                        }
                    });

                    // Update badge
                    section.querySelector('.rating-badge').textContent = newValue;

                    // Recalculate and update score
                    updateScore();
                });
            });
        });

        // Update score section
        updateScore();

        // Show sections
        if (cidpSection) cidpSection.style.display = 'block';
        if (scorSection) scorSection.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }
}

function updateScore() {
    const valuation = calcularValorAtivoFromValues(currentValues);
    const scoreValue = document.querySelector('.score-value');
    const riskBadge = document.querySelector('.risk-badge');

    if (scoreValue) {
        scoreValue.textContent = valuation.scoreTxt;
    }

    if (riskBadge) {
        riskBadge.className = `risk-badge ${valuation.classe_risco}`;
        riskBadge.textContent = valuation.nivel_risco;
    }
}

function calcularValorAtivoFromValues(values) {
    // Calculate the asset valuation score based on CIDP values
    const cidpValues = [
        values.confidencialidade,
        values.integridade,
        values.disponibilidade,
        values.privacidade
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

    // Add form submission handler to ensure hidden fields are updated
    const form = document.getElementById('cidp-form');
    if (form) {
        console.log('[OK] Form element found and ready for submission handler');
        form.addEventListener('submit', function(e) {
            console.log('[SUBMIT] Form submission detected');
            console.log('currentValues before update:', JSON.parse(JSON.stringify(currentValues)));

            // IMPORTANT: Update hidden fields before submission
            // This ensures the current clicked values are sent to the server
            updateHiddenFields();

            // Log what will be submitted
            const formData = new FormData(form);
            const dataObj = Object.fromEntries(formData);
            console.log('[SUBMIT] Form data to be sent:', dataObj);

            // Double-check the hidden field values
            showHiddenFieldsStatus();
        });
    } else {
        console.error('[ERROR] Form element with id="cidp-form" NOT found!');
    }
});

