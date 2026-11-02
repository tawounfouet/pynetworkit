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

- [x] Protections main et 9 required checks activés et vérifiés (owner CLI apply/verify, puis API GitHub main.protected=true le 2026-11-02).
- [x] PR, conversation resolution, restrictions admins et force push vérifiés par le script administratif `--verify` le 2026-11-02.
- [x] Permissions collaborateur et Actions GITHUB_TOKEN auditées : seul collaborateur listé `tawounfouet` admin/write, permissions par défaut `read`, revue PR par workflow désactivée.
- [ ] Disponibilité et configuration des alertes de dépendances/secrets.
- [ ] Relancer et réussir le workflow manuel Release candidate audit sur main. Premier run #41492439988 FAILED à `pip-audit --local` (setuptools 79.0.1).
- [ ] Vérifier que les 3 alertes `setuptools 79.0.1` sont éliminées avec `setuptools>=84.1.0` et qu'aucune autre vulnérabilité n'est détectée.
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

## Incident de qualification du 2026-11-02

- Run : https://github.com/tawounfouet/pynetworkkit/actions/runs/41492439988
- Head SHA : `6af9f4dacfebf959a042311a910f53eefeaf144d`
- Statut : FAILURE au contrôle `pip-audit --local` (pas de package candidat publié).
- Paquet en cause : `setuptools 79.0.1`, 3 signalements (PYSEC-2026-3447 deux fois, GHSA-xmj3-9gf7-h52w).
- Plancher des correctifs : `83.0.0` pour les signalements PYSEC, `84.1.0` pour GHSA. Retenir le minimum `84.1.0`.
- La mention du projet editable `pynetworkkit 0.1.0a2` non trouvé sur PyPI est attendue avant publication et ne constitue pas la cause du code de sortie 1.
- Remédiation : mise à jour setuptools AVANT `pip install -e`, plancher `[build-system]`, maintien de `pip-audit --local` bloquant.
- Aucune étape build/wheel/hash de ce run n'a été exécutée : aucun hash ni artefact candidat validé à en déduire.
- Le NO-GO de publication demeure jusqu'à un nouveau run vert et validation du reste de la checklist.
