function switchTab(event, tabName) {
  if (event) {
    event.preventDefault();
  }

  document.querySelectorAll('.tab-content').forEach(function (tab) {
    tab.classList.remove('active');
  });

  document.querySelectorAll('.tab-button').forEach(function (button) {
    button.classList.remove('active');
  });

  const selectedTab = document.getElementById(tabName);
  if (selectedTab) {
    selectedTab.classList.add('active');
  }

  const trigger = event && event.currentTarget ? event.currentTarget : null;
  if (trigger) {
    trigger.classList.add('active');
  }
}
