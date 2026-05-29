"""
VSCode GitHub Data Cleaner
===========================
Membersihkan hasil fetch dari vscode_data_fetcher.py

Input  → data/raw/
  - issues.csv
  - pull_requests.csv
  - commits.csv

Output → data/clean/
  - issues_clean.csv
  - pull_requests_clean.csv
  - commits_clean.csv

Cara penggunaan:
  1. Jalankan dulu vscode_data_fetcher.py untuk menghasilkan data/raw/
  2. Baru jalankan script ini:

       python vscode_data_cleaner.py

  3. Hasil cleaning tersimpan di folder data/clean/
     Laporan ringkasan ditampilkan di terminal.

Opsi tambahan:
  python vscode_data_cleaner.py --input-dir data/raw
  python vscode_data_cleaner.py --output-dir data/clean
  python vscode_data_cleaner.py --input-dir data/raw --output-dir data/clean
"""

import os
import re
import argparse

import pandas as pd


# ── Konfigurasi default ───────────────────────────────────────────────────────

INPUT_DIR  = "data/raw"
OUTPUT_DIR = "data/clean"


# ── Utilitas umum ─────────────────────────────────────────────────────────────

def load_csv(filename, input_dir):
    """Muat file CSV dari folder input. Kembalikan DataFrame kosong jika tidak ada."""
    path = os.path.join(input_dir, filename)
    if not os.path.exists(path):
        print(f"  ⚠  File tidak ditemukan: {path} — dilewati.")
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    print(f"  📂 Dimuat: {path} → {len(df)} baris, {df.shape[1]} kolom")
    return df


