import hashlib
import math
import random
from typing import Callable, List, Tuple


# =============================================================================
# 1. MONTE CARLO PROBABILITY ESTIMATION
# =============================================================================

def estimate_probability(event_fn: Callable[[], bool], n_trials: int = 50_000) -> dict:
    """
    Mengestimasi probabilitas suatu event menggunakan simulasi Monte Carlo.

    Metode ini tidak memerlukan asumsi distribusi, sehingga cocok untuk data
    dengan distribusi right-skewed seperti days_open pada microsoft/vscode
    (skewness = 1.69, ditemukan oleh Member A).

    Formula (Tsun, 2020, p. 314–315):
        P̂(event) = jumlah_sukses / N_trials
        SE        = sqrt(P̂ * (1 - P̂) / N_trials)

    Konvergensi dijamin oleh Hukum Bilangan Besar (Law of Large Numbers):
    semakin besar N_trials, estimasi semakin mendekati probabilitas sejati.

    Parameters
    ----------
    event_fn : Callable[[], bool]
        Fungsi tanpa argumen yang mensimulasikan satu trial.
        Mengembalikan True jika event terjadi, False jika tidak.
        Contoh untuk RQ3 vscode:
            lambda: np.random.choice(valid_days) > 12
    n_trials : int, optional
        Jumlah trial Monte Carlo (default: 50_000).

    Returns
    -------
    dict dengan kunci:
        'p_hat'     : float — estimasi probabilitas
        'std_error' : float — standard error estimasi
        'n_trials'  : int   — jumlah trial yang dijalankan
        'successes' : int   — jumlah trial di mana event terjadi

    Reference
    ---------
    Tsun (2020), p. 314–315.

    Example
    -------
    >>> import random
    >>> result = estimate_probability(lambda: random.random() < 0.3, n_trials=10_000)
    >>> 0.25 < result['p_hat'] < 0.35
    True
    """
    if n_trials <= 0:
        raise ValueError("n_trials harus lebih besar dari 0.")

    successes = sum(1 for _ in range(n_trials) if event_fn())
    p_hat     = successes / n_trials
    std_error = math.sqrt(p_hat * (1 - p_hat) / n_trials)

    return {
        "p_hat"    : p_hat,
        "std_error": std_error,
        "n_trials" : n_trials,
        "successes": successes,
    }


# =============================================================================
# 2. BLOOM FILTER
# =============================================================================

