# Contributing

Report design feedback and ordinary bugs in [GitHub Issues](https://github.com/Scetrov/confinium-mono/issues). For a security issue, see [SECURITY.md](SECURITY.md).

For font changes, include the glyph, variant and point size, and provide a rendered comparison where practical. Use original outlines only; do not submit material you cannot license under the [OFL 1.1](OFL.txt).

See [README.md](README.md) for the locked build environment and [AGENTS.md](AGENTS.md) for design constraints. Before submitting a change, run `uv run --locked python -m unittest discover -s tests -v`. Review rebuilt proofs in Chromium for visual changes. Keep earlier Chromium captures and the inputs that produced them; follow the [verification archive guide](verification/README.md).