def save_csv(df, filename, output_dir):
    """Simpan DataFrame ke folder output."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  ✔  Disimpan: {path} → {len(df)} baris, {df.shape[1]} kolom")


def strip_non_ascii(text):
    """Hapus karakter non-ASCII (emoji, simbol aneh) dari string."""
    if not isinstance(text, str):
        return text
    return re.sub(r"[^\x00-\x7F]+", " ", text).strip()


def normalize_text_column(series):
    """Strip whitespace, lowercase, dan hapus karakter non-ASCII."""
    return (
        series.astype(str)
              .str.strip()
              .str.lower()
              .apply(strip_non_ascii)
              .replace("nan", pd.NA)
    )


def report_missing(df, label):
    """Tampilkan ringkasan missing values sebelum dan sesudah cleaning."""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print(f"    ✅ {label}: tidak ada missing values")
    else:
        print(f"    📊 {label} — missing values tersisa:")
        for col, count in missing.items():
            pct = count / len(df) * 100
            print(f"       {col}: {count} ({pct:.1f}%)")


# ── Cleaning: Issues ──────────────────────────────────────────────────────────

def clean_issues(df):
    """
    Langkah cleaning untuk issues.csv:
      1. Hapus duplikat berdasarkan issue_id
      2. Konversi kolom timestamp ke datetime
      3. Isi missing values dengan nilai default
      4. Normalisasi teks (title, state)
      5. Validasi nilai kategorik (state hanya 'open'/'closed')
      6. Cap outlier pada days_open
      7. Buang baris tanpa issue_id atau created_at
    """
    if df.empty:
        return df

    original_len = len(df)
    print(f"\n  🔧 Cleaning issues ({original_len} baris)...")

    # 1. Hapus duplikat
    df = df.drop_duplicates(subset=["issue_id"]).copy()
    print(f"     Duplikat dihapus : {original_len - len(df)} baris")

    # 2. Konversi timestamp (mungkin terbaca sebagai string saat load CSV)
    for col in ("created_at", "updated_at", "closed_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    # 3. Isi missing values
    df["milestone"]      = df["milestone"].fillna("no milestone")
    df["assignees"]      = df["assignees"].fillna("")
    df["labels"]         = df["labels"].fillna("")
    df["comments_count"] = df["comments_count"].fillna(0).astype(int)
    df["body_length"]    = df["body_length"].fillna(0).astype(int)

    # 4. Normalisasi teks
    df["title"] = normalize_text_column(df["title"])
    df["state"] = df["state"].str.strip().str.lower()

    # 5. Validasi nilai kategorik state
    valid_states = {"open", "closed"}
    invalid_mask = ~df["state"].isin(valid_states)
    if invalid_mask.sum() > 0:
        print(f"     State tidak valid dihapus : {invalid_mask.sum()} baris")
        df = df[~invalid_mask]

    # 6. Cap outlier days_open (cap di persentil 99)
    if "days_open" in df.columns:
        cap = df["days_open"].quantile(0.99)
        outliers = (df["days_open"] > cap).sum()
        df["days_open"] = df["days_open"].clip(upper=cap)
        print(f"     Outlier days_open di-cap  : {outliers} baris (cap={cap:.0f} hari)")

    # 7. Buang baris kritis yang kosong
    before = len(df)
    df = df.dropna(subset=["issue_id", "created_at"])
    print(f"     Baris tanpa ID/tanggal    : {before - len(df)} baris dihapus")

    # Recalculate label_count setelah cleaning
    df["label_count"] = df["labels"].apply(lambda x: len(str(x).split("|")) if x else 0)

    report_missing(df, "Issues")
    print(f"  ✅ Issues: {original_len} → {len(df)} baris")
    return df


# ── Cleaning: Pull Requests ───────────────────────────────────────────────────

def clean_pull_requests(df):
    """
    Langkah cleaning untuk pull_requests.csv:
      1. Hapus duplikat berdasarkan pr_id
      2. Konversi kolom timestamp ke datetime
      3. Isi missing values dengan nilai default
      4. Normalisasi teks (title, state)
      5. Validasi nilai numerik (tidak boleh negatif)
      6. Cap outlier pada additions, deletions, days_to_close
      7. Buang baris tanpa pr_id atau created_at
    """
    if df.empty:
        return df

    original_len = len(df)
    print(f"\n  🔧 Cleaning pull requests ({original_len} baris)...")

    # 1. Hapus duplikat
    df = df.drop_duplicates(subset=["pr_id"]).copy()
    print(f"     Duplikat dihapus : {original_len - len(df)} baris")

    # 2. Konversi timestamp
    for col in ("created_at", "updated_at", "closed_at", "merged_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    # 3. Isi missing values
    df["labels"]           = df["labels"].fillna("")
    df["reviewers"]        = df["reviewers"].fillna("")
    df["merge_commit_sha"] = df["merge_commit_sha"].fillna("")
    df["base_branch"]      = df["base_branch"].fillna("unknown")
    df["head_branch"]      = df["head_branch"].fillna("unknown")

    for col in ("comments", "review_comments", "commits", "additions", "deletions", "changed_files"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 4. Normalisasi teks
    df["title"] = normalize_text_column(df["title"])
    df["state"] = df["state"].str.strip().str.lower()

    # 5. Validasi nilai numerik tidak negatif
    for col in ("additions", "deletions", "changed_files", "commits"):
        if col in df.columns:
            neg = (df[col] < 0).sum()
            if neg > 0:
                df[col] = df[col].clip(lower=0)
                print(f"     Nilai negatif di-clip ({col}): {neg} baris")

    # 6. Cap outlier
    for col in ("additions", "deletions", "days_to_close"):
        if col in df.columns:
            cap = df[col].quantile(0.99)
            outliers = (df[col] > cap).sum()
            df[col] = df[col].clip(upper=cap)
            if outliers > 0:
                print(f"     Outlier {col} di-cap : {outliers} baris (cap={cap:.0f})")

    # Recalculate is_merged dan net_line_delta setelah cleaning
    df["is_merged"]      = df["merged_at"].notna()
    df["net_line_delta"] = df["additions"] - df["deletions"]

    # 7. Buang baris kritis yang kosong
    before = len(df)
    df = df.dropna(subset=["pr_id", "created_at"])
    print(f"     Baris tanpa ID/tanggal    : {before - len(df)} baris dihapus")

    report_missing(df, "Pull Requests")
    print(f"  ✅ Pull Requests: {original_len} → {len(df)} baris")
    return df


# ── Cleaning: Commits ─────────────────────────────────────────────────────────

def clean_commits(df):
    """
    Langkah cleaning untuk commits.csv:
      1. Hapus duplikat berdasarkan sha
      2. Konversi kolom timestamp ke datetime
      3. Isi missing values dengan nilai default
      4. Normalisasi teks (message_summary)
      5. Cap outlier pada message_length
      6. Buang baris tanpa sha atau authored_at
    """
    if df.empty:
        return df

    original_len = len(df)
    print(f"\n  🔧 Cleaning commits ({original_len} baris)...")

    # 1. Hapus duplikat
    df = df.drop_duplicates(subset=["sha"]).copy()
    print(f"     Duplikat dihapus : {original_len - len(df)} baris")

    # 2. Konversi timestamp
    for col in ("authored_at", "committed_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    # 3. Isi missing values
    df["author_login"]   = df["author_login"].fillna("unknown")
    df["committer_login"]= df["committer_login"].fillna("unknown")
    df["author_name"]    = df["author_name"].fillna("unknown")
    df["committer_name"] = df["committer_name"].fillna("unknown")
    df["author_email"]   = df["author_email"].fillna("")
    df["comment_count"]  = pd.to_numeric(df["comment_count"], errors="coerce").fillna(0).astype(int)
    df["message_length"] = pd.to_numeric(df["message_length"], errors="coerce").fillna(0).astype(int)

    # 4. Normalisasi teks
    df["message_summary"] = normalize_text_column(df["message_summary"])

    # 5. Cap outlier message_length
    if "message_length" in df.columns:
        cap      = df["message_length"].quantile(0.99)
        outliers = (df["message_length"] > cap).sum()
        df["message_length"] = df["message_length"].clip(upper=cap)
        if outliers > 0:
            print(f"     Outlier message_length di-cap : {outliers} baris (cap={cap:.0f})")

    # 6. Buang baris kritis yang kosong
    before = len(df)
    df = df.dropna(subset=["sha", "authored_at"])
    print(f"     Baris tanpa SHA/tanggal   : {before - len(df)} baris dihapus")

    report_missing(df, "Commits")
    print(f"  ✅ Commits: {original_len} → {len(df)} baris")
    return df


# ── Ringkasan akhir ───────────────────────────────────────────────────────────

def print_summary(results):
    print("\n" + "=" * 55)
    print("  RINGKASAN CLEANING")
    print("=" * 55)
    for label, (before, after) in results.items():
        selisih = before - after
        print(f"  {label:<20}: {before:>5} → {after:>5} baris "
              f"({selisih} dihapus)")
    print(f"\n  File tersimpan di: {os.path.abspath(OUTPUT_DIR)}/")
    print("=" * 55)


# ── Argumen CLI ───────────────────────────────────────────────────────────────

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Cleaning data hasil vscode_data_fetcher.py.\n"
            "Jalankan SETELAH vscode_data_fetcher.py selesai."
        )
    )
    parser.add_argument(
        "--input-dir", type=str, default=INPUT_DIR,
        help=f"Folder input berisi file raw CSV (default: {INPUT_DIR})"
    )
    parser.add_argument(
        "--output-dir", type=str, default=OUTPUT_DIR,
        help=f"Folder output untuk file cleaned CSV (default: {OUTPUT_DIR})"
    )
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_arguments()

    print("=" * 55)
    print("  VSCode GitHub Data Cleaner")
    print("=" * 55)
    print(f"  Input  : {os.path.abspath(args.input_dir)}")
    print(f"  Output : {os.path.abspath(args.output_dir)}")

    # ── Load ──────────────────────────────────────────────
    print("\n📂 Memuat file raw...")
    df_issues = load_csv("issues.csv",       args.input_dir)
    df_prs    = load_csv("pull_requests.csv", args.input_dir)
    df_commits= load_csv("commits.csv",       args.input_dir)

    # ── Clean ─────────────────────────────────────────────
    print("\n🧹 Proses cleaning...")
    df_issues_clean  = clean_issues(df_issues)
    df_prs_clean     = clean_pull_requests(df_prs)
    df_commits_clean = clean_commits(df_commits)

    # ── Simpan ────────────────────────────────────────────
    print("\n💾 Menyimpan hasil cleaning...")
    save_csv(df_issues_clean,  "issues_clean.csv",       args.output_dir)
    save_csv(df_prs_clean,     "pull_requests_clean.csv", args.output_dir)
    save_csv(df_commits_clean, "commits_clean.csv",       args.output_dir)

    # ── Ringkasan ─────────────────────────────────────────
    print_summary({
        "Issues"        : (len(df_issues),  len(df_issues_clean)),
        "Pull Requests" : (len(df_prs),     len(df_prs_clean)),
        "Commits"       : (len(df_commits), len(df_commits_clean)),
    })


if __name__ == "__main__":
    main()