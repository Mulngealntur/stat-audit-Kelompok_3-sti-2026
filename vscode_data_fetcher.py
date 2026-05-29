"""
Microsoft/VSCode GitHub Data Collector
=======================================
Mengumpulkan data dari repository microsoft/vscode di GitHub:
  - Issues        → data/raw/issues.csv        (~1300 closed issues)
  - Pull Requests → data/raw/pull_requests.csv (~750+ merged PRs)
  - Commits       → data/raw/commits.csv

VSCode menggunakan GitHub Issues secara penuh, sehingga
semua data bisa diambil langsung dari GitHub API.

Penggunaan:
  python vscode_data_fetcher.py --token YOUR_TOKEN
  python vscode_data_fetcher.py --token YOUR_TOKEN --max-pages 13
  python vscode_data_fetcher.py --token YOUR_TOKEN --skip-commits
"""

import os
import time
import argparse
from datetime import datetime

import requests
import pandas as pd


# ── Konfigurasi ───────────────────────────────────────────────────────────────

REPO_OWNER = "microsoft"
REPO_NAME  = "vscode"
API_ROOT   = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
OUTPUT_DIR = "data/raw"
PAGE_DELAY = 0.4


# ── Utilitas GitHub API ───────────────────────────────────────────────────────

def build_headers(token=None):
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def handle_rate_limit(resp_headers):
    remaining = int(resp_headers.get("X-RateLimit-Remaining", 999))
    if remaining < 5:
        reset_ts  = int(resp_headers.get("X-RateLimit-Reset", time.time() + 60))
        wait_secs = max(reset_ts - time.time(), 0) + 3
        print(f"    ⏳ Quota hampir habis, menunggu {int(wait_secs)} detik...")
        time.sleep(wait_secs)


def collect_pages(endpoint, query_params, headers, page_limit=13, item_label="item"):
    """Iterasi semua halaman dari endpoint GitHub API."""
    collected, page = [], 1
    while page <= page_limit:
        params = {**query_params, "page": page, "per_page": 100}
        resp   = requests.get(endpoint, params=params, headers=headers, timeout=30)

        if resp.status_code in (403, 429):
            reset_ts  = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_secs = max(reset_ts - time.time(), 0) + 5
            print(f"    ⚠  Rate limited. Menunggu {int(wait_secs)} detik...")
            time.sleep(wait_secs)
            continue

        if resp.status_code == 404:
            raise RuntimeError(f"Endpoint tidak ditemukan: {endpoint}")

        if resp.status_code != 200:
            print(f"    ✗  HTTP {resp.status_code} hal. {page}: {resp.json().get('message', '')}")
            break

        page_data = resp.json()
        if not page_data:
            break

        collected.extend(page_data)
        quota_left = int(resp.headers.get("X-RateLimit-Remaining", 999))
        print(f"    Hal. {page}/{page_limit} → +{len(page_data)} {item_label} "
              f"| total: {len(collected)} | sisa quota: {quota_left}")

        handle_rate_limit(resp.headers)
        if len(page_data) < 100:
            break
        page += 1
        time.sleep(PAGE_DELAY)

    return collected


def display_rate_limit(headers):
    try:
        resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if resp.status_code == 200:
            info      = resp.json()["rate"]
            reset_str = datetime.fromtimestamp(info["reset"]).strftime("%H:%M:%S")
            print(f"🔑 GitHub API → limit: {info['limit']} | "
                  f"sisa: {info['remaining']} | reset: {reset_str}")
            if info["remaining"] < 30:
                print("⚠  Quota rendah — gunakan --token!")
    except Exception as e:
        print(f"⚠  Tidak bisa cek rate limit: {e}")


# ── Issues dari GitHub ────────────────────────────────────────────────────────

def retrieve_issues(headers, page_limit):
    """
    Ambil closed issues dari microsoft/vscode.
    GitHub API mengembalikan PR juga di endpoint /issues,
    jadi perlu difilter — item yang punya key 'pull_request' dibuang.
    """
    print(f"\n📋 Mengambil Issues (closed) dari {REPO_OWNER}/{REPO_NAME}...")
    raw = collect_pages(
        endpoint     = f"{API_ROOT}/issues",
        query_params = {"state": "closed", "sort": "created", "direction": "desc"},
        headers      = headers,
        page_limit   = page_limit,
        item_label   = "items",
    )
    # Filter: buang yang merupakan PR
    issues_only = [item for item in raw if "pull_request" not in item]
    print(f"  → {len(issues_only)} issues murni (dari {len(raw)} item total)")
    return issues_only


