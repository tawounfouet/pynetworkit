#!/usr/bin/env bash
# V9: Safe GitHub main protection bootstrap. Default is PREVIEW.
# Requires macOS Bash 3.2+, Python 3 and authenticated gh CLI.
# Never creates a tag, GitHub Release or PyPI upload.
set -euo pipefail
REPO="tawounfouet/pynetworkkit"
MODE="preview"
if [ "$#" -gt 0 ]; then
  case "$1" in
    --apply) MODE="apply" ;;
    --verify) MODE="verify" ;;
    --audit-permissions) MODE="audit" ;;
    --help|-h) echo "Usage: bash scripts/github/v9_main_protection.sh [--apply|--verify|--audit-permissions]"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
fi
command -v gh >/dev/null || { echo "gh missing" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 missing" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "gh auth login required" >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

echo "Repo $REPO | mode $MODE"
gh api "repos/$REPO" > "$TMP/repo.json"
python3 - "$TMP/repo.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
if (r.get("full_name"),r.get("default_branch")) != ("tawounfouet/pynetworkkit","main"):
    raise SystemExit("Repository identity mismatch")
print("Admin permission:",r.get("permissions",{}).get("admin","not visible"))
PY
if [ "$MODE" = "audit" ]; then
  echo "Actions default permissions:"
  gh api "repos/$REPO/actions/permissions/workflow" --jq '{default_workflow_permissions,can_approve_pull_request_reviews}' || true
  echo "Collaborator admin/push permissions:"
  gh api --paginate "repos/$REPO/collaborators?affiliation=all&per_page=100" --jq '.[] | [.login,.permissions.admin,.permissions.push] | @tsv' || true
  echo "Read-only audit complete. Inspect GitHub secrets, environments and Dependabot UI manually."
  exit 0
fi
gh api "repos/$REPO/branches/main" > "$TMP/branch.json"
gh api "repos/$REPO/rulesets?includes_parents=true" > "$TMP/rulesets.json"
SHA="$(python3 - "$TMP/branch.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))["commit"]["sha"])
PY
)"
echo "Current SHA: $SHA"
gh api "repos/$REPO/commits/$SHA/check-runs?per_page=100" > "$TMP/checks.json"
python3 - "$TMP/checks.json" "$TMP/rulesets.json" "$TMP/policy.json" <<'PY'
import json,sys
runs=json.load(open(sys.argv[1]))["check_runs"]
rules=json.load(open(sys.argv[2]))
required=[f"Quality / {os} / Python {py}"
          for os in ("ubuntu-latest","macos-latest","windows-latest")
          for py in ("3.11","3.12","3.13")]
byname={r["name"]:r for r in runs}
for name in required:
    r=byname.get(name)
    if r is None or r.get("app",{}).get("id")!=15368 or r.get("conclusion")!="success":
        raise SystemExit("Missing or unsuccessful GitHub Actions check: "+name)
if rules:
    raise SystemExit("Ruleset exists; refusing to overwrite without reconciliation")
policy={
    "required_status_checks":{"strict":True,
      "checks":[{"context":n,"app_id":15368} for n in required]},
    "enforce_admins":True,
    "required_pull_request_reviews":{
      "dismiss_stale_reviews":True,"require_code_owner_reviews":False,
      "required_approving_review_count":0,"require_last_push_approval":False},
    "restrictions":None,
    "required_conversation_resolution":True,
    "required_linear_history":True,
    "allow_force_pushes":False,"allow_deletions":False
}
if ("contexts" in policy["required_status_checks"]) == ("checks" in policy["required_status_checks"]):
    raise SystemExit("ERROR: GitHub requires exactly one of contexts or checks")
with open(sys.argv[3],"w") as f: json.dump(policy,f,indent=2)
print("Verified 9 GitHub Actions checks from app_id 15368 (checks-only API payload)")
print("Policy: PR required, review count 0, all 9 checks, strict, admins enforced,")
print("        conversations resolved, linear history, no force push or deletion.")
PY
PROTECTED="$(python3 - "$TMP/branch.json" <<'PY'
import json,sys
print("true" if json.load(open(sys.argv[1])).get("protected") else "false")
PY
)"
verify() {
  gh api "repos/$REPO/branches/main/protection" > "$TMP/protection.json" || return 1
  python3 - "$TMP/protection.json" "$TMP/policy.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); want=json.load(open(sys.argv[2]))
checks=x.get("required_status_checks") or {}
observed={(v.get("context"),v.get("app_id")) for v in checks.get("checks",[])}
required={(v["context"],v["app_id"]) for v in want["required_status_checks"]["checks"]}
if observed!=required or not checks.get("strict"): raise SystemExit("FAIL: status checks not exact")
reviews=x.get("required_pull_request_reviews")
if not isinstance(reviews,dict) or reviews.get("required_approving_review_count")!=0:
    raise SystemExit("FAIL: PR review policy differs")
if not reviews.get("dismiss_stale_reviews"): raise SystemExit("FAIL: stale review policy")
for field in ("enforce_admins","required_conversation_resolution","required_linear_history"):
    if not (x.get(field) or {}).get("enabled"): raise SystemExit("FAIL: "+field)
for field in ("allow_force_pushes","allow_deletions"):
    if (x.get(field) or {}).get("enabled"): raise SystemExit("FAIL: "+field)
print("SUCCESS: exact main protection policy verified")
PY
}
echo "main protected=$PROTECTED"
case "$MODE" in
  preview)
    if [ "$PROTECTED" = "true" ]; then verify
    else echo "PREVIEW only: --apply will install the protection policy"; fi
    ;;
  verify)
    [ "$PROTECTED" = "true" ] || { echo "ERROR: main unprotected"; exit 1; }
    verify
    ;;
  apply)
    if [ "$PROTECTED" = "true" ]; then
      echo "Refusing to overwrite existing protection; verifying"
      verify
      exit
    fi
    gh api --method PUT "repos/$REPO/branches/main/protection" --input "$TMP/policy.json" >/dev/null
    for attempt in 1 2 3 4 5 6; do
      if verify; then exit 0; fi
      echo "Retrying verification ($attempt/6)..."
      sleep 3
    done
    echo "ERROR: write may have applied, but verification was not confirmed" >&2
    exit 1
    ;;
esac
