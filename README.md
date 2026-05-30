# stat-audit-Kelompok_3-sti-2025

# |stastikal audit terhadap repository open source github `microsoft/vscode`|



## Reseach Question

| No. | Question | Teknik |
| 1. | Berapakah estimasi peluang (persentase) sebuah Pull Request (PR) di proyek microsoft/vscode akan berhasil digabungkan (merged) dibandingkan dengan yang ditolak (closed)? | MLE Bernoulli (B), Beta Posterior(B), Confidence Interval Bernoulli (C),Credible Interval dari Beta posterior(C) |
| 2. | Apakah tingkat merge  PR berbeda secara signifikan antara kontributor User dan Bot di vscode? | Z-test dua sampel proporsi (D), Confidence Interval dua sampel (C) |
| 3. | Berapakah peluang sebuah issue acak di repositori microsoft/vscode akan tetap terbuka lebih lama dari 12 hari jika dihitung menggunakan simulasi Monte Carlo? | Simulasi Monte Carlo (E), Bloom Filter untuk cek duplikasi issue ID (E), MCMC Knapsack opsional sebagai analisis lanjutan (E) |