def transform_issues(raw_list):
    """Konversi list dict GitHub Issues menjadi DataFrame terstruktur."""
    records = []
    for issue in raw_list:
        assignees   = [a.get("login", "") for a in issue.get("assignees", [])]
        label_names = [l.get("name", "")  for l in issue.get("labels",    [])]
        records.append({
            "issue_id"      : issue.get("id"),
            "number"        : issue.get("number"),
            "title"         : issue.get("title", "").strip(),
            "state"         : issue.get("state"),
            "author"        : issue.get("user", {}).get("login"),
            "author_type"   : issue.get("user", {}).get("type"),
            "assignees"     : "|".join(assignees),
            "labels"        : "|".join(label_names),
            "milestone"     : (issue.get("milestone") or {}).get("title"),
            "comments_count": issue.get("comments", 0),
            "created_at"    : issue.get("created_at"),
            "updated_at"    : issue.get("updated_at"),
            "closed_at"     : issue.get("closed_at"),
            "body_length"   : len(issue.get("body") or ""),
            "url"           : issue.get("html_url"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    for col in ("created_at", "updated_at", "closed_at"):
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    now = pd.Timestamp.now(tz="UTC")
    df["days_open"]    = (df["closed_at"].fillna(now) - df["created_at"]).dt.days.clip(lower=0)
    df["year_created"] = df["created_at"].dt.year
    df["month"]        = df["created_at"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m")
    df["has_assignee"] = df["assignees"].str.len() > 0
    df["label_count"]  = df["labels"].apply(lambda x: len(x.split("|")) if x else 0)

    return df


# ── Pull Requests dari GitHub ─────────────────────────────────────────────────

def retrieve_pull_requests(headers, page_limit):
    print(f"\n🔀 Mengambil Pull Requests (closed) dari {REPO_OWNER}/{REPO_NAME}...")
    raw = collect_pages(
        endpoint     = f"{API_ROOT}/pulls",
        query_params = {"state": "closed", "sort": "created", "direction": "desc"},
        headers      = headers,
        page_limit   = page_limit,
        item_label   = "pull requests",
    )
    print(f"  → {len(raw)} pull requests diambil")
    return raw


def transform_pull_requests(raw_list):
    records = []
    for pr in raw_list:
        label_names = [l.get("name", "") for l in pr.get("labels", [])]
        reviewers   = [r.get("login", "") for r in pr.get("requested_reviewers", [])]
        records.append({
            "pr_id"           : pr.get("id"),
            "number"          : pr.get("number"),
            "title"           : pr.get("title", "").strip(),
            "state"           : pr.get("state"),
            "author"          : pr.get("user", {}).get("login"),
            "author_type"     : pr.get("user", {}).get("type"),
            "is_draft"        : pr.get("draft", False),
            "labels"          : "|".join(label_names),
            "reviewers"       : "|".join(reviewers),
            "base_branch"     : pr.get("base", {}).get("ref"),
            "head_branch"     : pr.get("head", {}).get("ref"),
            "created_at"      : pr.get("created_at"),
            "updated_at"      : pr.get("updated_at"),
            "closed_at"       : pr.get("closed_at"),
            "merged_at"       : pr.get("merged_at"),
            "merge_commit_sha": pr.get("merge_commit_sha"),
            "comments"        : pr.get("comments", 0),
            "review_comments" : pr.get("review_comments", 0),
            "commits"         : pr.get("commits", 0),
            "additions"       : pr.get("additions", 0),
            "deletions"       : pr.get("deletions", 0),
            "changed_files"   : pr.get("changed_files", 0),
            "url"             : pr.get("html_url"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    for col in ("created_at", "updated_at", "closed_at", "merged_at"):
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    now = pd.Timestamp.now(tz="UTC")
    df["is_merged"]      = df["merged_at"].notna()
    df["net_line_delta"] = df["additions"] - df["deletions"]
    df["is_large"]       = df["changed_files"] > 10
    df["days_to_close"]  = (df["closed_at"].fillna(now) - df["created_at"]).dt.days.clip(lower=0)
    df["month"]          = df["created_at"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m")
    df["year_created"]   = df["created_at"].dt.year

    return df


# ── Commits dari GitHub ───────────────────────────────────────────────────────

def retrieve_commits(headers, page_limit):
    print(f"\n📝 Mengambil Commits dari {REPO_OWNER}/{REPO_NAME}...")
    raw = collect_pages(
        endpoint     = f"{API_ROOT}/commits",
        query_params = {"sha": "main"},
        headers      = headers,
        page_limit   = page_limit,
        item_label   = "commits",
    )
    print(f"  → {len(raw)} commits diambil")
    return raw


def transform_commits(raw_list):
    records = []
    for commit in raw_list:
        detail       = commit.get("commit", {})
        author_info  = detail.get("author", {})
        committer    = detail.get("committer", {})
        gh_author    = commit.get("author") or {}
        gh_committer = commit.get("committer") or {}

        records.append({
            "sha"            : commit.get("sha"),
            "message_summary": detail.get("message", "").split("\n")[0].strip(),
            "message_length" : len(detail.get("message", "")),
            "author_name"    : author_info.get("name"),
            "author_email"   : author_info.get("email"),
            "author_login"   : gh_author.get("login"),
            "authored_at"    : author_info.get("date"),
            "committer_name" : committer.get("name"),
            "committer_login": gh_committer.get("login"),
            "committed_at"   : committer.get("date"),
            "comment_count"  : detail.get("comment_count", 0),
            "url"            : commit.get("html_url"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    for col in ("authored_at", "committed_at"):
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    df["year"]        = df["authored_at"].dt.year
    df["month"]       = df["authored_at"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m")
    df["day_of_week"] = df["authored_at"].dt.day_name()
    df["hour_of_day"] = df["authored_at"].dt.hour

    return df


# ── Simpan CSV ────────────────────────────────────────────────────────────────

def export_csv(df, filename, description=""):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"    ✔ {path} ({description}) → {len(df)} baris, {df.shape[1]} kolom")
    return path


# ── Ringkasan ─────────────────────────────────────────────────────────────────

def print_summary(df_issues, df_prs, df_commits):
    print("\n" + "=" * 55)
    print("  RINGKASAN HASIL PENGAMBILAN DATA")
    print("=" * 55)

    if not df_issues.empty:
        print(f"  Issues          : {len(df_issues):>5} baris")
        print(f"    └─ Closed     : {(df_issues['state'] == 'closed').sum():>5}")
    else:
        print("  Issues          :     0 baris ⚠")

    if not df_prs.empty:
        print(f"  Pull Requests   : {len(df_prs):>5} baris")
        print(f"    └─ Merged     : {df_prs['is_merged'].sum():>5}")
        print(f"    └─ Not merged : {(~df_prs['is_merged']).sum():>5}")

    if not df_commits.empty:
        print(f"  Commits         : {len(df_commits):>5} baris")

    print(f"\n  File tersimpan di: {os.path.abspath(OUTPUT_DIR)}/")
    print("=" * 55)


# ── Argumen CLI ───────────────────────────────────────────────────────────────

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Ambil data microsoft/vscode dari GitHub → issues, pull_requests, commits (.csv)"
    )
    parser.add_argument("--token",        type=str, default=None,
                        help="GitHub Personal Access Token (sangat disarankan)")
    parser.add_argument("--max-pages",    type=int, default=13,
                        help="Maks halaman per endpoint (default: 13 = ~1300 item)")
    parser.add_argument("--skip-commits", action="store_true",
                        help="Lewati pengambilan commits (hemat quota API)")
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args    = parse_arguments()
    headers = build_headers(args.token)

    print("=" * 55)
    print("  Microsoft/VSCode GitHub Data Collector")
    print("=" * 55)
    display_rate_limit(headers)

    start = time.time()

    # Issues
    raw_issues = retrieve_issues(headers, page_limit=args.max_pages)
    df_issues  = transform_issues(raw_issues)

    # Pull Requests
    raw_prs = retrieve_pull_requests(headers, page_limit=args.max_pages)
    df_prs  = transform_pull_requests(raw_prs)

    # Commits
    df_commits = pd.DataFrame()
    if not args.skip_commits:
        raw_commits = retrieve_commits(headers, page_limit=args.max_pages)
        df_commits  = transform_commits(raw_commits)

    # Simpan CSV
    print("\n💾 Menyimpan file CSV...")
    export_csv(df_issues,  "issues.csv",       "closed issues")
    export_csv(df_prs,     "pull_requests.csv", "closed/merged PRs")
    if not df_commits.empty:
        export_csv(df_commits, "commits.csv",  "commits dengan timestamp")

    elapsed = time.time() - start
    print(f"\n✅ Selesai dalam {elapsed:.1f} detik.")
    print_summary(df_issues, df_prs, df_commits)


if __name__ == "__main__":
    main()