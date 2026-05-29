import numpy as np
from pyparsing import alphas

def mle_bernoulli(data):
    arr = np.asarray(data)

    if arr.size == 0:
        raise ValueError("Data tidak boleh kosong.")

    
    if arr.dtype == bool:
        arr = arr.astype(int)


    unique_vals = set(np.unique(arr).tolist())
    if not unique_vals.issubset({0, 1}):
        raise ValueError(
            f"Data harus berisi hanya 0/1 atau True/False. "
            f"Nilai ditemukan: {unique_vals}"
        )

    k = int(arr.sum())   
    n = int(arr.size)    

    return k / n

def mle_poisson(data):
   
    arr = np.asarray(data)
    if arr.size == 0:
        raise ValueError("Data tidak boleh kosong.")
    if np.any(arr < 0):
        raise ValueError("Data Poisson harus non-negatif.")
    if not np.all(np.equal(np.mod(arr, 1), 0)):
        raise ValueError("Data Poisson harus berupa bilangan cacah (integer).")

    return float(arr.sum()) / float(arr.size)

def beta_posterior(k, m):
    if k < 0 or m < 0:
        raise ValueError("Jumlah keberhasilan (k) dan kegagalan (m) harus non-negatif.")
    if k == 0 and m == 0:
        raise ValueError("Tidak dapat menentukan distribusi posterior dengan k=0 dan m=0.")

    alpha = 1 + k
    beta = 1 + m

    denom = alpha + beta - 2

    mode = (alpha - 1) / denom if denom > 0 else float("nan")

    mean = alpha / (alpha + beta)

    return {"alpha": alpha, "beta": beta, "mode": mode, "mean": mean}

