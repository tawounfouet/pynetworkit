# PyNetworkKit V9 - Audit de sécurisation GitHub

Date : 2026-11-02
Repo : https://github.com/tawounfouet/pynetworkkit
SHA audité : 2a8f92643b35102f7241d67d19ef29d95f5e02da
Décision initiale : NO-GO pour toute publication.

## 1. Constat vérifié

| Contrôle | Preuve | État |
| --- | --- | --- |
| Dépôt public, branche main | GitHub repository API | Vérifié |
| Identité connectée admin | permissions.admin=true | Vérifié |
| Protection main | branch.protected=false | NON |
| Rulesets | API retourne [] | Aucun |
| Required checks | Politique de branche absente | NON |
| 9 CI checks existants | Actions run 41484577935 | 9/9 SUCCESS |
| Provenance des checks | GitHub Actions app_id 15368 | Vérifiée |
| CI token | CI yaml : contents read | Minimum |
| Workflow PR | pull_request sans pull_request_target | Minimum |
| Dépendances runtime | pyproject dependencies=[] | Aucune |
| Dépendances build/dev | Contraintes minimales, pas de lock | Risque |
| Dependabot | pip et GitHub Actions hebdomadaires | Configuré |
| GitHub Actions | Références @v7 non figées | Risque |
| Scan de secrets complet | Vérification heuristique seulement | Non prouvé |
| Code scanning / Dependabot alerts | Endpoint connecteur non accessible | Inconnu |
| Permissions Actions par défaut | Audit gh admin requis | À vérifier |
| Issues publication | #29 et #67 ouvertes | Bloquant |

Les 9 checks exacts ont été lus au SHA audité. Tous provenaient de
GitHub Actions (app_id 15368) et étaient réussis.

## 2. Correctifs V9 soumis au dépôt

Le fichier CI conserve les 9 noms de jobs et le seuil de couverture 95 %.
Les actions sont figées aux SHA complets vérifiés sur les refs officielles
GitHub le 2 novembre 2026 :

- actions/checkout v7 : 3d3c42e5aac5ba805825da76410c181273ba90b1
- actions/setup-python v7 : 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0
- actions/upload-artifact v7 : cf430e030ddbb5b0abf93d22962f4752f3646cd9

Le checkout n'enregistre plus durablement les credentials. La CI reçoit
un timeout de 30 minutes par job et annule les exécutions PR obsolètes.
Permissions conservées : contents: read.

Le nouveau workflow Release candidate audit (NO PUBLISH) est manuel :
- Seulement sur main avec un job protégé par la vérification de ref.
- Permissions GitHub Actions : contents read uniquement.
- pip-audit --local sur les dépendances de build/développement.
- Ruff, mypy, pytest, couverture et contrôle des secrets heuristique.
- Wheel et sdist, twine, installation wheel isolée, SHA256SUMS.
- Vérification du manifeste SHA256 puis artefacts à durée de vie 14 jours.
- Aucune commande de tag, GitHub Release, TestPyPI ou PyPI.
- Une exécution réussie de ce workflow reste à obtenir après fusion.

## 3. Politique main recommandée

Après fusion de V9, exécuter le script CLI suivant avec les droits admin :

    bash scripts/github/v9_main_protection.sh
    bash scripts/github/v9_main_protection.sh --audit-permissions
    bash scripts/github/v9_main_protection.sh --apply
    bash scripts/github/v9_main_protection.sh --verify

Le script est en lecture seule par défaut. Il refuse les rulesets existants,
vérifie 9/9 checks et leur app GitHub Actions, refuse les écrasements de
protections existantes et vérifie par lecture après application.

Politique cible :
- PR obligatoire et historique linéaire.
- Checks stricts : 9 jobs réels de la matrice CI, app_id 15368.
- Conversations de revue résolues.
- Applies to admins, pas de force push ni suppression.
- Reviews requises : 0 approbation en mode mainteneur unique.
  Passer à 1 uniquement avec un relecteur indépendant disponible.
- Préserver squash et rebase. Ne pas exiger une review impossible à obtenir.

Le connecteur GitHub sait modifier les fichiers, PR et issues. Il ne fournit
pas de mutation pour configurer la protection main : l'application réelle
requiert gh CLI (ou l'interface GitHub). Ne pas marquer cette étape comme
accomplie avant une lecture de confirmation.

## 4. Permissions et sécurité à vérifier

- GitHub Settings > Actions > General : droits du GITHUB_TOKEN.
- Collaboration : accès admin/write et invitations.
- Security & analysis : dependency graph, Dependabot alerts, code scanning.
- Secret scanning et push protection : disponibilité et activation.
- Private vulnerability reporting et accès aux security advisories.
- Environments : configuration d'un environnement de publication protégé.

Les endpoints privés d'alertes de sécurité ne sont pas accessibles avec le
connecteur fourni. UNKNOWN ne doit jamais être assimilé à PASS.

## 5. Risques résiduels

- Dépendances de développement non verrouillées et transitives à auditer.
- Pas d'attestation SLSA ni publication OIDC configurée à V9.
- Le simple succès des tests n'établit pas un scan de sécurité complet.
- Les artefacts CI sont temporaires. Des hashes durables sont requis
  avant autorisation de publication.
- M0 #29 et M1 #67 demandent des décisions de release indépendantes.

## 6. Décision

GO technique M1, étayé par la CI sur le SHA audité.
NO-GO release tant que les protections, permissions, alertes, audits et
artefacts exacts ne sont pas vérifiés et acceptés.

Sources officielles :
- https://docs.github.com/en/rest/branches/branch-protection
- https://docs.github.com/en/rest/repos/rules
- https://docs.pypi.org/trusted-publishers/
