# Contributing to PyNetworkKit

Contribuer par de petites pull requests associées à un ticket GitHub,
un Epic et un milestone. M0 et M1 sont techniquement clôturés.

1. Prendre une issue et créer une branche courte, par exemple feat/m2-async-tcp.
2. Référencer issue, concept réseau, primitive Python, architecture et compromis.
3. Préserver la séparation M0 async / M1 sync et la compatibilité API.
4. Vérifier Ruff, mypy strict, pytest + couverture branches >=95 %, build et wheel.
5. Exiger les neuf contrôles Linux/macOS/Windows x Python 3.11, 3.12, 3.13.
6. Ne pas contourner les protections de main ou les validations de PR.
7. Relier les preuves aux SHA et fermer les issues seulement après intégration.

## Software Design & Learning

DDD, DIP, ISP, SoC, KISS/YAGNI et idiomes Python.
Domain pur sans dépendances infrastructure; ports par typing.Protocol;
adapters concrets et tests de contrat / loopback bornés.
Documenter EOF, datagrammes vides, writes partiels, timeouts et ownership.

## Sécurité et release

Ne pas committer de secrets ni données personnelles. Aucun scan réseau
sur une infrastructure externe sans autorisation.
Toute création de tag, GitHub Release, TestPyPI ou PyPI requiert un GO
distinct sur le SHA et les empreintes d'artefacts.

Voir SECURITY.md, docs/governance/V9_GITHUB_HARDENING_AUDIT_2026-11-02.md
et docs/releases/V9_0_1_0a2_PREPUBLICATION_GATE.md.
