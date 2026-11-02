#!/usr/bin/env bash
# PyNetworkKit M2 / GitHub Project v2 #9 bootstrap (Bash 3.2+, Python >=3.11).
# Preview by default. No tag, Release, TestPyPI or PyPI mutation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PNK_M2_MANIFEST="$ROOT/m2_backlog_manifest.json"
exec python3 - "$@" <<'PYNETWORKKIT_M2_BOOTSTRAP_PYTHON'
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = "tawounfouet/pynetworkkit"
OWNER = "tawounfouet"
PROJECT = 9
PROJECT_ID = "PVT_kwHOBKwz2s4Bpywv"
PROJECT_TITLE = "PyNetworkKit - Development Roadmap"
MILESTONE = "M2 - Async Core (v0.2.0a1)"
MANIFEST = Path(os.environ["PNK_M2_MANIFEST"])
AREAS = ["ports", "tcp", "udp", "lifecycle", "async", "testing"]
VIEWS = [
    ("06 - M2 Backlog", "TABLE_LAYOUT", f'repo:{REPO} is:issue milestone:"{MILESTONE}"'),
    ("07 - M2 Execution Board", "BOARD_LAYOUT", f'repo:{REPO} is:issue milestone:"{MILESTONE}" -label:"type:epic"'),
    ("08 - M2 Roadmap", "ROADMAP_LAYOUT", f'repo:{REPO} is:issue milestone:"{MILESTONE}" label:"type:epic"'),
]

def gh(*args: str, data: dict[str, Any] | None = None, allow404: bool = False) -> Any:
    cmd = ["gh", *args]
    p = subprocess.run(cmd, input=None if data is None else json.dumps(data),
                       capture_output=True, text=True, check=False)
    if p.returncode:
        if allow404 and ("HTTP 404" in p.stderr or "404 Not Found" in p.stderr):
            return None
        # Never echo environment secrets or authorization headers.
        raise RuntimeError(f"gh {args[0]} failed ({p.returncode}): {p.stderr[:800]}")
    if not p.stdout.strip():
        return {}
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        if args[:2] == ("project", "item-edit"):
            return {"ok": True}
        raise RuntimeError("Expected JSON from GitHub CLI")

def api(path: str, method: str = "GET", body: dict[str, Any] | None = None,
        allow404: bool = False) -> Any:
    a = ["api"]
    if method != "GET":
        a += ["--method", method]
    if body is not None:
        a += ["--input", "-"]
    return gh(*a, path, data=body, allow404=allow404)

def api_all(path: str) -> list[dict[str, Any]]:
    value = gh("api", "--paginate", "--slurp", path)
    return [item for page in value for item in page]

def graphql(query: str, **values: Any) -> dict[str, Any]:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in values.items():
        if value is not None:
            args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    result = gh(*args)
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL returned errors")
    return result.get("data") or {}

def load_plan() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    p = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (p["repository"], p["owner"], p["project_number"], p["project_id"]) != (
        REPO, OWNER, PROJECT, PROJECT_ID
    ):
        raise RuntimeError("Manifest repository or project identity mismatch")
    if p["milestone_title"] != MILESTONE or len(p["epics"]) != 6 or len(p["tasks"]) != 36:
        raise RuntimeError("Unexpected milestone or backlog dimensions")
    expected_keys = [f"PNK-M2-E{i:02}" for i in range(6)] + [
        f"PNK-M2-{i:03}" for i in range(1, 37)
    ]
    entries = []
    for e in p["epics"]:
        code = e["id"][-3:]
        entries.append(dict(key=e["id"], title=f'[{e["id"]}] M2/{code} - {e["title"]}',
                            body=f'## M2/{code} - {e["title"]}\n\n'
                                 f'**Source normative:** https://github.com/{REPO}/blob/main/{p["plan_path"]}\n'
                                 f'**Milestone:** {MILESTONE}\n**Priority:** P0\n\n'
                                 f'**Scope:** 6 native child issues: {", ".join(e["tasks"])}.\n\n'
                                 '**Definition of Done:** all six children closed with reviewed ADRs, '
                                 'merged PRs, exact-SHA CI evidence. Technical completion does not '
                                 'authorize a tag or PyPI publication.\n',
                            priority="P0", type="epic", epic=code, area=AREAS[int(code[-2:])]))
    for t in p["tasks"]:
        code = t["epic"][-3:]
        entries.append(dict(key=t["id"], title=f'[{t["id"]}] {t["title"]}',
                            body=f'## Objective\n\n{t["title"]}\n\n'
                                 f'**Source:** https://github.com/{REPO}/blob/main/{p["plan_path"]}, section 7.\n'
                                 f'**Epic:** [{t["epic"]}] (native parent relationship created by bootstrap).\n'
                                 f'**Priority:** {t["priority"]}\n'
                                 f'**Dependencies from plan:** {t["dependencies"]}. '
                                 'These are textual references until explicit GitHub dependency review.\n\n'
                                 f'## Acceptance criteria\n\n- [ ] {t["acceptance"]}\n'
                                 '- [ ] Add tests and exact-SHA CI evidence as appropriate.\n'
                                 '- [ ] Preserve M0/M1 backwards compatibility; link an ADR for behavioral change.\n\n'
                                 '## Release policy\n\nNo automatic tag, Release, TestPyPI or PyPI publication.\n',
                            priority=t["priority"], type="task", epic=code,
                            area=AREAS[int(code[-2:])]))
    if [x["key"] for x in entries] != expected_keys:
        raise RuntimeError("Manifest keys/order invalid")
    if any(x["priority"] not in ("P0", "P1") for x in entries):
        raise RuntimeError("Unknown priority")
    return p, entries

