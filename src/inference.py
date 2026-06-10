import numpy as np
from scipy.stats import norm, beta


def confidence_interval(theta_hat, sigma, n, confidence=0.95):
    
    if n <= 0:
        raise ValueError("Sample size (n) Harus lebih besar dari 0.")

    z = norm.ppf((1 + confidence) / 2)

    margin_error = z * sigma / np.sqrt(n)

    lower_bound = theta_hat - margin_error
    upper_bound = theta_hat + margin_error

    return {
        "theta_hat": theta_hat,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "margin_error": margin_error,
        "confidence": confidence
    }


def ci_bernoulli(k, n, confidence=0.95):
    
    if n <= 0:
        raise ValueError("n harus lebih besar 0.")

    if k < 0 or k > n:
        raise ValueError("k harus memenuhi 0 <= k <= n.")

    p_hat = k / n

    sigma = np.sqrt(p_hat * (1 - p_hat))

    result = confidence_interval(
        theta_hat=p_hat,
        sigma=sigma,
        n=n,
        confidence=confidence
    )

    result["p_hat"] = p_hat

    return result


def ci_poisson(data, confidence=0.95):
    
    data = np.asarray(data)

    if len(data) == 0:
        raise ValueError("Data tidak boleh kosong.")

    if np.any(data < 0):
        raise ValueError("Poisson data harus non-negatif.")

    lambda_hat = np.mean(data)

    sigma = np.std(data, ddof=1)

    result = confidence_interval(
        theta_hat=lambda_hat,
        sigma=sigma,
        n=len(data),
        confidence=confidence
    )

    result["lambda_hat"] = lambda_hat

    return result


def credible_interval(alpha, beta_param, confidence=0.95):
    
    if alpha <= 0 or beta_param <= 0:
        raise ValueError("alpha and beta harus positif.")

    tail = (1 - confidence) / 2

    lower_bound = beta.ppf(
        tail,
        alpha,
        beta_param
    )

    upper_bound = beta.ppf(
        1 - tail,
        alpha,
        beta_param
    )

    return {
        "alpha": alpha,
        "beta": beta_param,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "confidence": confidence
    }