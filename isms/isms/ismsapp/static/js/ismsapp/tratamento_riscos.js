
/*CONSTANTS — keep the frontend aligned with the backend */

const CONTROL_REDUCTION_STEP = 10;
const CONTROL_EFFECTIVENESS = {
  preventivo: {
    label: 'Preventivo',
    reduces_prob: true, reduces_cons: false,
  },
  detectivo: {
    label: 'Detectivo',
    reduces_prob: true, reduces_cons: true,
  },
  corretivo: {
    label: 'Corretivo / Contingência',
    reduces_prob: false, reduces_cons: true,
  },
};

const MAX_REDUCTION = 95;

/*BOOTSTRAP */

document.addEventListener('DOMContentLoaded', function () {
  buildControlesCheckboxes();
  initControlesSearch();
  initStrategySelection();
  initReductionInputListeners();
  initFormValidation();
  triggerInitialPreview();
});

/* CONTROLS — checkbox list builder */

function buildControlesCheckboxes() {
  const select    = document.querySelector('select[name="controles"]');
  const container = document.getElementById('controles-checkbox-list');
  if (!select || !container) return;

  container.innerHTML = '';

  Array.from(select.options).forEach(function (option) {
    const wrapper = document.createElement('label');
    wrapper.className = 'checkbox-asset-item';
    wrapper.dataset.label = option.text.toLowerCase();

    const cb = document.createElement('input');
    cb.type    = 'checkbox';
    cb.value   = option.value;
    cb.className = 'asset-cb';
    cb.checked = option.selected;
    cb.dataset.tipo = option.dataset.tipo || '';
    cb.dataset.tipos = option.dataset.tipos || option.dataset.tipo || '';

    cb.addEventListener('change', function () {
      option.selected = this.checked;
      updateControlesSummary();
      recalculateControlReductions();
    });

    const label = document.createElement('span');
    label.className  = 'asset-cb-label';
    label.textContent = option.text;

    wrapper.appendChild(cb);
    wrapper.appendChild(label);
    container.appendChild(wrapper);
  });

  updateControlesSummary();

  // Recompute immediately so the inputs always reflect only the controls.
  setTimeout(recalculateControlReductions, 150);
}

function initControlesSearch() {
  const input     = document.getElementById('controles-search');
  const container = document.getElementById('controles-checkbox-list');
  if (!input || !container) return;

  input.addEventListener('input', function () {
    const term = this.value.toLowerCase().trim();
    container.querySelectorAll('.checkbox-asset-item').forEach(function (item) {
      item.style.display = (!term || item.dataset.label.includes(term)) ? '' : 'none';
    });
  });
}

function updateControlesSummary() {
  const el = document.getElementById('controles-count');
  if (el) {
    el.textContent = document.querySelectorAll('#controles-checkbox-list .asset-cb:checked').length;
  }
}

/*CONTROL-BASED REDUCTION — pure client-side */

