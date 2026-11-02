# V9 - Incident de qualification setuptools, exécution #41492439988

## Constat GitHub vérifié le 2026-11-02

- Workflow : Release candidate audit (NO PUBLISH)
- Exécution : https://github.com/tawounfouet/pynetworkkit/actions/runs/41492439988
- SHA : `6af9f4dacfebf959a042311a910f53eefeaf144d`
- Résultat : FAILURE, job Candidate audit / Python 3.11
- Étape bloquante : `pip-audit --local`, exit code 1
- `setuptools 79.0.1` : trois entrées, dont deux pour PYSEC-2026-3447 et
  une pour GHSA-xmj3-9gf7-h52w. Ne pas compter le doublon comme deux failles.
- Fix minimal : 83.0.0 (PYSEC), 84.1.0 (GHSA). Relever à **84.1.0**.
- Avis : https://github.com/advisories/GHSA-xmj3-9gf7-h52w
- Le signalement `pynetworkkit 0.1.0a2` absent de PyPI est attendu pour un
  projet editable non publié et n'est pas la cause du blocage.

Les étapes de qualité, build, wheel, sha256 et collecte des artefacts ont
été ignorées après cet échec. Aucun hash candidat n'a été établi.

## Remédiation proposée

1. Fixer un plancher `setuptools>=84.1.0` dans `pyproject.toml`.
2. Installer `setuptools>=84.1.0` sur le runner AVANT le package dev.
3. Journaliser la version effectivement utilisée, puis maintenir
   `pip-audit --local` comme contrôle bloquant, sans ignore-vuln.
4. Ajouter les tests de non-régression de politique.
5. Fusionner uniquement avec neuf jobs qualité verts sur la PR protégée.
6. Refaire l'audit du candidat sur le nouveau SHA de main après fusion.

## Critères de clôture

- [ ] PR fusionnée et main CI 9/9 GREEN
- [ ] Nouveau run candidate main : pip-audit sans vulnérabilité connue
- [ ] Build, twine, wheel isolé, et deux SHA256 de la même exécution vérifiés
- [ ] État des alertes, droits et nom PyPI contrôlés
- [ ] Décision de publication distincte et explicite dans #67

**NO-GO** tant que ces preuves ne sont pas réunies. Aucun tag,
GitHub Release, TestPyPI ou PyPI upload n'est autorisé.
