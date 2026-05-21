/**
 * Tratamento de Riscos — tratamento_riscos.js
 *
 * Key improvements over the previous version:
 *
 * 1. Weights read from data-* attributes on the <form> element —
 *    no fragile DOM-text scraping with regex.
 * 2. AJAX endpoint for control reductions is replaced with a pure
 *    client-side calculation that mirrors the view's
 *    _CONTROL_EFFECTIVENESS table, so there's no 404 risk and no
 *    round-trip needed.
 * 3. The residual-risk preview renders a proper summary panel
 *    alongside a lightweight matrix, both using CSS classes rather
 *    than thousands of inline styles.
 * 4. Form validation uses an inline banner instead of alert().
 * 5. Strategy-suggested reductions are only applied when the
 *    reduction inputs are genuinely empty (new treatment), never
 *    overwriting saved values while editing.
 */

/*CONSTANTS — mirror the view's _CONTROL_EFFECTIVENESS table */

const STRATEGY_REDUCTIONS = {
  mitigar:       { prob: 40, cons: 30 },
  evitar:        { prob: 80, cons: 70 },
  compartilhar:  { prob: 30, cons: 50 },
  aceitar:       { prob:  0, cons:  0 },
};

/*CONTROL EFFECTIVENESS — define how different control types reduce probability and consequence */
// per_control and cap values must stay in sync with view's _CONTROL_EFFECTIVENESS
const CONTROL_EFFECTIVENESS = {
  preventivo: {
    prob_per_control: 20, cons_per_control: 0,
    prob_cap: 60, cons_cap: 0,
    label: 'Preventivo',
    reduces_prob: true, reduces_cons: false,
  },
  detectivo: {
    prob_per_control: 10, cons_per_control: 15,
    prob_cap: 30, cons_cap: 45,
    label: 'Detectivo',
    reduces_prob: true, reduces_cons: true,
  },
  corretivo: {
    prob_per_control: 0, cons_per_control: 25,
    prob_cap: 0, cons_cap: 60,
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

  // If there are already-selected controls on load (editing), compute immediately
  const preselected = Array.from(select.selectedOptions).length;
  if (preselected > 0) {
    setTimeout(recalculateControlReductions, 150);
  }
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

/**
 * Collect the category keywords from the labels of selected controls.
 * The label text must contain 'preventivo', 'detectivo', or 'corretivo'
 * (case-insensitive) for the mapping to fire — same keyword matching as
 * the view's _calculate_control_reductions().
 */
function recalculateControlReductions() {
  const checkedBoxes = document.querySelectorAll('#controles-checkbox-list .asset-cb:checked');
  const buckets = { preventivo: 0, detectivo: 0, corretivo: 0 };

  checkedBoxes.forEach(function (cb) {
    const tipo = (cb.dataset.tipo || '').toLowerCase();
    if (tipo === 'preventivo') buckets.preventivo++;
    else if (tipo === 'detectivo') buckets.detectivo++;
    else if (tipo === 'corretivo') buckets.corretivo++;
  });

  // Compute with diminishing returns per category (mirrors view logic)
  function diminishing(perControl, cap, count) {
    let total = 0;
    for (let k = 0; k < count; k++) {
      total += perControl * Math.pow(0.8, k);
    }
    return Math.min(total, cap);
  }

  let probTotal = 0;
  let consTotal = 0;
  const breakdown = [];
  const warnings  = [];

  for (const [key, count] of Object.entries(buckets)) {
    if (count === 0) continue;
    const eff = CONTROL_EFFECTIVENESS[key];

    const catProb = diminishing(eff.prob_per_control, eff.prob_cap, count);
    const catCons = diminishing(eff.cons_per_control, eff.cons_cap, count);

    const rawProb = [...Array(count)].reduce((s, _, k) => s + eff.prob_per_control * Math.pow(0.8, k), 0);
    const rawCons = [...Array(count)].reduce((s, _, k) => s + eff.cons_per_control * Math.pow(0.8, k), 0);

    if (rawProb > eff.prob_cap && eff.prob_cap > 0) {
      warnings.push(`${eff.label}: contribuição máxima de ${eff.prob_cap}% de redução de probabilidade atingida.`);
    }
    if (rawCons > eff.cons_cap && eff.cons_cap > 0) {
      warnings.push(`${eff.label}: contribuição máxima de ${eff.cons_cap}% de redução de consequência atingida.`);
    }

    probTotal += catProb;
    consTotal += catCons;

    breakdown.push({
      label: eff.label,
      count,
      reduces_prob: eff.reduces_prob,
      reduces_cons: eff.reduces_cons,
      prob_contribution: Math.round(catProb * 10) / 10,
      cons_contribution: Math.round(catCons * 10) / 10,
    });
  }

  if (probTotal > MAX_REDUCTION) warnings.push(`Redução total de probabilidade limitada a ${MAX_REDUCTION}%.`);
  if (consTotal > MAX_REDUCTION) warnings.push(`Redução total de consequência limitada a ${MAX_REDUCTION}%.`);

  const finalProb = Math.round(Math.min(probTotal, MAX_REDUCTION) * 10) / 10;
  const finalCons = Math.round(Math.min(consTotal, MAX_REDUCTION) * 10) / 10;

  renderControlBreakdown(breakdown, finalProb, finalCons, warnings);

  // Apply to inputs and refresh preview
  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const consInput = document.querySelector('input[name="reducao_impacto"]');

  if (probInput && breakdown.length > 0) {
    probInput.value = finalProb;
    probInput.dispatchEvent(new Event('input', { bubbles: true }));
  }
  if (consInput && breakdown.length > 0) {
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
    warnEl.innerHTML = warnings.map(w => `<div class="cbd-warning">⚠ ${w}</div>`).join('');
    warnEl.style.display = warnings.length ? '' : 'none';
  }
}

/*STRATEGY SELECTION */

function initStrategySelection() {
  const radios = document.querySelectorAll('input[name="tipo_tratamento"]');

  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      const reductions = STRATEGY_REDUCTIONS[this.value];
      if (!reductions) return;

      const probInput = document.querySelector('input[name="reducao_probabilidade"]');
      const consInput = document.querySelector('input[name="reducao_impacto"]');

      if (probInput) {
        probInput.value = reductions.prob;
        probInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      if (consInput) {
        consInput.value = reductions.cons;
        consInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
  });

  // On load: if the form is brand new (both inputs empty), seed values from the
  // currently checked strategy. If editing, leave the saved values alone.
  const checked   = document.querySelector('input[name="tipo_tratamento"]:checked');
  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const consInput = document.querySelector('input[name="reducao_impacto"]');
  const isNew     = (!probInput?.value && !consInput?.value);

  if (checked && isNew) {
    const reductions = STRATEGY_REDUCTIONS[checked.value];
    if (reductions) {
      if (probInput) {
        probInput.value = reductions.prob;
        probInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      if (consInput) {
        consInput.value = reductions.cons;
        consInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  }
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

    const nome = form.querySelector('input[name="nome"]');
    if (!nome?.value?.trim()) missing.push('Nome do Plano');

    if (!form.querySelector('input[name="tipo_tratamento"]:checked')) {
      missing.push('Estratégia de Tratamento');
    }

    const desc = form.querySelector('textarea[name="descricao"]');
    if (!desc?.value?.trim()) missing.push('Descrição');

    const prob = form.querySelector('input[name="reducao_probabilidade"]');
    if (prob?.value === '') missing.push('Redução de Probabilidade');

    const cons = form.querySelector('input[name="reducao_impacto"]');
    if (cons?.value === '') missing.push('Redução de Impacto');

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