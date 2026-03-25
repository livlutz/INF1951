// ── Num buttons (prob & cons) ─────────────────────────────────────────
['prob', 'cons'].forEach(function(group) {
  const btns  = document.querySelectorAll(`[data-group="${group}"]`);
  const input = document.getElementById(`input-${group}`);

  btns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      input.value = btn.dataset.value;
      highlightCell();
    });
  });
});

// ── Appetite buttons ──────────────────────────────────────────────────
document.querySelectorAll('.appetite-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.appetite-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('input-apetite').value = btn.dataset.appetite;
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
    if (target) target.classList.add('highlight');
  }
}

highlightCell(); // init on load

