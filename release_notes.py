#!/usr/bin/env python3
"""
Generate Markdown release notes from GitLab commits for a list of projects.

Enhancements:
- NEW: --group-across-projects to group all commits from multiple projects together by type,
       prefixing each item with the project name, e.g., "- [Group/Repo] feat: ...".
- Accept projects by numeric ID or full path (e.g., group/subgroup/repo).
- Choose range by tags/branches (from-ref..to-ref) or by date (since/until).
- Groups commits using Conventional Commits types (feat, fix, perf, etc.).
- Skips merge commits by default (can include with flag).
- Adds links to commits, merge requests (!123), and issues (#123).
- Handles pagination and basic retry for rate limits (429) and transient errors.
- Outputs Markdown file.
"""

from __future__ import annotations
import argparse
import os
import re
import sys
import time
import json
from typing import Dict, List, Optional, Tuple

try:
    import requests  # type: ignore
except Exception:
    requests = None

CONVENTIONAL_TYPES_ORDER = [
    "feat",
    "fix",
    "perf",
    "refactor",
    "docs",
    "build",
    "ci",
    "test",
    "style",
    "chore",
    "revert",
]

TYPE_EMOJIS = {
    "feat": "✨",
    "fix": "🐛",
    "perf": "⚡",
    "refactor": "♻️",
    "docs": "📝",
    "build": "📦",
    "ci": "🤖",
    "test": "✅",
    "style": "🎨",
    "chore": "🧹",
    "revert": "⏪",
    "other": "🔧",
}

MERGE_COMMIT_TITLE_PREFIXES = (
    "Merge branch",
    "Merge remote-tracking branch",
    "Merge pull request",
    "Merge tag",
    "Merge branch '",
)

MR_PATTERN = re.compile(r"!([0-9]+)")
ISSUE_PATTERN = re.compile(r"#([0-9]+)")


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate Markdown release notes from GitLab commits for specific projects",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--gitlab-url", default="https://gitlab.com", help="Base GitLab URL (no trailing slash)")
    p.add_argument(
        "--token",
        default=os.getenv("GITLAB_TOKEN"),
        help="GitLab access token (PAT or OAuth). Can also be set via GITLAB_TOKEN env var.",
    )

    proj = p.add_mutually_exclusive_group(required=True)
    proj.add_argument("--project", action="append", help="Project ID or path (can be used multiple times)")
    proj.add_argument("--projects-file", help="Path to a file with one project ID or path per line")

    rng = p.add_mutually_exclusive_group(required=True)
    rng.add_argument("--from-ref", help="Starting ref (tag or branch) for comparison")
    p.add_argument("--to-ref", help="Ending ref (tag or branch) for comparison (required if --from-ref)")

    rng.add_argument("--since", help="ISO8601 timestamp for start of range (e.g., 2025-10-01T00:00:00Z)")
    p.add_argument("--until", help="ISO8601 timestamp for end of range")

    p.add_argument("--include-merge-commits", action="store_true", help="Include merge commits in the notes")
    p.add_argument("--max-pages", type=int, default=50, help="Safety cap for pagination")
    p.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    p.add_argument("--retries", type=int, default=3, help="Retries for transient errors per request")
    p.add_argument("--output", default="release-notes.md", help="Output Markdown file path")
    p.add_argument(
        "--group-across-projects",
        action="store_true",
        help="Group all commits from all projects together by type, prefixing each line with the project name",
    )

    return p.parse_args()

def get_headers(token: str) -> Dict[str, str]:
    # GitLab supports either PRIVATE-TOKEN or Authorization: Bearer
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": os.getenv("GITLAB_TOKEN"),
        # "User-Agent": "release-notes-script/1.0",
    }

def api_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    if base.endswith("/api/v4"):
        return f"{base}{path}"
    return f"{base}/api/v4{path}"


