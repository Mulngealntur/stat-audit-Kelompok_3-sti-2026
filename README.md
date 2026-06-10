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
```bash
# 1.Tingkat keberhasilan merge Pull Request sangat tinggi
# - Dari 1.300 Pull Request yang dianalisis, sekitar 87,23% berhasil di-merge.
# - Confidence Interval 95% berada pada rentang 85,42%–89,04%, menunjukkan estimasi yang stabil dan tingkat ketidakpastian yang rendah.
# 2.Hasil estimasi Bayesian memperkuat temuan MLE
# - Distribusi posterior Beta menghasilkan nilai yang sangat dekat dengan estimasi MLE.
# - Konsistensi antara pendekatan Frequentist dan Bayesian meningkatkan keyakinan bahwa probabilitas merge yang diperoleh merepresentasikan kondisi repositori secara akurat.
# 3.Terdapat perbedaan signifikan antara performa User dan Bot
# - Merge rate User mencapai 89,86%, sedangkan Bot hanya 70,45%.
# - Uji Z menghasilkan Z = 5,4433 dan p-value < 0,05, sehingga perbedaan tersebut terbukti signifikan secara statistik.
# 4.Kontribusi manusia lebih efektif dibandingkan bot
# - Pull Request yang diajukan oleh manusia memiliki peluang diterima lebih tinggi dibandingkan Pull Request yang dibuat oleh bot.
# - Temuan ini mengindikasikan perlunya evaluasi terhadap kualitas dan proses otomatisasi bot.
# 5.Pengelolaan issue berjalan sangat responsif
# - Simulasi Monte Carlo sebanyak 50.000 iterasi menunjukkan probabilitas issue tetap terbuka lebih dari 12 hari sebesar 0%.
# - Seluruh issue dalam sampel berhasil diselesaikan dalam waktu ≤ 12 hari.
# 6.Bloom Filter terbukti efisien untuk penyaringan data
# - False Positive Rate (FPR) teoritis hanya 0,0862%.
# - Pengujian menunjukkan seluruh data valid terdeteksi dengan benar dan data palsu berhasil ditolak.
# - Solusi ini layak digunakan untuk pemrosesan event Pull Request secara real-time dengan penggunaan memori yang rendah.
# 7.Prioritas perbaikan repositori berfokus pada kualitas bot
# - Optimasi MCMC Knapsack mengidentifikasi tiga intervensi paling berdampak:
# - Bot PR Quality Gate (CI lint & test wajib)
# - Validasi Pull Request bot sebelum review
# - Dashboard monitoring waktu review
# - Ketiga proyek tersebut memberikan nilai dampak tertinggi dengan tetap memenuhi batas kapasitas kerja tim.
# 8.Kesimpulan penemuan
# - Repositori VS Code memiliki proses review dan integrasi kontribusi yang sangat baik, ditunjukkan oleh merge rate yang tinggi dan penyelesaian issue yang cepat.
# - Area yang paling membutuhkan perhatian adalah peningkatan kualitas Pull Request yang dihasilkan oleh bot agar performanya dapat mendekati kontribusi manusia.
```

## Sumber Pengambilan Data

- **Repository:** https://github.com/microsoft/vscode
- **Tanggal pengambilan data:** 27 Mei 2026
- **Endpoint API:** GitHub REST API v3
- **Keterbatasan:** Data diambil [X] halaman x 100 item via pagination
