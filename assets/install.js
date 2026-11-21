// Keep the ordinary releases link usable offline, without JS, or when rate-limited.
(async () => {
  const status = document.querySelector('#release-status');
  try {
    const response = await fetch('https://api.github.com/repos/Scetrov/confinium-mono/releases/latest');
    if (response.status === 404) {
      status.textContent = 'No published release yet.';
      return;
    }
    if (!response.ok) throw new Error('Release lookup failed');
    const release = await response.json();
    const name = 'ConfiniumMono-Variable.zip';
    const tag = release.tag_name;
    if (!/^\d+\.\d+\.\d+$/.test(tag) || !release.assets.some(asset => asset.name === name)) {
      status.textContent = 'See the release notes for available downloads.';
      return;
    }
    const link = document.createElement('a');
    link.href = `https://github.com/Scetrov/confinium-mono/releases/download/${tag}/${name}`;
    link.textContent = `Download Confinium Mono ${tag} (ZIP)`;
    status.replaceChildren(link);
  } catch {
    status.textContent = 'Could not check the latest version. Use the releases link below.';
  }
})();
