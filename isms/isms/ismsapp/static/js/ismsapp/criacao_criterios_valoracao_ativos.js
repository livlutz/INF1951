// Store asset data
let ativosData = {};

function calcularValoracaoAtual() {
    const campos = ['confidencialidade', 'integridade', 'disponibilidade', 'privacidade'];
    const valores = campos.map((campo) => {
        const checked = document.querySelector(`input[name="${campo}"]:checked`);
        return checked ? parseInt(checked.value, 10) : 0;
    });

    const valoresAvaliados = valores.filter((valor) => valor > 0);

    if (!valoresAvaliados.length) {
        return {
            score: '0.0',
            nivel: 'SEM AVALIAÇÃO',
            classe: 'sem-risco'
        };
    }

    const media = (valoresAvaliados.reduce((a, b) => a + b, 0) / valoresAvaliados.length).toFixed(1);
    const score = parseFloat(media);

    if (score >= 4.5) {
        return { score: media, nivel: 'MUITO ALTO', classe: 'muito-alto' };
    }
    if (score >= 3.5) {
        return { score: media, nivel: 'ALTO', classe: 'alto' };
    }
    if (score >= 2.5) {
        return { score: media, nivel: 'MÉDIO', classe: 'medio' };
    }
    if (score >= 1.5) {
        return { score: media, nivel: 'BAIXO', classe: 'baixo' };
    }
    return { score: media, nivel: 'MUITO BAIXO', classe: 'muito-baixo' };
}

function atualizarResumoValoracao() {
    const scoreValue = document.querySelector('.score-value');
    const riskBadge = document.querySelector('.risk-badge');
    if (!scoreValue || !riskBadge) {
        return;
    }

    const resultado = calcularValoracaoAtual();
    scoreValue.textContent = resultado.score;
    riskBadge.textContent = resultado.nivel;
    riskBadge.className = `risk-badge ${resultado.classe}`;
}

function atualizarPeso(dimensao) {
    const dimensionMap = {
        'conf': 'confidencialidade',
        'int': 'integridade',
        'disp': 'disponibilidade',
        'priv': 'privacidade'
    };

    const fieldName = dimensionMap[dimensao];
    const checked = document.querySelector(`input[name="${fieldName}"]:checked`);

    if (checked) {
        const valor = parseInt(checked.value);
        const elementId = `peso-${dimensao}`;
        const elemento = document.getElementById(elementId);

        if (elemento) {
            elemento.textContent = `Peso ${valor}`;
        }
    }

    atualizarResumoValoracao();
}

function carregarAtivoSelecionado(event) {
    const select = document.getElementById('ativo-select');
    const ativoId = select.value;

    if (!ativoId) {
        // Clear the form if no asset is selected
        document.querySelectorAll('input[type="radio"]').forEach(input => {
            input.checked = false;
        });
        document.querySelectorAll('.peso-label').forEach(label => {
            label.textContent = 'Peso 0';
        });
        atualizarResumoValoracao();
        return;
    }

    // Get the selected asset data
    const ativo = ativosData[ativoId];
    if (ativo) {
        // Update radio buttons with the asset's current values
        if (ativo.confidencialidade > 0) {
            document.getElementById(`conf-${ativo.confidencialidade}`).checked = true;
            atualizarPeso('conf');
        }
        if (ativo.integridade > 0) {
            document.getElementById(`int-${ativo.integridade}`).checked = true;
            atualizarPeso('int');
        }
        if (ativo.disponibilidade > 0) {
            document.getElementById(`disp-${ativo.disponibilidade}`).checked = true;
            atualizarPeso('disp');
        }
        if (ativo.privacidade > 0) {
            document.getElementById(`priv-${ativo.privacidade}`).checked = true;
            atualizarPeso('priv');
        }

        atualizarResumoValoracao();
    }
}

// Initialize labels on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load asset data from data attributes
    const dataElement = document.getElementById('ativos-data');
    if (dataElement) {
        ativosData = JSON.parse(dataElement.textContent);
    }

    // Prevent form submission on select change
    const selectElement = document.getElementById('ativo-select');
    if (selectElement) {
        selectElement.addEventListener('change', function(e) {
            carregarAtivoSelecionado(e);
        });
    }

    atualizarPeso('conf');
    atualizarPeso('int');
    atualizarPeso('disp');
    atualizarPeso('priv');
    atualizarResumoValoracao();
});
