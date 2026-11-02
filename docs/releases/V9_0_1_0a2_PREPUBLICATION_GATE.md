# PyNetworkKit v0.1.0a2 - Gate de prépublication V9

Statut : PREPARATION UNIQUEMENT - NO-GO pour publication.
Gouvernance M1 : https://github.com/tawounfouet/pynetworkkit/issues/67
Gouvernance M0 : https://github.com/tawounfouet/pynetworkkit/issues/29
Source M1 qualifiée : 2a8f92643b35102f7241d67d19ef29d95f5e02da
CI M1 : https://github.com/tawounfouet/pynetworkkit/actions/runs/41484577935

## Acquis techniques

- [x] Implémentation M1 PR #66 fusionnée.
- [x] Documentation et qualification PR #68 fusionnée.
- [x] Validation des ADR M1 PR #69 fusionnée.
- [x] 9/9 CI validés sur main.
- [x] 184 tests, couverture 98,90 % sur Linux Python 3.11.
- [x] Build et import wheel isolé présents dans la CI.

## Garde-fous avant publication

- [ ] Protections main et 9 required checks activés et vérifiés.
- [ ] PR, conversation resolution, restrictions admins et force push vérifiés.
- [ ] Permissions collaborateur et Actions GITHUB_TOKEN auditées.
- [ ] Disponibilité et configuration des alertes de dépendances/secrets.
- [ ] Exécuter le workflow manuel Release candidate audit sur main.
- [ ] Examiner toutes les vulnérabilités éventuelles de pip-audit.
- [ ] Enregistrer le SHA du job, les noms et SHA256 de wheel + sdist.
- [ ] Vérifier package name sur PyPI et droits du propriétaire.
- [ ] Décider explicitement du devenir du candidat a1 dans l'issue #29.
- [ ] Formaliser un GO signé pour un SHA et deux empreintes d'artefact.
- [ ] Autoriser séparément la création du tag v0.1.0a2.
- [ ] Autoriser séparément une GitHub Release.
- [ ] Autoriser séparément toute publication TestPyPI/PyPI.

## Processus

1. Fusionner et valider la PR V9 sur son SHA exact.
2. Exécuter le script GitHub CLI de protection main en preview puis apply.
3. Obtenir une vérification read-back positive de la protection.
4. Dans Actions, lancer Release candidate audit (NO PUBLISH), ref main.
5. Examiner le rapport de vulnérabilités, la qualité, les artefacts et hashes.
6. Transcrire les preuves et le GO/NO-GO dans l'issue #67.
7. Ne pas publier sans autorisations explicites et indépendantes.

La publication future doit utiliser un workflow OIDC Trusted Publishing
dédié avec environnement protégé et permissions limitées par job.
Ce workflow n'est volontairement pas créé par V9.

## En cas d'échec

Conserver NO-GO, ouvrir un ticket de correction et produire une nouvelle PR.
Ne jamais forcer un tag ni remplacer un artefact PyPI déjà publié.
L'absence de publication ne nécessite aucun rollback.
