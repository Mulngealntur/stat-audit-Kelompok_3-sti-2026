import numpy as np

def mle_bernoulli(data):
    """
    Menghitung Maximum Likelihood Estimation (MLE) untuk distribusi Bernoulli.
    Referensi: Tsun (2020), halaman 254.
    Formula: p_hat = k / n
    """
    k = np.sum(data) # Jumlah PR yang sukses di-merge (angka 1)
    n = len(data)    # Total seluruh PR yang dianalisis
    p_hat = k / n if n > 0 else 0
    return {"p_hat": p_hat, "k": k, "n": n}

def beta_posterior(k, n):
    """
    Menghitung parameter Beta Posterior menggunakan asumsi prior seragam (Beta(1,1)).
    Referensi: Tsun (2020), halaman 269.
    Formula: alpha = k + 1, beta = (n - k) + 1
    """
    m = n - k # Jumlah PR yang ditolak (angka 0)
    alpha = k + 1
    beta = m + 1
    
    # Menghitung Mode dan Mean dari Beta Posterior (Tsun 2020, p. 269)
    mode = (alpha - 1) / (alpha + beta - 2) if (alpha + beta > 2) else 0
    mean = alpha / (alpha + beta)
    
    return {
        "alpha": alpha,
        "beta": beta,
        "mode": mode,
        "mean": mean
    }