function recalculateControlReductions() {
  const checkedBoxes = document.querySelectorAll('#controles-checkbox-list .asset-cb:checked');
  const buckets = { preventivo: 0, detectivo: 0, corretivo: 0 };

  checkedBoxes.forEach(function (cb) {
    const tipos = String(cb.dataset.tipos || cb.dataset.tipo || '')
      .split(',')
      .map(function (tipo) { return tipo.trim().toLowerCase(); })
      .filter(Boolean);

    tipos.forEach(function (tipo) {
      if (Object.prototype.hasOwnProperty.call(buckets, tipo)) {
        buckets[tipo] += 1;
      }
    });
  });

  const rawProbTotal = (buckets.preventivo + buckets.detectivo) * CONTROL_REDUCTION_STEP;
  const rawConsTotal = (buckets.detectivo + buckets.corretivo) * CONTROL_REDUCTION_STEP;
  const breakdown = [];
  const warnings  = [];

  for (const [key, count] of Object.entries(buckets)) {
    if (count === 0) continue;
    const eff = CONTROL_EFFECTIVENESS[key];

    breakdown.push({
      label: eff.label,
      count,
      reduces_prob: eff.reduces_prob,
      reduces_cons: eff.reduces_cons,
      prob_contribution: eff.reduces_prob ? count * CONTROL_REDUCTION_STEP : 0,
      cons_contribution: eff.reduces_cons ? count * CONTROL_REDUCTION_STEP : 0,
    });
  }

  if (rawProbTotal > MAX_REDUCTION) warnings.push(`Redução total de probabilidade limitada a ${MAX_REDUCTION}%.`);
  if (rawConsTotal > MAX_REDUCTION) warnings.push(`Redução total de consequência limitada a ${MAX_REDUCTION}%.`);

  const finalProb = Math.min(rawProbTotal, MAX_REDUCTION);
  const finalCons = Math.min(rawConsTotal, MAX_REDUCTION);

  renderControlBreakdown(breakdown, finalProb, finalCons, warnings);

  // Apply to inputs and refresh preview
  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const consInput = document.querySelector('input[name="reducao_impacto"]');

  if (probInput) {
    probInput.value = finalProb;
    probInput.dispatchEvent(new Event('input', { bubbles: true }));
  }
  if (consInput) {
    consInput.value = finalCons;
    consInput.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

function renderControlBreakdown(breakdown, probTotal, consTotal, warnings) {
  const wrapper = document.getElementById('control-breakdown');
  const body    = document.getElementById('cbd-body');
  const probEl  = document.getElementById('cbd-prob-total');
  const consEl  = document.getElementById('cbd-cons-total');
  const warnEl  = document.getElementById('cbd-warnings');

  if (!wrapper) return;

  if (breakdown.length === 0) {
    wrapper.style.display = 'none';
    if (body) body.innerHTML = '';
    if (probEl) probEl.textContent = '0%';
    if (consEl) consEl.textContent = '0%';
    if (warnEl) {
      warnEl.innerHTML = '';
      warnEl.style.display = 'none';
    }
    return;
  }

  wrapper.style.display = '';

  if (body) {
    body.innerHTML = breakdown.map(function (item) {
      const probEffect = item.reduces_prob
        ? `<span class="cbd-effect effect-prob">↓ Prob +${item.prob_contribution}%</span>`
        : `<span class="cbd-effect effect-no">Prob —</span>`;
      const consEffect = item.reduces_cons
        ? `<span class="cbd-effect effect-cons">↓ Cons +${item.cons_contribution}%</span>`
        : `<span class="cbd-effect effect-no">Cons —</span>`;

      return `
        <div class="cbd-row">
          <div class="cbd-row-type">
            <strong>${item.label}</strong>
            <span class="cbd-row-qty">${item.count} controle${item.count !== 1 ? 's' : ''}</span>
          </div>
          <div class="cbd-row-effects">${probEffect}${consEffect}</div>
          <div class="cbd-row-example"></div>
        </div>`;
    }).join('');
  }

  if (probEl) probEl.textContent = `${probTotal}%`;
  if (consEl) consEl.textContent = `${consTotal}%`;

  if (warnEl) {
    warnEl.innerHTML = warnings.map(function (w) {
      return `<div class="cbd-warning">⚠ ${w}</div>`;
    }).join('');
    warnEl.style.display = warnings.length ? '' : 'none';
  }
}

/*STRATEGY SELECTION */

function initStrategySelection() {
  const radios = document.querySelectorAll('input[name="tipo_tratamento"]');

  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      recalculateControlReductions();
    });
  });
}

/*RESIDUAL RISK PREVIEW */

function initReductionInputListeners() {
  ['reducao_probabilidade', 'reducao_impacto'].forEach(function (name) {
    const input = document.querySelector(`input[name="${name}"]`);
    if (input) {
      input.addEventListener('input',  updateResidualRiskPreview);
      input.addEventListener('change', updateResidualRiskPreview);
    }
  });
}

function triggerInitialPreview() {
  setTimeout(updateResidualRiskPreview, 150);
}