def request_with_retry(method: str, url: str, headers: Dict[str, str], params=None, timeout=30.0, retries=3):
    if requests is None:
        raise RuntimeError("The 'requests' package is required to run this script. Please install requests.")

    backoff = 1.5
    for attempt in range(1, retries + 1):
        try:
            resp = requests.request(method, url, headers=headers, params=params, timeout=timeout)
            if resp.status_code in (429, 502, 503, 504):
                wait = float(resp.headers.get("Retry-After", 0)) or min(2 ** attempt, 10)
                eprint(f"{resp.status_code} on {url}. Retrying in {wait:.1f}s (attempt {attempt}/{retries})...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except Exception as e:
            if attempt == retries:
                raise
            wait = min(backoff ** attempt, 10)
            eprint(f"Error {e} on {url}. Retrying in {wait:.1f}s (attempt {attempt}/{retries})...")
            time.sleep(wait)
    raise RuntimeError("Unreachable")


def paginate_get(url: str, headers: Dict[str, str], params: Optional[Dict]=None, max_pages: int=50, timeout: float=30.0, retries: int=3):
    if params is None:
        params = {}
    page = 1
    while page <= max_pages:
        p = {**params, "per_page": 100, "page": page}
        resp = request_with_retry("GET", url, headers, params=p, timeout=timeout, retries=retries)
        data = resp.json()
        if isinstance(data, list):
            for item in data:
                yield item
        else:
            yield data
            break
        next_page = resp.headers.get("X-Next-Page")
        if not next_page:
            break
        try:
            page = int(next_page)
        except ValueError:
            page += 1


def get_project_info(base_url: str, headers: Dict[str, str], project: str, timeout: float, retries: int) -> Dict:
    from urllib.parse import quote
    project_enc = quote(str(project), safe='')
    url = api_url(base_url, f"/projects/{project_enc}")
    resp = request_with_retry("GET", url, headers, timeout=timeout, retries=retries)
    return resp.json()


def get_commits_by_compare(base_url: str, headers: Dict[str, str], project: str, from_ref: str, to_ref: str, timeout: float, retries: int):
    from urllib.parse import quote
    project_enc = quote(str(project), safe='')
    url = api_url(base_url, f"/projects/{project_enc}/repository/compare")
    params = {"from": from_ref, "to": to_ref}
    resp = request_with_retry("GET", url, headers, params=params, timeout=timeout, retries=retries)
    data = resp.json()
    commits = data.get("commits", [])
    return commits, data


def get_commits_by_time(base_url: str, headers: Dict[str, str], project: str, since: str, until: Optional[str], timeout: float, retries: int, max_pages: int) -> List[Dict]:
    from urllib.parse import quote
    project_enc = quote(str(project), safe='')
    url = api_url(base_url, f"/projects/{project_enc}/repository/commits")
    params = {"since": since}
    if until:
        params["until"] = until
    commits: List[Dict] = []
    for item in paginate_get(url, headers, params=params, max_pages=max_pages, timeout=timeout, retries=retries):
        if isinstance(item, dict) and "id" in item:
            commits.append(item)
    return commits


def is_merge_commit(commit: Dict) -> bool:
    title = commit.get("title", "")
    if any(title.startswith(prefix) for prefix in MERGE_COMMIT_TITLE_PREFIXES):
        return True
    msg = commit.get("message", "")
    if "See merge request" in msg:
        return True
    return False


def parse_conventional_type(title: str) -> Tuple[str, Optional[str]]:
    m = re.match(r"^(\w+)(?:\(([^)]+)\))?!?:\s+", title)
    if m:
        return m.group(1).lower(), m.group(2)
    return "other", None


def linkify_refs(text: str, project_web_url: str) -> str:
    def repl_mr(m):
        iid = m.group(1)
        return f"[!{iid}]({project_web_url}/-/merge_requests/{iid})"
    def repl_issue(m):
        iid = m.group(1)
        return f"[#{iid}]({project_web_url}/-/issues/{iid})"
    text = MR_PATTERN.sub(repl_mr, text)
    text = ISSUE_PATTERN.sub(repl_issue, text)
    return text


def group_commits(commits: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {t: [] for t in CONVENTIONAL_TYPES_ORDER}
    grouped["other"] = []
    for c in commits:
        t, _scope = parse_conventional_type(c.get("title", ""))
        t = t if t in grouped else "other"
        grouped[t].append(c)
    return grouped


def build_markdown_for_project(project_info: Dict, commits: List[Dict], range_text: str) -> str:
    name = project_info.get("name_with_namespace") or project_info.get("path_with_namespace") or project_info.get("name")
    web_url = project_info.get("web_url")
    md_lines: List[str] = []
    md_lines.append(f"## {name}")
    md_lines.append("")
    md_lines.append(f"_Range_: {range_text}")
    md_lines.append("")
    if not commits:
        md_lines.append("No changes in this range.")
        md_lines.append("")
        return "\n".join(md_lines)
    grouped = group_commits(commits)
    for t in CONVENTIONAL_TYPES_ORDER + ["other"]:
        bucket = grouped.get(t, [])
        if not bucket:
            continue
        emoji = TYPE_EMOJIS.get(t, TYPE_EMOJIS["other"])  # default
        header = t.capitalize() if t != "ci" else "CI"
        md_lines.append(f"### {emoji} {header}")
        md_lines.append("")
        for c in bucket:
            # format_commit_line(c, web_url)
            md_lines.append(format_commit_line(c, web_url))
        md_lines.append("")
    return "\n".join(md_lines)


def build_cross_project_markdown(aggregated_entries, title_prefix: str = "Release Notes") -> str:
    from collections import defaultdict
    groups = defaultdict(list)
    for item in aggregated_entries:
        groups[item['type']].append(item)
    doc = []
    doc.append(f"# {title_prefix}")
    doc.append("")
    doc.append(f"_Generated on: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}_")
    doc.append("")
    order = CONVENTIONAL_TYPES_ORDER + ["other"]
    checked = []
    for t in order:
        bucket = groups.get(t, [])
        if not bucket:
            continue
        emoji = TYPE_EMOJIS.get(t, TYPE_EMOJIS['other'])
        header = t.capitalize() if t != 'ci' else 'CI'
        doc.append(f"## {emoji} {header}")
        doc.append("")
        
        for item in bucket:
            # item['line'] begins with '- ', keep content after that and add project prefix
            line_without_dash = item['line'][2:] if item['line'].startswith('- ') else item['line']
            project_name = item['project_name'].replace(" ","").split("/")[-1].replace("cmg-cp-","").replace("-ci-cd","").replace("cmg-ec2-blue-green-cd-pipeline","EC2 Deploy").replace("ami-ci","EC2 Build").replace("terraform-cd","Terraform")
            check = line_without_dash.split("([")[0]
            if check not in checked:
                print(check)
                checked.append(check)
                if "chore: package Version in catalog-info" in line_without_dash:
                    doc.append(f"- **[{project_name}]** {line_without_dash} ** RELEASE")
                else:
                    doc.append(f"- **[{project_name}]** {line_without_dash}")
        doc.append("")
    return "\n".join(doc)


def load_projects(args: argparse.Namespace) -> List[str]:
    if args.project:
        return args.project
    projects: List[str] = []
    with open(args.projects_file, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                projects.append(s)
    return projects


def main():
    args = parse_args()
    if not args.token:
        eprint("Error: no token provided. Use --token or set GITLAB_TOKEN.")
        sys.exit(2)
    if args.from_ref and not args.to_ref:
        eprint("Error: --to-ref is required when using --from-ref.")
        sys.exit(2)

    projects = load_projects(args)
    headers = get_headers(args.token)

    all_sections: List[str] = []
    aggregated: List[dict] = []

    for proj in projects:
        try:
            project_info = get_project_info(args.gitlab_url, headers, proj, args.timeout, args.retries)
        except Exception as e:
            eprint(f"Failed to fetch project '{proj}': {e}")
            all_sections.append(f"## {proj}\n\nFailed to fetch project details: {e}\n")
            continue

        try:
            if args.from_ref:
                commits, _compare = get_commits_by_compare(
                    args.gitlab_url, headers, proj, args.from_ref, args.to_ref, args.timeout, args.retries
                )
                range_text = f"{args.from_ref}…{args.to_ref} ([compare]({project_info['web_url']}/-/compare/{args.from_ref}...{args.to_ref}))"
            else:
                commits = get_commits_by_time(
                    args.gitlab_url, headers, proj, args.since, args.until, args.timeout, args.retries, args.max_pages
                )
                range_text = f"{args.since}…{args.until or 'now'}"
        except Exception as e:
            eprint(f"Failed to fetch commits for project '{proj}': {e}")
            all_sections.append(f"## {project_info.get('name_with_namespace', proj)}\n\nFailed to fetch commits: {e}\n")
            continue

        if not args.include_merge_commits:
            commits = [c for c in commits if not is_merge_commit(c)]

        if args.group_across_projects:
            name = project_info.get('name_with_namespace') or project_info.get('path_with_namespace') or project_info.get('name')
            web_url = project_info.get('web_url')
            for c in commits:
                t, _ = parse_conventional_type(c.get('title', ''))
                if t not in CONVENTIONAL_TYPES_ORDER:
                    t = 'other'
                line = format_commit_line(c, web_url)
                aggregated.append({'type': t, 'project_name': name, 'line': line})
        else:
            section_md = build_markdown_for_project(project_info, commits, range_text)
            all_sections.append(section_md)

    out_path = args.output
    if args.group_across_projects:
        md = build_cross_project_markdown(aggregated)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(md.rstrip() + '\n')
    else:
        doc: List[str] = []
        title = 'Release Notes'
        doc.append(f'# {title}')
        doc.append('')
        doc.append(f'_Generated on: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}_')
        doc.append('')
        doc.extend(all_sections)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(doc).rstrip() + "\n")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        eprint("Interrupted")
        sys.exit(130)
 


def format_commit_line(c: Dict, project_web_url: str) -> str:
    title = c.get("title", "").strip()
    title = linkify_refs(title, project_web_url)
    short_id = c.get("short_id") or (c.get("id", "")[:8])
    web_url = c.get("web_url") or f"{project_web_url}/-/commit/{c.get('id')}"
    author = c.get("author_name") or c.get("committer_name") or ""
    # print(json.dumps(c,indent=2))
    # exit(1)
    # 
    return f"- {title} ([{short_id}])"