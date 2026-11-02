# PyNetworkKit M2 - Audit final GO / NO-GO et clôture technique

> Date : 2026-11-02
>
> Milestone : M2 - Async Core (`0.2.0a1`)
>
> Source de vérité pour le code audité : `main` au SHA `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12`
>
> Décision sur le code audité : **GO technique M2**
>
> Décision sur publication (Git tag, GitHub Release, TestPyPI ou PyPI) : **NO-GO publication tant qu'une autorisation séparée n'a pas été documentée**
>
> Ce document est l'audit de l'état du code ci-dessus. La fusion du rapport change le SHA de `main`; le run CI post-fusion et la fermeture des tickets sont conservés dans les commentaires de [#114](https://github.com/tawounfouet/pynetworkkit/issues/114).

## 1. Périmètre audité

M2 apporte des ports asynchrones complémentaires et des adaptateurs `asyncio` pour TCP et UDP, la gestion explicite de l'ownership, de la cancellation et des deadlines monotones, la backpressure bornée par octets/éléments et une concurrence structurée limitée par travailleurs. La compatibilité M0/M1 demeure un invariant. Le domaine et les ports restent indépendants des adaptateurs réseau.

Le code expose `AsyncioTCPConnector`, `AsyncioTCPListener`, `AsyncioTCPStream`, `AsyncioUDPChannel`, `Deadline`, `within_deadline`, `BoundedByteQueue` et `bounded_map`. Les limites du contrat TCP (flux d'octets sans framing, annulation avec éventuelle écriture partielle) et UDP (datagrammes sans garantie de livraison) sont documentées.

## 2. Preuves reproductibles sur le SHA audité

| Contrôle | Preuve / résultat |
| --- | --- |
| SHA code de référence | `d29d686a5fb01c8d5161e1a5fe6051967dfa0d12` |
| CI `main` | [run #41525452114](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452114) : **9/9** jobs réussis |
| Matrice OS/Python | Linux, macOS, Windows ; Python 3.11, 3.12, 3.13 |
| Pytest | **240 tests réussis** sur le job Ubuntu / Python 3.11 |
| Couverture combinée branches | **97,54 %**, seuil bloquant **95 %** |
| Typage, style, hygiène | `mypy` strict, `ruff check`, `ruff format --check`, contrôles d'hygiène réussis |
| Audit de sécurité | [run #41525452563](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563) : `pip-audit --local` ne signale aucune vulnérabilité connue |
| Distribution | `pynetworkkit-0.2.0a1-py3-none-any.whl` et `pynetworkkit-0.2.0a1.tar.gz` construits et validés par `twine check`, puis installation wheel isolée |
| SHA256 | Les deux fichiers ont passé `sha256sum -c` dans le run de sécurité |
| Artefacts | [candidate #13178973173](https://github.com/tawounfouet/pynetworkkit/actions/runs/41525452563/artifacts/13178973173), avec wheel, sdist et `SHA256SUMS.txt`, rétention GitHub Actions limitée |
| Branch protection | `main` marqué `protected=true`, avec neuf contextes Quality obligatoires, via `GET /repos/.../branches/main` |
| Publication | Liste GitHub Releases vide au moment de l'audit ; le workflow M2 ne possède pas de permission de publication |

L'audit `pip-audit` décrit l'état connu des dépendances au moment du run. Il n'est pas une garantie absolue d'absence de vulnérabilités ni un pentest. Le seuil de couverture contractuel du plan M2 est 95 %, non le 98 % affiché sur une infographie de planification. La mesure 97,54 % franchit le gate applicable.

## 3. Traçabilité GitHub

- PRs de réalisation fusionnées : [#116](https://github.com/tawounfouet/pynetworkkit/pull/116), [#117](https://github.com/tawounfouet/pynetworkkit/pull/117), [#118](https://github.com/tawounfouet/pynetworkkit/pull/118), [#119](https://github.com/tawounfouet/pynetworkkit/pull/119), [#120](https://github.com/tawounfouet/pynetworkkit/pull/120), [#121](https://github.com/tawounfouet/pynetworkkit/pull/121), [#122](https://github.com/tawounfouet/pynetworkkit/pull/122) et [#123](https://github.com/tawounfouet/pynetworkkit/pull/123).
- ADR-M2-01 à ADR-M2-08 acceptées pour **l'implémentation technique**, sans autoriser une publication.
- Six Epics natifs [#73-#78](https://github.com/tawounfouet/pynetworkkit/issues/78), contenant chacun six sous-issues; les **36 relations natives** ont été relues via l'API GitHub.
- Au moment de la rédaction : **35/36 tâches** et **5/6 Epics** clos, avec uniquement [#114](https://github.com/tawounfouet/pynetworkkit/issues/114) et son Epic parent [#78](https://github.com/tawounfouet/pynetworkkit/issues/78) ouverts. Leur clôture est la dernière action de gouvernance après validation de cette PR et CI.
- Le Project v2 #9 et ses trois vues M2 ont été initialement vérifiés dans [le document bootstrap](../roadmap/30_PYNETWORKKIT_M2_GITHUB_PROJECT_V2_INTEGRATION_AND_BOOTSTRAP.md). **L'état live des champs Project v2 n'a pas pu être relu par l'intégration GitHub disponible**. Ne pas présenter ces champs comme audités en direct.

## 4. Décision G5 et périmètre de la clôture

**GO technique sur le SHA audité** : les contrats, adaptateurs, tests, sécurité des dépendances, distributions candidates, documentation et compatibilité sont suffisants pour déclarer l'implémentation du M2 qualifiée au niveau alpha. Les éventuels écarts de performance ou de comportement doivent rester soumis aux mêmes gates CI.

**NO-GO publication automatique** : aucun tag, aucune GitHub Release et aucun envoi vers un index de paquets ne découlent de cette décision. Une publication requiert une revue indépendante de release (autorisation explicite, vérification des métadonnées, provenance exacte des artefacts et politique de sécurité). Le workflow d'audit candidat utilise uniquement `contents: read` et n'émet pas d'identité OIDC.

**Réserves déclarées** : le protocole TCP half-close n'est pas exposé par `AsyncByteStream` et demeure différé; DNS, TLS et framing sont exclus de M2. Le Project v2 live ne peut être entièrement revalidé via les seules capacités de lecture présentes. L'état administratif de la milestone GitHub #2 doit être distingué de la validation du code et de la clôture des issues.

## 5. Handoff M3 : Protocol Utilities (`0.3.0a1`, planification)

La suite cohérente est M3, tel que proposé dans le roadmap 16, avec quatre familles de travaux : (1) framing applicatif length-prefixed et delimiter-based avec tailles maximales strictes; (2) port `NameResolver` et adaptateur de résolution DNS sans faire entrer `socket` dans le domaine; (3) résultats typés, erreurs et policy d'entrées non fiables; (4) exemple request-response et parseur testable par propriétés/fuzzing.

Critères d'entrée M3 : aucun changement incompatible dans les contrats M2; TLS et politiques d'egress réservés à M4; aucun client HTTP complet; usage de transports M2 remplaçables par des doubles mémoire et tests loopback; nouveaux ADR avant implémentation. La version `0.3.0a1` reste une cible de planification, pas un tag autorisé.

## 6. Journal de décision

- **G5 - Technical closure** : GO pour la base M2 auditée.
- **G6 - Publication** : NO-GO automatique, dossier séparé.
- **Suivi GitHub** : clôturer #114 puis #78 après fusion CI de la présente PR; inscrire le nouveau SHA final dans le commentaire de clôture. La milestone GitHub #2 et l'état des vues Project #9 exigent une vérification administrative distincte si l'interface disponible ne permet pas leur modification.