class BloomFilter:
    """
    Struktur data probabilistik yang efisien untuk uji keanggotaan (membership test).

    Bloom Filter menggunakan k fungsi hash independen untuk memetakan setiap item
    ke k posisi dalam bit array berukuran m. Operasi add() dan contains() berjalan
    dalam O(k) — konstan terhadap jumlah item.

    Properti penting:
      - TIDAK PERNAH false negative: jika item tidak ada, pasti dilaporkan tidak ada.
      - BISA false positive: item yang tidak ada bisa dilaporkan ada, dengan FPR teoritis
        sebesar (1 - (1 - 1/m)^n)^k.

    Motivasi untuk microsoft/vscode:
      Dengan 1.300 PR dari dua tipe kontributor (User dan Bot) yang terbukti berbeda
      merge rate-nya secara signifikan (Z=5.4433, p≈0, Member D), Bloom Filter dapat
      digunakan sebagai mekanisme deduplication yang hemat memori pada pipeline
      CI/monitoring untuk menghindari pemrosesan PR yang sama dua kali.

    Formula FPR teoritis (Tsun, 2020, p. 329):
        FPR = (1 - (1 - 1/m)^n)^k

    Parameters
    ----------
    k : int
        Jumlah fungsi hash. Nilai lebih besar → FPR lebih rendah, tapi lebih lambat.
    m : int
        Ukuran bit array. Nilai lebih besar → FPR lebih rendah, tapi lebih boros memori.

    Reference
    ---------
    Tsun (2020), p. 329.

    Example
    -------
    >>> bf = BloomFilter(k=3, m=13_000)
    >>> bf.add("PR_1234")
    >>> bf.contains("PR_1234")
    True
    >>> bf.theoretical_fpr(n=1300)
    0.000...
    """

    def __init__(self, k: int, m: int):
        """
        Inisialisasi Bloom Filter dengan k hash function dan bit array berukuran m.

        Parameters
        ----------
        k : int — jumlah hash function (≥ 1)
        m : int — ukuran bit array (≥ 1)
        """
        if k < 1:
            raise ValueError("k (jumlah hash function) harus ≥ 1.")
        if m < 1:
            raise ValueError("m (ukuran bit array) harus ≥ 1.")

        self.k = k
        self.m = m
        self._bits       = [False] * m  # bit array, semua diinisialisasi 0
        self._n_inserted = 0            # counter item yang dimasukkan

    # ------------------------------------------------------------------
    # Private helper
    # ------------------------------------------------------------------

    def _hash_positions(self, item: str) -> List[int]:
        """
        Menghasilkan k posisi bit untuk item menggunakan k SHA-256 yang di-salt.

        Setiap hash function disimulasikan dengan hashing "i:item" (i = 0, 1, ..., k-1),
        memastikan independensi antar hash function.

        Parameters
        ----------
        item : str — item yang akan di-hash

        Returns
        -------
        List[int] — k posisi dalam [0, m)
        """
        positions = []
        item_str  = str(item)
        for i in range(self.k):
            salted = f"{i}:{item_str}".encode("utf-8")
            digest = hashlib.sha256(salted).hexdigest()
            pos    = int(digest, 16) % self.m
            positions.append(pos)
        return positions

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def add(self, item: str) -> None:
        """
        Masukkan item ke dalam Bloom Filter.

        Mengeset k bit pada posisi hasil hash menjadi True.
        Operasi ini berjalan dalam O(k).

        Parameters
        ----------
        item : str — item yang dimasukkan (contoh: nomor PR, issue ID, contributor login)

        Reference
        ---------
        Tsun (2020), p. 329.
        """
        for pos in self._hash_positions(item):
            self._bits[pos] = True
        self._n_inserted += 1

    def contains(self, item: str) -> bool:
        """
        Uji apakah item mungkin ada dalam filter (membership test).

        Mengembalikan True jika SEMUA k posisi bit untuk item bernilai True.
        - True  → item *mungkin* ada (bisa false positive)
        - False → item *pasti tidak* ada (tidak pernah false negative)

        Parameters
        ----------
        item : str — item yang akan diuji

        Returns
        -------
        bool

        Reference
        ---------
        Tsun (2020), p. 329.
        """
        return all(self._bits[pos] for pos in self._hash_positions(item))

    def theoretical_fpr(self, n: int) -> float:
        """
        Hitung False Positive Rate (FPR) teoritis setelah n item dimasukkan.

        Formula (Tsun, 2020, p. 329):
            FPR = (1 - (1 - 1/m)^n)^k

        Parameters
        ----------
        n : int — jumlah item yang telah dimasukkan ke dalam filter

        Returns
        -------
        float — FPR teoritis dalam [0, 1]

        Reference
        ---------
        Tsun (2020), p. 329.

        Example
        -------
        >>> bf = BloomFilter(k=3, m=13_000)
        >>> bf.theoretical_fpr(n=1300)   # 1300 PR vscode
        0.00...
        """
        if n < 0:
            raise ValueError("n harus ≥ 0.")
        inner = (1 - 1 / self.m) ** n
        return (1 - inner) ** self.k

    # ------------------------------------------------------------------
    # Properties & dunder
    # ------------------------------------------------------------------

    @property
    def n_inserted(self) -> int:
        """Jumlah item yang telah dimasukkan ke dalam filter."""
        return self._n_inserted

    def __repr__(self) -> str:
        fpr = self.theoretical_fpr(self._n_inserted)
        return (
            f"BloomFilter("
            f"k={self.k}, "
            f"m={self.m}, "
            f"n_inserted={self._n_inserted}, "
            f"current_fpr={fpr:.8f})"
        )


# =============================================================================
# 3. MCMC KNAPSACK
# =============================================================================

