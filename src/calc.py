import numpy as np


# Left Riemann Approximation Method
def LRAM(lower, upper, func, integration_samples):
    """""Left Riemann Sum: evaluate at the start of the interval."""

    dx = (upper - lower) / integration_samples

    x_values = np.linspace(lower, upper - dx, integration_samples)
    y_values = func(x_values)

    return np.sum(y_values) * dx


# Right Riemann Approximation Method
def RRAM(lower, upper, func, integration_samples):
    """Right Riemann Sum: evaluate at the end of the interval."""

    dx = (upper - lower) / integration_samples

    x_values = np.linspace(lower + dx, upper, integration_samples)
    y_values = func(x_values)

    return np.sum(y_values) * dx

# Midpoint Riemann Approximation Method
def MRAM(lower, upper, func, integration_samples):
    """Midpoint Riemann Sum: evaluate at the midpoint of the interval."""

    dx = (upper - lower) / integration_samples

    x_values = np.linspace(lower + dx / 2, upper - dx / 2, integration_samples)
    y_values = func(x_values)

    return np.sum(y_values) * dx

# Trapezoidal Rule
def TRAP(lower, upper, func, integration_samples):
    """
    Trapezoidal Rule: evaluate at both the start and end of the interval,
    then average the results.
    """

    dx = (upper - lower) / integration_samples

    x_values = np.linspace(lower, upper, integration_samples + 1)
    y_values = func(x_values)

    y_sum = 2 * np.sum(y_values) - y_values[0] - y_values[-1]

    return y_sum * dx * 0.5
