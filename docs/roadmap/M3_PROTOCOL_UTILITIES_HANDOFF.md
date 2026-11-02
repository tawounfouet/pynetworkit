# PyNetworkKit - Handoff M2 vers M3 Protocol Utilities

> Date : 2026-11-02
>
> Source : `16_PYNETWORKKIT_IMPLEMENTATION_ROADMAP.md` (section 10) et clôture technique M2.
>
> Objectif M3 : helpers protocolaires de niveau application, et non une pile HTTP/TCP.

## Dépendances héritées de M2

- `AsyncByteStream` : flux d'octets, sans frontière de message et sans garantie de réception distante.
- `AsyncDatagramChannel` : datagrammes et métadonnées de troncature, sans fiabilité intrinsèque.
- `Deadline` : budget absolu monotone réutilisable à travers plusieurs opérations.
- `BoundedByteQueue` / `bounded_map` : budgets mémoire et de tâches.
- `IPEndpoint` : endpoint numérique valide, sans résolution DNS implicite.
- Séparation : domaine et ports purs, `asyncio` seulement dans les adaptateurs.

## Epics M3 proposés (à cadrer avant bootstrap)

| Axe | Livrable | Validation minimale |
| --- | --- | --- |
| Framing | Framing length-prefixed et delimiter-based, avec max-size explicite | Refus des frames surdimensionnées et malformées; lectures TCP partielles |
| Codecs | Protocoles encode/decode incrémentaux pour données applicatives | Parser fuzzable, erreurs typées, bornes mémoire |
| Naming | Port `NameResolver`, adaptateur stdlib et fake pour tests | Plusieurs résultats possibles, erreurs/timeouts, données non fiables |
| Exemples | Protocole requête/réponse local documenté au niveau wire | Loopback + doubles mémoire, aucun service Internet requis |
| Qualité | ADR, tests propriétés, compatibilité et CI | Matrice 9/9, couverture conforme, aucun mélange M3/M4 |

## Exclusions et gates

M3 ne réimplémente pas TCP, DNS serveur ou HTTP complet; TLS, validation de certificat, egress policy et prévention SSRF seront cadrés dans M4. Tous les parseurs doivent imposer une limite stricte de mémoire et de taille. Les résultats de résolution sont non fiables jusqu'à application des politiques de connexion pertinentes. Le nombre d'Epics et d'issues M3 reste une proposition de cadrage, aucune ressource Github M3 n'est créée ici.

## Premières décisions d'architecture à prendre

1. Framing : séparer la logique pure d'encodage/décodage de l'I/O réseau.
2. Une `read(max_bytes)` peut retourner moins que demandé : introduire une consommation incrémentale, pas un appel magique de `recv(n)`.
3. DNS : ne pas convertir un `HostEndpoint` en `IPEndpoint` sans résultat explicite; conserver l'ensemble des résultats et leur famille.
4. Conserver les garanties de cancellation, de deadlines partagées et de buffers bornés sur chaque opération.

Référence de fin M2 : [audit final](../audits/M2_FINAL_TECHNICAL_CLOSURE_2026-11-02.md).
