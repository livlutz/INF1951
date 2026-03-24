// Store asset data
let ativosData = {};

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
            label.textContent = 'Peso 1';
        });
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
});
