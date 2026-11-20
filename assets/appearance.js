(() => {
  const key = 'confinium-theme';
  const modes = { auto: 'Auto (system)', light: 'Light', dark: 'Dark' };
  const root = document.documentElement;
  const apply = value => {
    root.dataset.theme = Object.hasOwn(modes, value) ? value : 'auto';
  };
  try { apply(localStorage.getItem(key)); }
  catch { apply('auto'); }

  document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('.site-nav');
    if (!nav) return;
    const label = document.createElement('label');
    label.className = 'theme-control';
    label.textContent = 'Appearance';
    const select = document.createElement('select');
    for (const [value, text] of Object.entries(modes)) {
      select.add(new Option(text, value));
    }
    select.value = root.dataset.theme;
    label.append(select);
    nav.append(label);
    select.addEventListener('change', () => {
      apply(select.value);
      try { localStorage.setItem(key, select.value); }
      catch { /* The current page still works when storage is disabled. */ }
    });
    window.addEventListener('storage', event => {
      if (event.key === key || event.key === null) {
        apply(event.newValue);
        select.value = root.dataset.theme;
      }
    });
  });
})();