/**
 * Read weights safely from data-* attributes on the form element.
 * Falls back to sensible defaults so the preview never crashes.
 */
function getRiskWeights() {
  const form = document.querySelector('form[data-prob-weight]');
  if (!form) return { probWeight: 3, consWeight: 4, currentValue: 12, acceptanceLevel: 12 };

  return {
    probWeight:      parseFloat(form.dataset.probWeight)      || 3,
    consWeight:      parseFloat(form.dataset.consWeight)      || 4,
    currentValue:    parseFloat(form.dataset.currentValue)    || 12,
    acceptanceLevel: parseFloat(form.dataset.acceptanceLevel) || 12,
  };
}

function updateResidualRiskPreview() {
  const container = document.getElementById('residual-preview');
  if (!container) return;

  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const consInput = document.querySelector('input[name="reducao_impacto"]');
  if (!probInput || !consInput) return;

  const reducaoProb = Math.min(parseFloat(probInput.value) || 0, MAX_REDUCTION);
  const reducaoCons = Math.min(parseFloat(consInput.value) || 0, MAX_REDUCTION);

  const { probWeight, consWeight, currentValue, acceptanceLevel } = getRiskWeights();

  const residualProb = probWeight * (1 - reducaoProb / 100);
  const residualCons = consWeight * (1 - reducaoCons / 100);
  const residualValue = residualProb * residualCons;

  const currentLevel  = classifyRisk(currentValue);
  const residualLevel = classifyRisk(residualValue);
  const reductionPct  = currentValue > 0 ? ((1 - residualValue / currentValue) * 100) : 0;
  const isAcceptable  = residualValue < acceptanceLevel;

  container.innerHTML = buildPreviewHTML(
    currentValue, currentLevel,
    residualValue, residualLevel,
    reductionPct, isAcceptable, acceptanceLevel,
    probWeight, consWeight,
    residualProb, residualCons
  );
}

function classifyRisk(value) {
  if (value <= 3)  return { name: 'Muito Baixo', color: '#10b981', cls: 'nivel-baixo' };
  if (value <= 6)  return { name: 'Baixo',       color: '#34d399', cls: 'nivel-baixo' };
  if (value <= 12) return { name: 'Médio',        color: '#f59e0b', cls: 'nivel-medio' };
  if (value <= 20) return { name: 'Alto',         color: '#f97316', cls: 'nivel-alto' };
  return               { name: 'Crítico',         color: '#ef4444', cls: 'nivel-critico' };
}

function buildPreviewHTML(
  currentValue, currentLevel,
  residualValue, residualLevel,
  reductionPct, isAcceptable, acceptanceLevel,
  probWeight, consWeight,
  residualProb, residualCons
) {
  const acceptanceBadge = isAcceptable
    ? `<span class="badge badge-success">✓ Aceitável após tratamento</span>`
    : `<span class="badge badge-danger">✕ Ainda acima do limite (${acceptanceLevel})</span>`;

  const matrixHTML = buildMatrixHTML(
    probWeight,
    consWeight,
    residualProb,
    residualCons
  );

  return `
    <div class="preview-grid">
      <div class="preview-summary">
        <div class="preview-summary-block">
          <span class="psb-label">📊 Risco Atual</span>
          <span class="psb-value" style="color:${currentLevel.color}">${currentValue.toFixed(1)}</span>
          <span class="psb-level" style="color:${currentLevel.color}">${currentLevel.name}</span>
        </div>

        <div class="preview-summary-block">
          <span class="psb-label">🎯 Risco Residual Projetado</span>
          <span class="psb-value" style="color:${residualLevel.color}">${residualValue.toFixed(1)}</span>
          <span class="psb-level" style="color:${residualLevel.color}">${residualLevel.name}</span>
          <div class="psb-acceptance">${acceptanceBadge}</div>
        </div>

        <div class="preview-summary-block">
          <span class="psb-label">✓ Redução Estimada</span>
          <span class="psb-reduction">${reductionPct.toFixed(0)}%</span>
          <div class="psb-note">
            Com os controles propostos, o risco passará de
            <strong>${currentValue.toFixed(1)}</strong> para
            <strong>${residualValue.toFixed(1)}</strong>.
          </div>
        </div>
      </div>

      <div class="matrix-wrap">
        <div class="matrix-title">Matriz de Risco 5×5</div>
        ${matrixHTML}
        <div class="matrix-legend">
          <div class="legend-item"><span style="font-size:1.1rem">●</span> Risco Atual</div>
          <div class="legend-item"><span style="font-size:1.1rem">■</span> Risco Residual</div>
        </div>
      </div>
    </div>`;
}

