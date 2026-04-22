document.addEventListener('DOMContentLoaded', function() {
  initializeAmeacasSelect2();
});

function initializeAmeacasSelect2() {
  const ameacasSelect = document.getElementById('id_ameacas');

  if (!ameacasSelect || typeof jQuery === 'undefined' || !jQuery.fn.select2) {
    return;
  }

  jQuery(ameacasSelect).select2({
    placeholder: 'Buscar e selecionar ameacas...',
    allowClear: true,
    width: '100%',
    language: 'pt-BR',
    matcher: matchCustom,
    templateResult: formatAmeacaOption,
    templateSelection: formatAmeacaSelection,
    closeOnSelect: false,
    escapeMarkup: function(markup) { return markup; }
  });

  jQuery(ameacasSelect).on('select2:select select2:unselect', function() {
    updateCheckboxStates();
  });

  jQuery(ameacasSelect).on('select2:opening', function() {
    setTimeout(updateCheckboxStates, 50);
  });

  const legacyFilter = document.querySelector('[data-target-select="ameacas"]');
  if (legacyFilter) {
    legacyFilter.style.display = 'none';
  }
}

function matchCustom(params, data) {
  if (jQuery.trim(params.term) === '') {
    return data;
  }

  if (typeof data.text === 'undefined') {
    return null;
  }

  if (data.text.toUpperCase().indexOf(params.term.toUpperCase()) > -1) {
    return jQuery.extend({}, data, true);
  }

  return null;
}

function updateCheckboxStates() {
  const selectedValues = jQuery('#id_ameacas').val() || [];

  jQuery('.select2-results__option').each(function() {
    const optionElement = jQuery(this);
    const resultData = optionElement.data('data');

    if (!resultData || !resultData.id) {
      return;
    }

    const isSelected = selectedValues.includes(resultData.id.toString());
    optionElement.find('input[type="checkbox"]').prop('checked', isSelected);
  });
}

function formatAmeacaOption(option) {
  if (!option.id) {
    return option.text;
  }

  const selectedValues = jQuery('#id_ameacas').val() || [];
  const isSelected = selectedValues.includes(option.id.toString());
  const checkboxHTML = '<input type="checkbox" ' +
    (isSelected ? 'checked' : '') +
    ' class="control-checkbox" style="margin-right: 10px; cursor: pointer; width: 18px; height: 18px; vertical-align: middle;">';

  return '<span style="display: flex; align-items: center;">' + checkboxHTML + '<span>' + option.text + '</span></span>';
}

function formatAmeacaSelection(option) {
  if (!option.id) {
    return option.text;
  }

  return option.text;
}
