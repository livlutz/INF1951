/**
 * Tratamento de Riscos JavaScript
 *
 * Handles interactive features for risk treatment planning and residual risk visualization.
 * This module implements ISO 27001 risk treatment strategies with real-time matrix preview.
 *
 * Features:
 * - Strategy-based intelligent defaults for risk reduction percentages
 * - Manual adjustment of reduction values with live residual risk preview
 * - Visual risk matrix showing current vs. residual risk positions
 * - Risk level classification (Muito Baixo, Baixo, Médio, Alto, Crítico)
 *
 * Risk Calculation:
 * - Current Risk = Probability Weight × Consequence Weight
 * - Residual Risk = (Prob Weight × (1 - Prob Reduction%)) × (Cons Weight × (1 - Impact Reduction%))
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeRiskReductionPreview();
  initializeStrategySelection();
  initializeRiskSelection();
  initializeFormValidation();
});

/**
 * Treatment strategy effectiveness mapping (ISO 27001 Risk Treatment)
 *
 * Each strategy has suggested reduction percentages for probability and impact.
 * These values represent typical effectiveness ranges for each treatment approach.
 * Users can adjust these values based on their specific control implementation.
 *
 * Strategies:
 * - MITIGAR (Mitigate): Implement controls to reduce probability or impact
 *   Example: Install antivirus, implement access controls, employee training
 *   Suggested: 40% probability reduction + 30% impact reduction
 *
 * - EVITAR (Avoid): Eliminate the activity or condition that creates the risk
 *   Example: Stop using vulnerable technology, discontinue risky process
 *   Suggested: 80% probability reduction + 70% impact reduction (highest effectiveness)
 *
 * - COMPARTILHAR (Share): Transfer risk to third party (insurance, outsourcing)
 *   Example: Buy cyber insurance, outsource to managed security provider
 *   Suggested: 30% probability reduction + 50% impact reduction (handles impact better)
 *
 * - ACEITAR (Accept): Accept the risk without additional treatment
 *   Example: Accept low-value risks, document risk acceptance
 *   Suggested: 0% reduction (no controls applied)
 */
const strategyReductions = {
  'mitigar': { probabilidade: 40, impacto: 30 },    // Mitigate: implement controls (moderate effectiveness)
  'evitar': { probabilidade: 80, impacto: 70 },      // Avoid: eliminate activity (highest effectiveness)
  'compartilhar': { probabilidade: 30, impacto: 50 }, // Share: transfer to third party (risk transfer)
  'aceitar': { probabilidade: 0, impacto: 0 }        // Accept: accept residual risk (no reduction)
};

/**
 * Initialize strategy selection with visual feedback
 */
function initializeStrategySelection() {
  const radioButtons = document.querySelectorAll('input[name="tipo_tratamento"]');

  radioButtons.forEach(radio => {
    radio.addEventListener('change', function() {
      const strategy = this.value;
      console.log('Treatment strategy selected:', strategy);

      // Set suggested reduction values based on strategy
      applyStrategyReductions(strategy);

      // Update the preview
      updateResidualRiskPreview();
    });
  });
}

/**
 * Apply suggested reduction percentages based on treatment strategy
 */
function applyStrategyReductions(strategy) {
  const reductions = strategyReductions[strategy];
  if (!reductions) return;

  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const impactInput = document.querySelector('input[name="reducao_impacto"]');

  if (probInput) {
    probInput.value = reductions.probabilidade;
  }
  if (impactInput) {
    impactInput.value = reductions.impacto;
  }

  console.log(`Strategy "${strategy}" applied - Prob: ${reductions.probabilidade}%, Impact: ${reductions.impacto}%`);
}

/**
 * Update residual risk preview when reduction values change
 */
function initializeRiskReductionPreview() {
  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const impactInput = document.querySelector('input[name="reducao_impacto"]');

  if (probInput && impactInput) {
    probInput.addEventListener('input', updateResidualRiskPreview);
    impactInput.addEventListener('input', updateResidualRiskPreview);

    // Trigger initial update with default values
    setTimeout(updateResidualRiskPreview, 100);
  }
}

