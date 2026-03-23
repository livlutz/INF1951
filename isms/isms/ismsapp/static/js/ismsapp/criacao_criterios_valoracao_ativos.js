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

function carregarAtivoSelecionado() {
    const select = document.getElementById('ativo-select');
    if (select.value) {
        window.location.href = `?ativo_id=${select.value}`;
    }
}

// Initialize labels on page load
document.addEventListener('DOMContentLoaded', function() {
    atualizarPeso('conf');
    atualizarPeso('int');
    atualizarPeso('disp');
    atualizarPeso('priv');
});
