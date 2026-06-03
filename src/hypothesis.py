<<<<<<< Updated upstream

=======
import numpy as np
from scipy.stats import norm

def z_test_one_sample(x_bar, mu0, sigma, n, alternative='two-sided', alpha=0.05):
    """
    Melakukan Uji Z Satu Sampel untuk rata-rata.
    Formula: Z = (x_bar - mu0) / (sigma / sqrt(n))
    """
    z_stat = (x_bar - mu0) / (sigma / np.sqrt(n))
    
    if alternative == 'two-sided':
        p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    elif alternative == 'less':
        p_value = norm.cdf(z_stat)
    elif alternative == 'greater':
        p_value = 1 - norm.cdf(z_stat)
    else:
        raise ValueError("Alternative harus 'two-sided', 'less', atau 'greater'")
        
    if p_value < alpha:
        decision = "reject H0"
        interpretation = f"Karena p-value ({p_value:.4f}) < alpha ({alpha}), terdapat bukti statistik yang cukup untuk menolak H0."
    else:
        decision = "fail to reject H0"
        interpretation = f"Karena p-value ({p_value:.4f}) >= alpha ({alpha}), tidak cukup bukti statistik untuk menolak H0."
        
    return {
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "decision": decision,
        "interpretation": interpretation
    }

def z_test_two_sample(x_bar1, x_bar2, sigma1, sigma2, n1, n2, alternative='two-sided', alpha=0.05):
    """
    Melakukan Uji Z Dua Sampel untuk membandingkan dua rata-rata populasi.
    Formula: Z = (x_bar1 - x_bar2) / sqrt((sigma1^2 / n1) + (sigma2^2 / n2))
    """
    denominator = np.sqrt((sigma1**2 / n1) + (sigma2**2 / n2))
    z_stat = (x_bar1 - x_bar2) / denominator
    
    if alternative == 'two-sided':
        p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    elif alternative == 'less':
        p_value = norm.cdf(z_stat)
    elif alternative == 'greater':
        p_value = 1 - norm.cdf(z_stat)
    else:
        raise ValueError("Alternative harus 'two-sided', 'less', atau 'greater'")
        
    if p_value < alpha:
        decision = "reject H0"
        interpretation = f"Karena p-value ({p_value:.4f}) < alpha ({alpha}), terdapat perbedaan signifikan antara kedua kelompok."
    else:
        decision = "fail to reject H0"
        interpretation = f"Karena p-value ({p_value:.4f}) >= alpha ({alpha}), tidak ada perbedaan signifikan antara kedua kelompok."
        
    return {
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "decision": decision,
        "interpretation": interpretation
    }
>>>>>>> Stashed changes