function buildMatrixHTML(currentProb, currentCons, residualProb, residualCons) {
  const curCell = {
    prob: Math.max(1, Math.min(5, Math.round(currentProb))),
    impact: Math.max(1, Math.min(5, Math.round(currentCons)))
  };

  const resCell = {
    prob: Math.max(1, Math.min(5, Math.round(residualProb))),
    impact: Math.max(1, Math.min(5, Math.round(residualCons)))
  };

  const sameCell = (curCell.prob === resCell.prob && curCell.impact === resCell.impact);

  let cells = '';
  for (let impact = 5; impact >= 1; impact--) {
    for (let prob = 1; prob <= 5; prob++) {
      const cellValue = impact * prob;
      const { color } = classifyRisk(cellValue);
      const isCurrent  = prob === curCell.prob  && impact === curCell.impact;
      const isResidual = prob === resCell.prob && impact === resCell.impact;
      const opacity    = (isCurrent || isResidual) ? 0.95 : 0.35;

      let symbol = '';
      if (sameCell && isCurrent) {
        symbol = '<div style="font-size:1.2rem;font-weight:900;line-height:1">●■</div>';
      } else if (isCurrent) {
        symbol = '<div style="font-size:1.4rem;line-height:1">●</div>';
      } else if (isResidual) {
        symbol = '<div style="font-size:1.2rem;line-height:1">■</div>';
      }

      cells += `
        <div class="matrix-cell" style="background-color:${color};opacity:${opacity}">
          ${symbol}
          <span class="matrix-cell-val">${cellValue}</span>
        </div>`;
    }
  }

  return `<div class="matrix-grid">${cells}</div>`;
}

/*FORM VALIDATION */

function initFormValidation() {
  const form = document.querySelector('form[data-prob-weight]');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    const missing = [];

    // Read values from the form payload itself so validation stays correct
    // even if widgets or element types change.
    const data = new FormData(form);

    const nome = String(data.get('nome') || '').trim();
    if (!nome) missing.push('Nome do Plano');

    const tipoTratamento = String(data.get('tipo_tratamento') || '').trim();
    if (!tipoTratamento) missing.push('Estratégia de Tratamento');

    const descricao = String(data.get('descricao') || '').trim();
    if (!descricao) missing.push('Descrição');

    const prob = String(data.get('reducao_probabilidade') ?? '').trim();
    if (prob === '') missing.push('Redução de Probabilidade');

    const cons = String(data.get('reducao_impacto') ?? '').trim();
    if (cons === '') missing.push('Redução de Impacto');

    if (missing.length > 0) {
      e.preventDefault();
      showValidationBanner('Por favor, preencha os campos obrigatórios: ' + missing.join(', ') + '.');
    }
  });
}

function showValidationBanner(message) {
  const existing = document.getElementById('validation-banner');
  if (existing) existing.remove();

  const banner = document.createElement('div');
  banner.id        = 'validation-banner';
  banner.className = 'alert alert-error';
  banner.style.cssText = 'margin-bottom:1rem;animation:fadeIn .2s ease;';
  banner.textContent   = message;

  const buttons = document.querySelector('.button-group');
  if (buttons) {
    buttons.parentElement.insertBefore(banner, buttons);
    banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  setTimeout(() => banner.remove(), 6000);
}