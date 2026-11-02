# 30 - PyNetworkKit M2 : GitHub Project v2 Integration & Bootstrap

> Date : 2026-11-02
> Repo : https://github.com/tawounfouet/pynetworkkit
> Project : https://github.com/users/tawounfouet/projects/9/views/1
> Status : BOOTSTRAP EXÉCUTÉ SUR GITHUB, documentation et scripts ajoutés via PR protégée.
> Release : aucune publication autorisée par ce document.

## 1. Inventaire réel du bootstrap

Le 2026-11-02, le propriétaire a exécuté le bootstrap puis `--verify`
dans une session GitHub CLI authentifiée. Les sorties contiennent :

| Objet | GitHub | État |
| --- | --- | --- |
| Milestone M2 | #2, `M2 - Async Core (v0.2.0a1)` | 1/1 |
| Epics E00-E05 | Issues #73-#78 | 6/6 |
| Tâches M2-001..036 | Issues #79-#114 | 36/36 |
| Relations parent/sous-issue | six enfants par Epic | 36/36 |
| Project v2 #9 | 42 items | 42/42 |
| Status | Todo initial | 42/42 |
| Priority | P0/P1 | 42/42 |
| Vues dédiées | 06 Backlog, 07 Execution Board, 08 Roadmap | 3/3 |
| Historique M0/M1 | Vues et items existants | Préservés |
| Gouvernance v0.1.0a2 | Issues #29 et #67 | Indépendantes |

Les numéros GitHub réels sont enregistrés dans le manifeste pour aider à
naviguer, mais le script ne suppose pas que chaque exécution créera les
mêmes numéros de ticket dans un autre dépôt.

## 2. Référentiel versionné

- `docs/roadmap/29_PYNETWORKKIT_M2_ASYNC_CORE_IMPLEMENTATION_PLAN.md`
  : édition GitHub du plan, synchronisée sur les critères des 42 issues
  existantes, avec catalogue dans la section 7.
- `scripts/github/m2_backlog_manifest.json` : six Epics et 36 tâches,
  priorités, dépendances et critères d'acceptation.
- `scripts/github/m2_project_bootstrap.sh` : bootstrap idempotent,
  prévisualisation par défaut et modes `--apply` / `--verify`.
- `tests/unit/test_m2_project_bootstrap_manifest.py` : contrôle du
  manifeste, intégrité des liens, commandes mutantes protégées.
- Le document original complet de planification local de 709 lignes
  reste un document historique distinct; l'édition GitHub est un
  référentiel synchronisé avec les issues effectivement créées.

## 3. Mode opératoire

Depuis la RACINE du clone `pynetworkkit` sur Mac, après fusion de la PR :

```bash
pwd
git switch main
git pull --ff-only origin main

gh auth status
# Au besoin: gh auth refresh -s project

bash scripts/github/m2_project_bootstrap.sh
bash scripts/github/m2_project_bootstrap.sh --verify
```

Le mode par défaut ne modifie aucune ressource. `--verify` contrôle
milestone, 42 issues, priorité, statuts, 36 liens natifs et trois vues.
`--apply` crée les ressources manquantes, mais **ne doit pas être
relancé sur une roadmap déjà en cours de traitement sans revue** :
les statuts ne seront plus tous Todo et le script refusera des conflits.

Ne PAS refaire un bootstrap parallèle, recréer une milestone ou créer
les 42 issues en doublon : GitHub est déjà prêt pour E00.

## 4. Project v2

| Vue | Type | Intention |
| --- | --- | --- |
| 06 - M2 Backlog | Table | Tous les tickets M2 |
| 07 - M2 Execution Board | Board | Tâches M2 hors Epics |
| 08 - M2 Roadmap | Roadmap | Epics M2 uniquement |

Aucun `Start date`, `Target date` ni `Size` n'est inventé.
Le champ `Linked pull requests` se remplira lors des PR d'implémentation.
Le champ natif `Sub-issues progress` évoluera au fil des tâches fermées.

## 5. Sécurité et gouvernance

La branche `main` est protégée avec neuf contrôles CI obligatoires.
Les scripts M2 n'affectent ni les autres Epics ni les issues #29/#67
relatives aux releases. Les commandes `--apply` ne créent aucun tag,
GitHub Release, TestPyPI ou PyPI upload.

L'intégration documentaire doit respecter une PR et la CI complète.
Un bootstrap réussi n'est pas une preuve d'implémentation réseau.

## 6. Prochaines actions

1. Vérifier les chemins versionnés après fusion et la CI sur `main`.
2. Démarrer [PNK-M2-001](https://github.com/tawounfouet/pynetworkkit/issues/79).
3. Produire l'audit d'API M0/M1/M2 et proposer ADR-M2-01/02.
4. Ouvrir la première PR technique M2, sans publication automatique.

Décision : **GO pour exécuter E00**. M2 reste à 0/36 tâches livrées.