def preflight() -> dict[str, Any]:
    p = subprocess.run(["gh", "auth", "status", "-h", "github.com"],
                       capture_output=True, text=True, check=False)
    if p.returncode:
        raise RuntimeError("Run gh auth login and gh auth refresh -s project")
    r = api(f"repos/{REPO}")
    if r.get("full_name") != REPO or r.get("default_branch") != "main":
        raise RuntimeError("Repository identity/default branch mismatch")
    project = gh("project", "view", str(PROJECT), "--owner", OWNER, "--format", "json")
    if project.get("id") != PROJECT_ID or project.get("title") != PROJECT_TITLE:
        raise RuntimeError("Wrong Project identity; refusing writes")
    fields = gh("project", "field-list", str(PROJECT), "--owner", OWNER, "--limit",
                "100", "--format", "json")
    result = {}
    for name, required in (("Status", ("Todo",)), ("Priority", ("P0", "P1"))):
        match = [x for x in fields["fields"] if x.get("name") == name]
        if len(match) != 1 or match[0].get("type") != "ProjectV2SingleSelectField":
            raise RuntimeError(f"Missing single-select field: {name}")
        options = {x["name"]: x["id"] for x in match[0]["options"]}
        if not all(k in options for k in required):
            raise RuntimeError(f"Missing {name} choices")
        result[name] = dict(id=match[0]["id"], choices=options)
    return result

def issue_index() -> dict[str, dict[str, Any]]:
    index = {}
    for x in api_all(f"repos/{REPO}/issues?state=all&per_page=100"):
        if x.get("pull_request"):
            continue
        m = re.match(r"^\[(PNK-M2-(?:E0[0-5]|\d{3}))\]", x.get("title", ""))
        if m:
            if m.group(1) in index:
                raise RuntimeError(f"Duplicate issue {m.group(1)}")
            index[m.group(1)] = x
    return index

def milestone() -> dict[str, Any] | None:
    m = [x for x in api_all(f"repos/{REPO}/milestones?state=all&per_page=100")
         if x["title"] == MILESTONE]
    if len(m) > 1 or (m and m[0]["state"] != "open"):
        raise RuntimeError("Duplicate or closed M2 milestone")
    return m[0] if m else None

