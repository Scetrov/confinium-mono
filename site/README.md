# Hugo site

Install Hugo (CI pins 0.168.0; extended is not required). From the repository root:

```sh
hugo server --source site --bind 127.0.0.1 --port 1313
```

Open `http://localhost:1313/`. Hugo watches route content, templates, menu data,
and mounted assets. Use `hugo --source site` for a disk build in `site/public/`;
its relative links also work when opening `site/public/index.html` directly.

- `content/` defines the public routes and their page parameters.
- `layouts/` and `data/navigation.json` define the shared navigation.
- `assets/proofs/` holds page fragments around the shared navigation, including
  existing embedded fonts and CSS. No Python is needed to build or preview them.
- `hugo.toml` mounts shared assets and downloads without copying them into the
  source tree. Standalone HTML proofs remain in the repository, not in these mounts.

When regenerating a specimen with Python, refresh just its Hugo fragments:

```sh
uv run python scripts/arrow_study.py
python3 scripts/import_proof.py studies/programming-arrows/index.html
```

The importer does not overwrite existing route metadata or alter the standalone
proof. Commit the refreshed fragments. Edit Hugo layout and navigation changes
in `site/` directly; don't re-import pages just for a menu change.

In GitHub, set **Settings → Pages → Build and deployment → Source** to
**GitHub Actions**. Pull requests build with Hugo; pushes to `main` build and
deploy `site/public/`. The tag-triggered font release workflow is independent.