/**
 * Initialize risk selection from list
 */
function initializeRiskSelection() {
  const riskItems = document.querySelectorAll('.risk-treatment-item');

  riskItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const url = this.getAttribute('href');
      if (url) {
        window.location.href = url;
      }
    });
  });
}

/**
 * Update the residual risk preview based on reduction inputs
 * Displays a risk matrix with current and projected residual risk positions
 */
function updateResidualRiskPreview() {
  const previewContent = document.getElementById('residual-preview');

  if (!previewContent) {
    console.error('Preview element not found');
    return;
  }

  const probInput = document.querySelector('input[name="reducao_probabilidade"]');
  const impactInput = document.querySelector('input[name="reducao_impacto"]');

  if (!probInput || !impactInput) {
    console.error('Reduction input fields not found');
    return;
  }

  const reducaoProbabilidade = parseInt(probInput.value, 10) || 0;
  const reducaoImpacto = parseInt(impactInput.value, 10) || 0;

  // Get current risk value from the impact value span
  let currentRiskValue = 12; // default fallback
  const impactValue = document.querySelector('.impact-value');
  if (impactValue && impactValue.textContent) {
    const riskText = impactValue.textContent.trim();
    const riskNum = parseFloat(riskText);
    if (!isNaN(riskNum)) {
      currentRiskValue = riskNum;
    }
  }

  // Extract probability and consequence weights from the risk overview card
  let probWeight = 3;
  let consWeight = 4;

  const riskOverviewCard = document.querySelector('.risk-overview-card');
  if (riskOverviewCard) {
    // Get all info items
    const infoItems = riskOverviewCard.querySelectorAll('.info-item');

    infoItems.forEach(item => {
      const label = item.querySelector('.label');
      const value = item.querySelector('.value');

      if (label && value) {
        const labelText = label.textContent.trim();
        const valueText = value.textContent.trim();

        // Extract probability weight
        if (labelText.includes('Probabilidade')) {
          const probMatch = valueText.match(/peso:\s*([\d.]+)/);
          if (probMatch) {
            probWeight = parseFloat(probMatch[1]);
          }
        }

        // Extract consequence weight
        if (labelText.includes('Consequência')) {
          const consMatch = valueText.match(/peso:\s*([\d.]+)/);
          if (consMatch) {
            consWeight = parseFloat(consMatch[1]);
          }
        }
      }
    });
  }

  console.log('Current Risk Value:', currentRiskValue, 'Weights extracted - Prob:', probWeight, 'Cons:', consWeight);

  // Calculate residual weights
  const residualProbWeight = probWeight * (1 - reducaoProbabilidade / 100);
  const residualConsWeight = consWeight * (1 - reducaoImpacto / 100);
  const residualRiskValue = residualProbWeight * residualConsWeight;

  console.log('Risk calculations - Current:', currentRiskValue, 'Residual:', residualRiskValue);

  // Determine risk levels
  const currentLevel = getRiskLevel(currentRiskValue);
  const residualLevel = getRiskLevel(residualRiskValue);

  // Create risk matrix visualization
  const matrixHTML = createRiskMatrixVisualization(
    probWeight, consWeight, currentRiskValue,
    residualProbWeight, residualConsWeight, residualRiskValue,
    currentLevel, residualLevel
  );

  previewContent.innerHTML = matrixHTML;
}

/**
 * Determine risk level based on value
 */
function getRiskLevel(value) {
  if (value <= 3) {
    return { name: 'Muito Baixo', color: '#10b981', severity: 1, symbol: '●' };
  } else if (value <= 6) {
    return { name: 'Baixo', color: '#34d399', severity: 2, symbol: '●' };
  } else if (value <= 12) {
    return { name: 'Médio', color: '#f59e0b', severity: 3, symbol: '■' };
  } else if (value <= 20) {
    return { name: 'Alto', color: '#ef4444', severity: 4, symbol: '■' };
  } else {
    return { name: 'Crítico', color: '#dc2626', severity: 5, symbol: '■' };
  }
}

/**
 * Create a visual risk matrix showing current and residual positions
 */
