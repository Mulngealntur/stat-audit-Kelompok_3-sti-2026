import math
 
Z_CRITICAL = {
    0.10: 1.645,
    0.05: 1.960,
    0.01: 2.576,
}
 
def mean(data):
    return sum(data) / len(data)
 
def z_test_one_sample(data, mu0, sigma, alpha=0.05, tail="two"):
    """
    Uji Z satu sampel (σ populasi diketahui).
 
    Parameter:
    - data  : list nilai sampel
    - mu0   : rata-rata yang diklaim H₀
    - sigma : standar deviasi populasi
    - alpha : tingkat signifikansi (0.10 / 0.05 / 0.01)
    - tail  : "two", "left", atau "right"
    """
    n     = len(data)
    xbar  = mean(data)
    se    = sigma / math.sqrt(n)
    z     = (xbar - mu0) / se
    z_crit = Z_CRITICAL.get(alpha, 1.960)
 
    print("=" * 50)
    print("  UJI Z SATU SAMPEL")
    print("-" * 50)
    print(f"  Data     : {data}")
    print(f"  n        : {n}")
    print(f"  x̄       : {xbar:.4f}")
    print(f"  μ₀ (H₀) : {mu0}")
    print(f"  σ        : {sigma}")
    print(f"  SE       : {se:.4f}")
    print(f"  Z hitung : {z:.4f}")
    print("-" * 50)
    print(f"  H₀ : μ = {mu0}")
 
    if tail == "two":
        print(f"  H₁ : μ ≠ {mu0}  (two-tailed)")
        reject = abs(z) > z_crit
        print(f"  Z kritis : ±{z_crit}  (α={alpha})")
    elif tail == "right":
        print(f"  H₁ : μ > {mu0}  (right-tailed)")
        reject = z > z_crit
        print(f"  Z kritis : +{z_crit}  (α={alpha})")
    else:
        print(f"  H₁ : μ < {mu0}  (left-tailed)")
        reject = z < -z_crit
        print(f"  Z kritis : -{z_crit}  (α={alpha})")
 
    print("-" * 50)
    if reject:
        print(f"  Keputusan  : TOLAKk H₀")
        print(f"  Kesimpulan : Cukup bukti μ ≠ {mu0}")
    else:
        print(f"  Keputusan  : GAGAL TOLAK H₀")
        print(f"  Kesimpulan : Tidak cukup bukti untuk menolak H₀")
    print("=" * 50)
 
    return z, reject
 
 
if __name__ == "__main__":
    # Contoh: apakah rata-rata response time server = 200ms?
    z_test_one_sample(
        data=[215, 198, 230, 205, 222, 189, 210],
        mu0=200,
        sigma=15,
        alpha=0.05,
        tail="two"
    )