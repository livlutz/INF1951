// Lightweight safe initialization
let ativosData = {};
let currentAtivoId = null;
let currentValues = { confidencialidade: 0, integridade: 0, disponibilidade: 0, privacidade: 0 };

function updateHiddenFields() {
    document.getElementById('cidp-confidencialidade').value = currentValues.confidencialidade;
    document.getElementById('cidp-integridade').value = currentValues.integridade;
    document.getElementById('cidp-disponibilidade').value = currentValues.disponibilidade;
    document.getElementById('cidp-privacidade').value = currentValues.privacidade;
    updateCIDPScore();
}

function updateCIDPScore() {
    const vals = [currentValues.confidencialidade, currentValues.integridade, currentValues.disponibilidade, currentValues.privacidade];
    const sum = vals.reduce((a,b) => a + b, 0);
    const nonZero = vals.filter(v => v > 0);

    const partial = nonZero.length > 0 ? +(nonZero.reduce((a,b) => a + b, 0) / nonZero.length).toFixed(1) : 0.0;
    const complete = +(sum / 4).toFixed(1);

    // Update UI
    const partialEl = document.querySelector('.score-value');
    const completeEl = document.querySelector('.score-complete');
    const riskBadge = document.querySelector('.risk-badge');

    if (partialEl) partialEl.textContent = partial.toFixed(1);
    if (completeEl) completeEl.textContent = complete.toFixed(1);

    // choose value for risk display
    const allFilled = nonZero.length === 4;
    const valueForRisk = allFilled ? complete : partial;
    let riskLevel = 'SEM AVALIAÇÃO';
    let riskClass = 'muito-baixo';

    if (valueForRisk > 0) {
        if (valueForRisk >= 4.5) { riskLevel = 'MUITO ALTO'; riskClass = 'muito-alto'; }
        else if (valueForRisk >= 3.5) { riskLevel = 'ALTO'; riskClass = 'alto'; }
        else if (valueForRisk >= 2.5) { riskLevel = 'MÉDIO'; riskClass = 'medio'; }
        else if (valueForRisk >= 1.5) { riskLevel = 'BAIXO'; riskClass = 'baixo'; }
        else { riskLevel = 'MUITO BAIXO'; riskClass = 'muito-baixo'; }
    }

    if (riskBadge) {
        riskBadge.textContent = allFilled ? riskLevel : ('PROVISÓRIO - ' + riskLevel);
        riskBadge.className = 'risk-badge ' + riskClass;
    }
}

function setRatingVisuals(section, value) {
    const items = section.querySelectorAll('.rating-item');
    items.forEach(item => item.classList.remove('active', 'preview'));
    if (value > 0) {
        const match = Array.from(items).find(it => Number(it.dataset.value) === Number(value));
        if (match) match.classList.add('active');
    }
}

function attachRatingHandlers(section, dim) {
    const items = section.querySelectorAll('.rating-item');
    items.forEach(item => {
        item.onmouseenter = () => {
            items.forEach(it => it.classList.remove('preview'));
            item.classList.add('preview');
        };
        item.onmouseleave = () => { item.classList.remove('preview'); };
        item.onclick = (e) => {
            const newValue = Number(item.dataset.value);
            currentValues[dim] = newValue;
            setRatingVisuals(section, newValue);
            const badge = section.querySelector('.rating-badge');
            if (badge) badge.textContent = newValue;
            updateHiddenFields();
        };
    });
}

function showCIDPSection(show) {
    const cidp = document.querySelector('.valorizacao-cidp-section');
    const score = document.querySelector('.valuation-score-section');
    if (!cidp || !score) return;
    if (!show) {
        cidp.classList.remove('show');
        score.classList.remove('show');
        setTimeout(() => { cidp.style.display = 'none'; score.style.display = 'none'; }, 260);
        return;
    }
    cidp.style.display = 'block'; score.style.display = 'block';
    setTimeout(() => { cidp.classList.add('show'); score.classList.add('show'); }, 20);
}

function mostrarValorizacao(ativoId) {
    if (!ativoId) { showCIDPSection(false); return; }
    currentAtivoId = ativoId;
    const ativo = ativosData[ativoId] || {};

    currentValues.confidencialidade = ativo.confidencialidade || 0;
    currentValues.integridade = ativo.integridade || 0;
    currentValues.disponibilidade = ativo.disponibilidade || 0;
    currentValues.privacidade = ativo.privacidade || 0;

    // update badges
    const dimensoes = ['confidencialidade','integridade','disponibilidade','privacidade'];
    document.querySelectorAll('.rating-badge').forEach((badge, idx) => badge.textContent = (ativo[dimensoes[idx]] || 0));

    // update visuals and attach handlers
    const sections = document.querySelectorAll('.criterio-section');
    sections.forEach((section, index) => {
        const dim = dimensoes[index];
        const val = ativo[dim] || 0;
        setRatingVisuals(section, val);
        attachRatingHandlers(section, dim);
    });

    updateHiddenFields();
    // small delay to show fade-in
    setTimeout(() => showCIDPSection(true), 200);
}

document.addEventListener('DOMContentLoaded', function() {
    // parse safely from json_script
    const dataEl = document.getElementById('ativos-data');
    if (dataEl) {
        try { ativosData = JSON.parse(dataEl.textContent); }
        catch (e) { console.error('Failed to parse ativos data', e); ativosData = {}; }
    }

    const select = document.getElementById('ativo-select');
    const search = document.getElementById('ativo-search');

    if (search && select) {
        search.addEventListener('input', function() {
            const term = this.value.toLowerCase().trim();
            Array.from(select.options).forEach(opt => {
                if (!opt.value) return; // keep placeholder
                opt.hidden = term ? !opt.text.toLowerCase().includes(term) : false;
            });
        });
    }

    if (select) {
        select.addEventListener('change', function() { mostrarValorizacao(this.value); });
        if (select.value) mostrarValorizacao(select.value);
    }

    // Form submit: ensure hidden fields updated
    const form = document.getElementById('cidp-form');
    if (form) form.addEventListener('submit', function() { updateHiddenFields(); });
});

