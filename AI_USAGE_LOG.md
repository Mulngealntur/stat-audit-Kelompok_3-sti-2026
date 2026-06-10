## AI Usage Disclosure
### **Member:** Multazam Ahmad — Data Engineer | **Tools used:** Claude, Chatgpt
 
| Task | Tool | Prompt summary | Output modified? |
|------|------|----------------|-----------------|
| Scaffolding struktur notebook | Claude | "Rapihkan Notebook saya" | Ya — semua interpretasi ditulis ulang secara mandiri |
| Boilerplate kode plotting | Claude | "Template histogram + boxplot dengan seaborn" | Ya — disesuaikan dengan kolom dataset |
 
**Ditulis sepenuhnya tanpa AI:** Semua sel interpretasi/markdown analisis, variable selection rationale, ringkasan EDA.

## AI Usage Disclosure

**Member:** [Keymal] — [Inference Analyst] | **Claude:** 
| Task                          | Tool   | Prompt summary                                    | Output modified?        |
| ----------------------------- | ------ | ------------------------------------------------- | ----------------------- |
|Implementasi confidence interval | Claude | "contoh implementasi confidence interval" | Ya — menyesuaikan dengan struktur projek | 
| Debugging kode | Claude | "Periksa error dan validasi input" | Ya

Ditulis sepenuhnya tanpa AI: Seluruh interpretasi hasil analisis dan kesimpulan notebook.

# Notebook 04 — Hypothesis Testing Analysis

## Research Questions
**Q2 (Inferensi & Hipotesis):** Apakah tingkat keberhasilan penggabungan (*merge rate*) Pull Request berbeda secara signifikan antara kontributor User (Manusia) dan Bot di repositori `microsoft/vscode`?



| Item | Detail |
| :--- | :--- |
| **Research Questions Addressed** | Q2: Apakah tingkat keberhasilan penggabungan (*merge rate*) Pull Request berbeda secara signifikan antara kontributor User (Manusia) dan Bot di repositori `microsoft/vscode` jika diuji menggunakan pendekatan *Two-Sample Z-Test*? |
| **Nama** | Arista Imanuela Berutu |
| **Role** | Hypothesis Analyst (Member D) |
| **Notebook** | `04_hypothesis_testing.ipynb` |
| **Dependencies** | `data/clean/pull_requests_clean.csv`, `src/hypothesis.py` |

---

## AI Usage Disclosure

**Member:** Arista Imanuela Berutu | Hypothesis Analyst (Member D) | **Tools used:** Gemini

| Task | Tool | Prompt summary | Output modified? |
| :--- | :--- | :--- | :--- |
| Scaffolding struktur rumus statistik | Gemini | "Bantu buat fungsi z_test_one_sample dan dua populasi sesuai rumus Tsun (2020)" | Ya — Diintegrasikan ke dalam modul `src/hypothesis.py` dan disesuaikan parameter data asli |
| Boilerplate kode visualisasi distribusi | Gemini | "Template plot distribusi normal z-test menggunakan matplotlib" | Ya — Disesuaikan dengan posisi nilai Z-score riil data VS Code |

**Ditulis sepenuhnya tanpa AI:** Semua sel interpretasi analitis, peninjauan angka statistik deskriptif dari data bersih `pull_requests_clean.csv` (1.124 User & 176 Bot), perumusan draf hipotesis $H_0$ dan $H_a$, serta penulisan analisis 6 Prosedur Langkah Pengujian Hipotesis secara mandiri.

---

## Prosedur Analisis Pengujian Hipotesis

### 1. Rumusan Hipotesis
Pengujian ini ditujukan untuk mengevaluasi secara empiris apakah rata-rata/proporsi tingkat keberhasilan penggabungan (*merge rate*) Pull Request antara kelompok kontributor User (Manusia) dan Bot pada proyek open-source `microsoft/vscode` menunjukkan perbedaan yang signifikan.

* **Hipotesis Nol ($H_0$):** $\mu_1 = \mu_2$ (Rata-rata/proporsi tingkat keberhasilan merge PR antara kontributor User dan Bot adalah sama)
* **Hipotesis Alternatif ($H_a$):** $\mu_1 \neq \mu_2$ (Rata-rata/proporsi tingkat keberhasilan merge PR antara kontributor User dan Bot adalah berbeda secara signifikan)

*Tingkat signifikansi ($\alpha$) yang ditetapkan secara teoretis adalah 0.05.*

## AI Usage Disclosure

**Member:** Muhammad Fadhil — Computation Analyst &nbsp;|&nbsp; **Tools used:** Claude

| # | Task | Tool | Prompt summary | Output modified? |
|---|---|---|---|---|
| 1 | Scaffold notebook sesuai data aktual kelompok | Claude | "buatkan 05_simulation siap jalan di VS Code" | Ya — interpretasi & kesimpulan ditulis sendiri |

**Ditulis sepenuhnya tanpa AI:**
- Semua cell `### Interpretasi`
- Research question di header
- Kesimpulan akhir (Summary cell)