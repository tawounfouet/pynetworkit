# Security policy

PyNetworkKit is pre-alpha and is not currently approved for production use.

Please do **not** post exploitable vulnerability details, secrets or credentials in
public issues. Contact the repository owner through GitHub using a private
security advisory if GitHub's private vulnerability reporting is enabled,
or another private channel agreed with the maintainer.

Security baseline:
- Never add credentials or secrets to Git or tests.
- Do not run unsolicited network scans or contact third-party hosts in CI.
- TLS must validate peer identities when TLS support is introduced (M4).
- Keep test data synthetic and all network fixtures bounded.

No particular security response SLA is promised during bootstrap.