def mcmc_knapsack(
    items   : List[Tuple[str, int, int]],
    capacity: int,
    n_iter  : int = 100_000,
) -> dict:
    """
    Mendekati solusi 0/1 Knapsack menggunakan Markov Chain Monte Carlo (MCMC)
    dengan skema penerimaan Metropolis–Hastings yang dimodifikasi (greedy accept).

    Masalah Knapsack:
        Diberikan N item, masing-masing dengan bobot (weight) dan nilai (value),
        cari subset yang MEMAKSIMALKAN total value tanpa melebihi capacity.

    Motivasi untuk microsoft/vscode:
        Temuan dari layer sebelumnya mengidentifikasi beberapa area yang perlu
        intervensi — terutama Bot merge rate yang hanya 70.5% vs User 89.9%
        (Z=5.4433, Member D). MCMC Knapsack membantu maintainer MEMPRIORITASKAN
        intervensi mana yang paling efisien dalam keterbatasan kapasitas sprint.

    Mengapa MCMC bukan Dynamic Programming?
        - DP optimal untuk N kecil, namun MCMC scalable ke ratusan intervensi.
        - MCMC dapat dimodifikasi untuk reward probabilistik tanpa mengubah struktur.
        - Sesuai dengan materi Tsun (2020) p. 317–320.

    Algoritma (Tsun, 2020, p. 317–320):
        1. State awal: semua item tidak dipilih (vektor biner {0,1}^N, semua 0)
        2. Proposal: flip satu bit acak (tambah atau hapus satu item)
        3. Tolak langsung jika proposal tidak feasible (bobot > capacity)
        4. Terima proposal jika nilai baru ≥ nilai saat ini (greedy accept)
        5. Simpan state terbaik yang pernah ditemui selama iterasi

    Parameters
    ----------
    items : List[Tuple[str, int, int]]
        Daftar item dalam format (nama, bobot, nilai).
        - nama   : str — nama/identitas item (contoh: "Bot PR quality gate")
        - bobot  : int — effort yang dibutuhkan (contoh: hari-orang per sprint)
        - nilai  : int — dampak/manfaat yang diharapkan (skor 1–30)
    capacity : int
        Batas maksimum total bobot yang dapat ditampung knapsack (kapasitas sprint).
    n_iter : int, optional
        Jumlah iterasi MCMC (default: 100_000).

    Returns
    -------
    dict dengan kunci:
        'best_items'  : List[str]  — nama item-item yang dipilih
        'best_value'  : int        — total nilai dari kombinasi terpilih
        'best_weight' : int        — total bobot dari kombinasi terpilih
        'n_iter'      : int        — jumlah iterasi yang dijalankan
        'accept_rate' : float      — proporsi proposal yang diterima (0–1)

    Reference
    ---------
    Tsun (2020), p. 317–320.

    Example
    -------
    >>> items = [("A", 10, 15), ("B", 20, 25), ("C", 15, 18)]
    >>> result = mcmc_knapsack(items, capacity=30, n_iter=50_000)
    >>> result['best_weight'] <= 30
    True
    """
    if not items:
        return {
            "best_items" : [],
            "best_value" : 0,
            "best_weight": 0,
            "n_iter"     : n_iter,
            "accept_rate": 0.0,
        }

    if capacity <= 0:
        raise ValueError("capacity harus > 0.")

    n       = len(items)
    names   = [it[0] for it in items]
    weights = [it[1] for it in items]
    values  = [it[2] for it in items]

    # Helper functions
    def total_weight(state: List[int]) -> int:
        return sum(w for w, s in zip(weights, state) if s)

    def total_value(state: List[int]) -> int:
        return sum(v for v, s in zip(values, state) if s)

    def is_feasible(state: List[int]) -> bool:
        return total_weight(state) <= capacity

    # --- Inisialisasi: knapsack kosong ---
    current_state = [0] * n
    current_value = 0
    best_state    = current_state[:]
    best_value    = 0
    accepts       = 0

    # --- Iterasi MCMC ---
    for _ in range(n_iter):
        # Langkah 2: proposal — flip satu bit acak
        flip_idx = random.randrange(n)
        proposal = current_state[:]
        proposal[flip_idx] = 1 - proposal[flip_idx]

        # Langkah 3: tolak jika tidak feasible
        if not is_feasible(proposal):
            continue

        # Langkah 4: terima jika nilai baru ≥ nilai saat ini
        proposal_value = total_value(proposal)
        if proposal_value >= current_value:
            current_state = proposal
            current_value = proposal_value
            accepts      += 1

            # Langkah 5: update best
            if current_value > best_value:
                best_value = current_value
                best_state = current_state[:]

    accept_rate = accepts / n_iter
    best_items  = [names[i]   for i in range(n) if best_state[i]]
    best_weight = sum(weights[i] for i in range(n) if best_state[i])

    return {
        "best_items" : best_items,
        "best_value" : best_value,
        "best_weight": best_weight,
        "n_iter"     : n_iter,
        "accept_rate": accept_rate,
    }