function createRiskMatrixVisualization(
  currentProbWeight, currentConsWeight, currentValue,
  residualProbWeight, residualConsWeight, residualValue,
  currentLevel, residualLevel
) {
  // Find the cell closest to current and residual risk values
  let currentClosestCell = null;
  let residualClosestCell = null;
  let minCurrentDiff = Infinity;
  let minResidualDiff = Infinity;

  for (let impact = 1; impact <= 5; impact++) {
    for (let prob = 1; prob <= 5; prob++) {
      const cellValue = impact * prob;

      // Find closest cell to current risk value
      const currentDiff = Math.abs(cellValue - currentValue);
      if (currentDiff < minCurrentDiff) {
        minCurrentDiff = currentDiff;
        currentClosestCell = { prob, impact, value: cellValue };
      }

      // Find closest cell to residual risk value
      const residualDiff = Math.abs(cellValue - residualValue);
      if (residualDiff < minResidualDiff) {
        minResidualDiff = residualDiff;
        residualClosestCell = { prob, impact, value: cellValue };
      }
    }
  }

  console.log('Matrix positions - Current:', currentClosestCell, 'Residual:', residualClosestCell);

  // Create matrix cells
  let matrixCells = '';

  for (let impact = 5; impact >= 1; impact--) {
    for (let prob = 1; prob <= 5; prob++) {
      const cellValue = impact * prob;
      const cellLevel = getRiskLevel(cellValue);
      const cellColor = cellLevel.color;

      let symbol = '';
      let backgroundColor = cellColor;
      let opacity = 0.4;

      // Check if this is current position
      const isCurrent = prob === currentClosestCell.prob && impact === currentClosestCell.impact;
      // Check if this is residual position
      const isResidual = prob === residualClosestCell.prob && impact === residualClosestCell.impact;

      if (isCurrent) {
        symbol = '●';
        opacity = 0.9;
      } else if (isResidual) {
        symbol = '■';
        opacity = 0.9;
      }

      matrixCells += `
        <div style="
          background-color: ${backgroundColor};
          opacity: ${opacity};
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: #fff;
          position: relative;
          min-height: 60px;
          min-width: 60px;
          border-radius: 4px;
          border: 2px solid transparent;
          transition: all 0.3s ease;
          cursor: pointer;
        ">
          ${symbol ? `<div style="font-size: 1.8rem; margin-bottom: 4px;">${symbol}</div>` : ''}
          <span style="font-size: 0.75rem; opacity: 0.9; font-weight: normal;">${cellValue}</span>
        </div>
      `;
    }
  }

  return `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; width: 100%; margin-top: 1rem;">
      <!-- Risk Matrix -->
      <div>
        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; margin-bottom: 1rem;">Matriz de Risco 5×5</div>
        <div style="
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 6px;
          background-color: #ffffff10;
          padding: 1.5rem;
          border-radius: 6px;
          border: 1px solid #2a3f5f;
        ">
          ${matrixCells}
        </div>
        <div style="margin-top: 1.5rem; font-size: 0.8rem; color: #cbd5e1; background-color: #1a1f2e; padding: 1rem; border-radius: 6px; border-left: 4px solid #8b3cf7;">
          <strong>Legenda da Matriz:</strong>
          <div style="margin-top: 0.75rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="font-size: 1.4rem;">●</span> Risco Atual
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="font-size: 1.4rem;">■</span> Risco Residual
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Summary -->
      <div style="display: flex; flex-direction: column; justify-content: flex-start;">
        <div style="background-color: #1a1f2e; border: 1px solid #2a3f5f; border-radius: 6px; padding: 1.5rem;">
          <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; margin-bottom: 0.5rem;">📊 Risco Atual</div>
            <div style="display: flex; align-items: baseline; gap: 0.75rem;">
              <div style="font-size: 2.5rem; font-weight: 700; color: ${currentLevel.color};">${currentValue.toFixed(1)}</div>
              <div style="font-size: 0.95rem; font-weight: 600; color: ${currentLevel.color};">${currentLevel.name}</div>
            </div>
          </div>

          <div style="margin-bottom: 1.5rem; padding-top: 1rem; border-top: 1px solid #2a3f5f;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; margin-bottom: 0.5rem;">🎯 Risco Residual Projetado</div>
            <div style="display: flex; align-items: baseline; gap: 0.75rem;">
              <div style="font-size: 2.5rem; font-weight: 700; color: ${residualLevel.color};">${residualValue.toFixed(1)}</div>
              <div style="font-size: 0.95rem; font-weight: 600; color: ${residualLevel.color};">${residualLevel.name}</div>
            </div>
          </div>

          <div style="padding-top: 1rem; border-top: 1px solid #2a3f5f;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; margin-bottom: 0.75rem;">✓ Redução Esperada</div>
            <div style="font-size: 2rem; font-weight: 700; color: #10b981;">${((1 - residualValue / currentValue) * 100).toFixed(0)}%</div>
            <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 1rem; background-color: #0e1019; padding: 0.75rem; border-radius: 4px; border-left: 3px solid #10b981;">
              Com os controles propostos, você reduzirá o risco de <strong>${currentValue.toFixed(1)}</strong> para <strong>${residualValue.toFixed(1)}</strong>.
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
  const form = document.querySelector('form');

  if (form) {
    form.addEventListener('submit', function(e) {
      const nome = this.querySelector('input[name="nome"]');
      const tipoTratamento = this.querySelector('input[name="tipo_tratamento"]:checked');
      const descricao = this.querySelector('textarea[name="descricao"]');
      const reducaoProbabilidade = this.querySelector('input[name="reducao_probabilidade"]');
      const reducaoImpacto = this.querySelector('input[name="reducao_impacto"]');

      const nomeValid = nome && nome.value && nome.value.trim().length > 0;
      const tipoValid = tipoTratamento !== null;
      const descricaoValid = descricao && descricao.value && descricao.value.trim().length > 0;
      const reducaoProbabilidadeValid = reducaoProbabilidade && reducaoProbabilidade.value !== '';
      const reducaoImpactoValid = reducaoImpacto && reducaoImpacto.value !== '';

      if (!nomeValid || !tipoValid || !descricaoValid || !reducaoProbabilidadeValid || !reducaoImpactoValid) {
        e.preventDefault();

        // Show specific error message
        let missingFields = [];
        if (!nomeValid) missingFields.push('Nome do Plano');
        if (!tipoValid) missingFields.push('Estratégia de Tratamento');
        if (!descricaoValid) missingFields.push('Descrição');
        if (!reducaoProbabilidadeValid) missingFields.push('Redução de Probabilidade');
        if (!reducaoImpactoValid) missingFields.push('Redução de Impacto');

        alert('Por favor, preencha os campos obrigatórios:\n- ' + missingFields.join('\n- '));
        return false;
      }

      return true;
    });
  }
}

/**
 * Get treatment strategy label
 */
function getStrategyLabel(strategy) {
  const labels = {
    'mitigar': 'Mitigar (Modificar)',
    'evitar': 'Evitar',
    'compartilhar': 'Compartilhar',
    'aceitar': 'Aceitar'
  };
  return labels[strategy] || 'Desconhecido';
}

/**
 * Format percentage value for display
 */
function formatPercentage(value) {
  return Math.round(value) + '%';
}

/**
 * Export treatment plan summary
 */
function exportTreatmentPlan() {
  const riskName = document.querySelector('.risk-overview-title')?.textContent || 'Risk';
  const strategy = document.querySelector('input[name="tipo_tratamento"]:checked')?.value || 'Not selected';
  const description = document.querySelector('textarea[name="descricao"]')?.value || '';
  const responsible = document.querySelector('input[name="responsavel"]')?.value || '';

  const data = {
    riskName: riskName,
    strategy: getStrategyLabel(strategy),
    description: description,
    responsible: responsible,
    timestamp: new Date().toISOString()
  };

  console.log('Treatment Plan Data:', data);
  return data;
}

/**
 * Print treatment plan report
 */
function printTreatmentPlan() {
  window.print();
}

/**
 * Reset form to initial state
 */
function resetTreatmentForm() {
  const form = document.querySelector('form');
  if (form) {
    form.reset();
    updateResidualRiskPreview();
  }
}

