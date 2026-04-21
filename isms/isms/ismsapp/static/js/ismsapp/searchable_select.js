document.addEventListener('DOMContentLoaded', function() {
  const searchInputs = document.querySelectorAll('[data-target-select]');

  searchInputs.forEach((input) => {
    const targetName = input.getAttribute('data-target-select');
    const select = document.querySelector(`[name="${targetName}"]`);

    if (!select) {
      return;
    }

    const filterOptions = () => {
      const query = input.value.trim().toLowerCase();

      Array.from(select.options).forEach((option, index) => {
        if (index === 0 && option.value === '') {
          option.hidden = false;
          return;
        }

        option.hidden = Boolean(query) && !option.textContent.toLowerCase().includes(query);
      });
    };

    input.addEventListener('input', filterOptions);
  });
});
