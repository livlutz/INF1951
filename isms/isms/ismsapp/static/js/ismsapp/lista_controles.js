document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('search');
  const filterForm = document.querySelector('.filter-form');
  const deleteModal = document.getElementById('delete-modal');
  const deleteModalText = document.getElementById('delete-modal-text');
  const deleteConfirmForm = document.getElementById('delete-confirm-form');
  const deleteTriggers = document.querySelectorAll('.js-delete-trigger');
  const deleteCancelButtons = document.querySelectorAll('[data-delete-cancel]');

  if (searchInput && filterForm) {
    let debounceTimer;
    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = window.setTimeout(function () {
        filterForm.requestSubmit ? filterForm.requestSubmit() : filterForm.submit();
      }, 300);
    });
  }

  if (deleteModal && deleteConfirmForm && deleteModalText) {
    const openModal = function (action, name) {
      deleteConfirmForm.action = action;
      deleteModalText.textContent = name ? `Tem certeza que deseja excluir "${name}"?` : 'Tem certeza que deseja excluir este controle?';
      deleteModal.classList.add('open');
      deleteModal.setAttribute('aria-hidden', 'false');
    };

    const closeModal = function () {
      deleteModal.classList.remove('open');
      deleteModal.setAttribute('aria-hidden', 'true');
      deleteConfirmForm.action = '';
    };

    deleteTriggers.forEach(function (trigger) {
      trigger.addEventListener('click', function () {
        openModal(trigger.dataset.deleteUrl, trigger.dataset.deleteName);
      });
    });

    deleteCancelButtons.forEach(function (button) {
      button.addEventListener('click', closeModal);
    });

    deleteModal.addEventListener('click', function (event) {
      if (event.target === deleteModal) {
        closeModal();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && deleteModal.classList.contains('open')) {
        closeModal();
      }
    });
  }
});
