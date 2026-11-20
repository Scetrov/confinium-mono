(() => {
  const key = 'confinium-theme';
  const modes = ['auto', 'light', 'dark'];
  const icons = {
    auto: '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/>',
    light: '<circle cx="12" cy="12" r="4"/><path d="M12 1v3m0 16v3M1 12h3m16 0h3M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2"/>',
    dark: '<path d="M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11Z"/>'
  };
  let button;
  const next = mode => modes[(modes.indexOf(mode) + 1) % modes.length];
  function apply(value) {
    const mode = modes.includes(value) ? value : 'auto';
    document.documentElement.dataset.theme = mode;
    if (!button) return;
    button.innerHTML = `<svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8">${icons[mode]}</svg>`;
    button.title = `Appearance: ${mode}. Switch to ${next(mode)}`;
    button.setAttribute('aria-label', button.title);
  }
  try { apply(localStorage.getItem(key)); } catch { apply('auto'); }
  document.addEventListener('DOMContentLoaded', () => {
    const nav = document.querySelector('.site-nav');
    if (!nav) return;
    button = document.createElement('button');
    button.type = 'button';
    button.className = 'theme-control';
    apply(document.documentElement.dataset.theme);
    nav.append(button);
    button.addEventListener('click', () => {
      const value = next(document.documentElement.dataset.theme);
      apply(value);
      try { localStorage.setItem(key, value); } catch { /* storage is optional */ }
    });
    window.addEventListener('storage', e => {
      if (e.key === key || e.key === null) apply(e.newValue);
    });
  });
})();
