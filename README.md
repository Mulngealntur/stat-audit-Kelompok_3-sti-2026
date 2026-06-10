# stat-audit-Kelompok_3-sti-2025

# | stastikal audit terhadap repository open source github `microsoft/vscode` |



## Reseach Question

| No. | Question | Teknik |
|-----|----------|--------|
| 1. | Berapakah estimasi peluang (persentase) sebuah Pull Request (PR) di proyek microsoft/vscode akan berhasil digabungkan (merged) dibandingkan dengan yang ditolak (closed)? | MLE Bernoulli (B), Beta Posterior(B), Confidence Interval Bernoulli (C),Credible Interval dari Beta posterior(C) |
| 2. | Apakah tingkat merge  PR berbeda secara signifikan antara kontributor User dan Bot di vscode? | Z-test dua sampel proporsi (D), Confidence Interval dua sampel (C) |
| 3. | Berapakah peluang sebuah issue acak di repositori microsoft/vscode akan tetap terbuka lebih lama dari 12 hari jika dihitung menggunakan simulasi Monte Carlo? | Simulasi Monte Carlo (E), Bloom Filter untuk cek duplikasi issue ID (E), MCMC Knapsack opsional sebagai analisis lanjutan (E) |

## Meet Our Team

| ~ | Nama | NIM | Role |
|---|------|-----|------|
| A | Multazam Ahmad | 1519625033 | Data Engineer |
| B | Dhanu Refian Majid | 1519625059 | Estimation Analyst |
| C | Keymal Alghifary | 1519625044 | Inference Analyst |
| D | Arista Imanuela Berutu | 1519625011 | Hypothesis Analyst |
| E | Muhammad Fadhil | 1519625061 | Computation Analyst |

## Struktur Repository

```
stat-audit-moby-sti-2025/
  → README.md
  → AI_USAGE_LOG.md
  → data/
      → raw/        (data asli GitHub API)
      → clean/      (dataset.csv, issues.csv)
  → src/
      → estimator.py   [Member B]
      → inference.py   [Member C]
      → hypothesis.py  [Member D]
      → simulation.py  [Member E]
  → notebooks/
      → 01_eda.ipynb
      → 02_estimation.ipynb
      → 03_confidence_interval.ipynb
      → 04_hypothesis_testing.ipynb
      → 05_simulation.ipynb
  → report/
      → statistical_health_report.pdf
  → presentation/
      → video_link.md
  → requirements.txt
```

## Cara memakai/menjalankan

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ambil data dan masukan github token(jalankan sekali)
python vscode_data_fetcher.py --token YOUR_TOKEN

# 3. Bersihkan data raw
python vscode_data_cleaner.py

# 3. Jalankan notebook secara urut
jupyter notebook
```
## Hasil Penemuan

## Sumber Pengambilan Data

- **Repository:** https://github.com/microsoft/vscode
- **Tanggal pengambilan data:** 27 Mei 2026
- **Endpoint API:** GitHub REST API v3
- **Keterbatasan:** Data diambil [X] halaman x 100 item via pagination
