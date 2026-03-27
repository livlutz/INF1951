// ── Num buttons (prob & cons) ─────────────────────────────────────────
['prob', 'cons'].forEach(function(group) {
  const btns  = document.querySelectorAll(`[data-group="${group}"]`);
  const input = document.getElementById(`input-${group}`);

  btns.forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      input.value = btn.dataset.value;
      updateRiskValue();
      highlightCell();
    });
  });
});

// ── Highlight selected cell ───────────────────────────────────────────
function highlightCell() {
  const p = document.getElementById('input-prob').value;
  const c = document.getElementById('input-cons').value;

  document.querySelectorAll('#risk-matrix .cell').forEach(function(cell) {
    cell.classList.remove('highlight');
  });

  if (p && c) {
    const target = document.querySelector(
      `#risk-matrix .cell[data-p="${p}"][data-c="${c}"]`
    );
    if (target) {
      target.classList.add('highlight');
    }
  }
}

// ── Update risk value display ─────────────────────────────────────────
function updateRiskValue() {
  const p = parseInt(document.getElementById('input-prob').value) || 0;
  const c = parseInt(document.getElementById('input-cons').value) || 0;
  const riskValue = p * c;

  // Update the displayed value
  const riskValueElement = document.getElementById('risk-value');
  const riskLevelElement = document.getElementById('risk-level');

  riskValueElement.textContent = riskValue;

  // Determine risk level label and color based on value
  let riskLevel = 'SEM RISCO';
  let color = '#10b981'; // Green by default

  if (riskValue <= 0) {
    riskLevel = 'SEM RISCO';
    color = '#6b7280';
  } else if (riskValue <= 5) {
    riskLevel = 'IMPACTO BAIXO';
    color = '#10b981'; // Green
  } else if (riskValue <= 10) {
    riskLevel = 'IMPACTO MODERADO';
    color = '#f59e0b'; // Orange
  } else if (riskValue <= 15) {
    riskLevel = 'IMPACTO ALTO';
    color = '#ef4444'; // Red
  } else {
    riskLevel = 'IMPACTO CRÍTICO';
    color = '#7f1d1d'; // Dark Red
  }

  riskLevelElement.textContent = riskLevel;

  // Update colors
  riskValueElement.style.color = color;
  riskLevelElement.style.color = color;
}

// Initialize on page load
highlightCell();
updateRiskValue();