def project_items() -> dict[int, dict[str, Any]]:
    query = '''query($login:String!,$number:Int!,$after:String){user(login:$login){projectV2(number:$number){id items(first:100,after:$after){pageInfo{hasNextPage endCursor} nodes{id content{... on Issue{number repository{nameWithOwner}}} status:fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}} priority:fieldValueByName(name:"Priority"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}'''
    result: dict[int, dict[str, Any]] = {}
    cursor = None
    while True:
        data = graphql(query, login=OWNER, number=PROJECT, after=cursor)
        p = (data.get("user") or {}).get("projectV2")
        if not p or p.get("id") != PROJECT_ID:
            raise RuntimeError("Wrong Project GraphQL identity")
        for x in p["items"]["nodes"]:
            issue = x.get("content") or {}
            if (issue.get("repository") or {}).get("nameWithOwner") == REPO:
                n = issue["number"]
                if n in result:
                    raise RuntimeError(f"Duplicate Project item #{n}")
                result[n] = dict(id=x["id"],
                                 status=(x.get("status") or {}).get("name"),
                                 priority=(x.get("priority") or {}).get("name"))
        page = p["items"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
        if not cursor:
            raise RuntimeError("Incomplete Project pagination")
    return result

def view_index() -> dict[str, dict[str, Any]]:
    q = '''query($login:String!,$number:Int!){user(login:$login){projectV2(number:$number){id views(first:100){pageInfo{hasNextPage} nodes{id name layout filter}}}}}'''
    p = (graphql(q, login=OWNER, number=PROJECT).get("user") or {}).get("projectV2")
    if not p or p.get("id") != PROJECT_ID or p["views"]["pageInfo"]["hasNextPage"]:
        raise RuntimeError("Project views unavailable or paginated")
    return {x["name"]: x for x in p["views"]["nodes"]}

def expected_labels(x: dict[str, Any]) -> list[str]:
    return ["milestone:M2", f'epic:M2-{x["epic"]}', f'type:{x["type"]}',
            f'priority:{x["priority"]}', f'area:{x["area"]}']

def check_issue(x: dict[str, Any], found: dict[str, Any],
                milestone_num: int | None, strict: bool) -> None:
    if found["title"] != x["title"] or found["state"] != "open":
        raise RuntimeError(f'Issue {x["key"]} differs in title/state')
    current = (found.get("milestone") or {}).get("number")
    if current not in (None, milestone_num):
        raise RuntimeError(f'{x["key"]} belongs to conflicting milestone')
    if strict:
        if current != milestone_num:
            raise RuntimeError(f'{x["key"]} milestone not set')
        have = {z["name"] for z in found.get("labels", [])}
        if not set(expected_labels(x)).issubset(have):
            raise RuntimeError(f'{x["key"]} missing required labels')

def sync_views(*, apply: bool = False, strict: bool = False) -> None:
    existing = view_index()
    create = '''mutation($project:ID!,$name:String!,$layout:ProjectV2ViewLayout!){createProjectV2View(input:{projectId:$project,name:$name,layout:$layout}){projectV2View{id}}}'''
    update = '''mutation($view:ID!,$filter:String!){updateProjectV2View(input:{viewId:$view,filter:$filter}){projectV2View{id}}}'''
    for name, layout, filter_text in VIEWS:
        v = existing.get(name)
        if v:
            if v.get("layout") != layout:
                raise RuntimeError(f"Conflicting layout {name}")
            if v.get("filter") != filter_text:
                if apply and not v.get("filter"):
                    graphql(update, view=v["id"], filter=filter_text)
                elif strict:
                    raise RuntimeError(f"Conflicting view filter {name}")
            else:
                print(f"VIEW OK: {name}")
        elif apply:
            val = graphql(create, project=PROJECT_ID, name=name, layout=layout)
            graphql(update, view=val["createProjectV2View"]["projectV2View"]["id"],
                    filter=filter_text)
            print(f"VIEW CREATED: {name}")
        elif strict:
            raise RuntimeError(f"Missing view {name}")
        else:
            print(f"VIEW TO CREATE: {name}")

def verify(entries: list[dict[str, Any]], strict_todo: bool = True) -> None:
    m = milestone()
    if not m:
        raise RuntimeError("M2 milestone missing")
    found, items = issue_index(), project_items()
    for x in entries:
        issue = found.get(x["key"])
        if not issue:
            raise RuntimeError(f'Missing issue {x["key"]}')
        check_issue(x, issue, m["number"], strict=True)
        item = items.get(issue["number"])
        if not item or item["priority"] != x["priority"]:
            raise RuntimeError(f'Project item or Priority missing for {x["key"]}')
        if strict_todo and item["status"] != "Todo":
            raise RuntimeError(f'Bootstrap Status is not Todo for {x["key"]}')
        if x["type"] == "task":
            parent = api(f"repos/{REPO}/issues/{issue['number']}/parent", allow404=True)
            expected = found[f'PNK-M2-{x["epic"]}']["number"]
            if not parent or parent["number"] != expected:
                raise RuntimeError(f'Wrong native parent for {x["key"]}')
    sync_views(strict=True)
    print("VERIFIED: 1 M2 milestone, 6/6 Epics, 36/36 tasks, 36/36 native relations, 42/42 Project items")
    print("VERIFIED: Status Todo on all, Priority P0/P1, three M2 views; historical M0/M1 preserved")
    print("Release governance #29/#67 remains independent; no publication performed")

def apply(entries: list[dict[str, Any]], found: dict[str, dict[str, Any]],
          m: dict[str, Any] | None, fields: dict[str, Any]) -> None:
    if m is None:
        m = api(f"repos/{REPO}/milestones", "POST", {
            "title": MILESTONE,
            "description": "M2 Async Core planning: 6 epics and 36 tasks, no release authorization."})
        print(f"CREATE milestone #{m['number']}")
    label_set = {x["name"] for x in api_all(f"repos/{REPO}/labels?per_page=100")}
    labels = {name for x in entries for name in expected_labels(x)}
    for label in sorted(labels - label_set):
        color = ("b60205" if label == "priority:P0" else
                 "fbca04" if label == "priority:P1" else "ededed")
        api(f"repos/{REPO}/labels", "POST", {
            "name": label, "color": color, "description": "PyNetworkKit M2 planning"})
        print(f"CREATE label {label}")
    for x in entries:
        current = found.get(x["key"])
        if current:
            check_issue(x, current, m["number"], strict=False)
            if not current.get("milestone"):
                current = api(f"repos/{REPO}/issues/{current['number']}",
                              "PATCH", {"milestone": m["number"]})
            diff = set(expected_labels(x)) - {z["name"] for z in current.get("labels", [])}
            if diff:
                api(f"repos/{REPO}/issues/{current['number']}/labels",
                    "POST", {"labels": sorted(diff)})
        else:
            current = api(f"repos/{REPO}/issues", "POST", {
                "title": x["title"], "body": x["body"],
                "milestone": m["number"], "labels": expected_labels(x)})
            print(f"CREATE issue {x['key']} -> #{current['number']}")
        found[x["key"]] = current
    for x in entries:
        if x["type"] != "task":
            continue
        child = found[x["key"]]
        parent = found[f'PNK-M2-{x["epic"]}']
        current = api(f"repos/{REPO}/issues/{child['number']}/parent", allow404=True)
        if current is None:
            api(f"repos/{REPO}/issues/{parent['number']}/sub_issues",
                "POST", {"sub_issue_id": child["id"]})
            print(f"LINK #{child['number']} -> Epic #{parent['number']}")
        elif current.get("number") != parent["number"]:
            raise RuntimeError(f'Conflicting parent for {x["key"]}')
    items = project_items()
    for x in entries:
        number = found[x["key"]]["number"]
        if number not in items:
            gh("project", "item-add", str(PROJECT), "--owner", OWNER, "--url",
               f"https://github.com/{REPO}/issues/{number}", "--format", "json")
            print(f"PROJECT add {x['key']} #{number}")
    items = project_items()
    for x in entries:
        item = items.get(found[x["key"]]["number"])
        if not item:
            raise RuntimeError(f'Project item missing for {x["key"]}')
        for name, target in (("Status", "Todo"), ("Priority", x["priority"])):
            current = item[name.lower()]
            if current is None:
                gh("project", "item-edit", "--project-id", PROJECT_ID, "--id", item["id"],
                   "--field-id", fields[name]["id"],
                   "--single-select-option-id", fields[name]["choices"][target])
                print(f"FIELD {name}={target}: {x['key']}")
            elif current != target:
                raise RuntimeError(f'Conflicting {name} for {x["key"]}')
    sync_views(apply=True)

def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded PyNetworkKit M2 GitHub Project bootstrap")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="Create only missing resources")
    g.add_argument("--verify", action="store_true", help="Verify existing bootstrap resources")
    args = parser.parse_args()
    plan, entries = load_plan()
    fields = preflight()
    m, found, items = milestone(), issue_index(), project_items()
    if m is None and found:
        raise RuntimeError("M2 issues exist without milestone; reconcile manually")
    for x in entries:
        if x["key"] in found:
            check_issue(x, found[x["key"]], m["number"] if m else None, strict=False)
    present = sum(x["key"] in found for x in entries)
    in_project = sum(x["key"] in found and found[x["key"]]["number"] in items for x in entries)
    print(f"Repo: {REPO} | Project #{PROJECT} ({PROJECT_ID})")
    print(f"Milestone: {MILESTONE} | {'existing #'+str(m['number']) if m else 'to create'}")
    print(f"Plan: {len(plan['epics'])} Epics + {len(plan['tasks'])} tasks")
    print(f"Issues existing: {present}/42; missing: {42-present}; Project items: {in_project}/42")
    print("Status target: Todo for all; Priority: P0/P1; Size not assigned")
    if args.apply:
        apply(entries, found, m, fields)
        verify(entries)
    elif args.verify:
        verify(entries)
    else:
        sync_views()
        print("PREVIEW ONLY - no GitHub mutations. Re-run with --apply to bootstrap M2.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
PYNETWORKKIT_M2_BOOTSTRAP_PYTHON