# =============================================================================
# SELF-TEST — jalankan: python simulation.py
# =============================================================================

if __name__ == "__main__":
    import numpy as np

    print("=" * 65)
    print("simulation.py — Self-Test | microsoft/vscode context")
    print("=" * 65)

    # -----------------------------------------------------------------
    # 1. Monte Carlo — RQ3 vscode
    # -----------------------------------------------------------------
    print("\n[1] Monte Carlo — P(days_open > 12 hari)")
    print("    Konteks: Member A menemukan semua 590 issues ≤ 12 hari")
    print("    Ekspektasi: P̂ ≈ 0.0000")

    # Simulasi distribusi days_open vscode (max=12, skewed ke 0)
    np.random.seed(42)
    raw_p = [0.30, 0.20, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04,
             0.03, 0.03, 0.02, 0.01, 0.005, 0.005, 0.003, 0.002]
    total_p = sum(raw_p)
    norm_p  = [p / total_p for p in raw_p]
    simulated_days = np.random.choice(
        [0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        size=590,
        p=norm_p
    )

    mc_result = estimate_probability(
        event_fn=lambda: np.random.choice(simulated_days) > 12,
        n_trials=50_000
    )
    print(f"    P̂(issue > 12 hari) : {mc_result['p_hat']:.4f}")
    print(f"    Standard Error      : {mc_result['std_error']:.4f}")
    print(f"    Sukses / Trial      : {mc_result['successes']:,} / {mc_result['n_trials']:,}")

    # -----------------------------------------------------------------
    # 2. Bloom Filter — 1300 PR vscode
    # -----------------------------------------------------------------
    print("\n[2] Bloom Filter — 1300 PR microsoft/vscode")
    print("    k=3, m=13000 (10x jumlah item)")

    K_HASH = 3
    M_BITS = 13_000   # 1300 PR × 10
    N_PR   = 1_300

    bf = BloomFilter(k=K_HASH, m=M_BITS)
    pr_ids = [str(i) for i in range(1, N_PR + 1)]
    for pr_id in pr_ids:
        bf.add(pr_id)

    print(f"    {bf}")
    print(f"    FPR teoritis (n=1300): {bf.theoretical_fpr(N_PR):.6f}")
    print(f"    PR '1' ada dalam filter   : {bf.contains('1')}   (ekspektasi True)")
    print(f"    PR '99999' ada dalam filter: {bf.contains('99999')}  (ekspektasi False)")

    # -----------------------------------------------------------------
    # 3. MCMC Knapsack — prioritisasi intervensi vscode
    # -----------------------------------------------------------------
    print("\n[3] MCMC Knapsack — prioritisasi intervensi vscode")
    print("    Kapasitas: 35 hari-orang")

    items = [
        ("Bot PR quality gate (CI lint+test)", 15, 28),
        ("Filter/validasi PR Bot sebelum review", 8, 20),
        ("SLA review ≤ 12 jam untuk PR baru", 12, 25),
        ("Otomasi label issue (auto-triage)", 6, 15),
        ("Review latency monitoring dashboard", 10, 18),
        ("Template PR standar kontributor baru", 5, 12),
        ("Notifikasi stale PR (>30 hari)", 4, 10),
        ("Panduan kontributor (CONTRIBUTING.md)", 7, 14),
    ]

    kp = mcmc_knapsack(items=items, capacity=35, n_iter=100_000)
    print(f"    Item terpilih  : {kp['best_items']}")
    print(f"    Total nilai    : {kp['best_value']}")
    print(f"    Total bobot    : {kp['best_weight']} / 35 hari-orang")
    print(f"    Accept rate    : {kp['accept_rate']:.4f}")
    assert kp['best_weight'] <= 35, "ERROR: bobot melebihi kapasitas!"

    print("\n" + "=" * 65)
    print("Semua self-test selesai tanpa error.")
    print("=" * 65)