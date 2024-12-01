#!/usr/bin/env python3
"""
This script provides functions to calculate angular conversions and mappings
between alpha and beta angles based on the cosine and sine laws. It creates
maps to facilitate efficient conversion and interpolation between these angles.

Modules:
    - math: Provides mathematical functions such as trigonometric calculations.
    - Config: Contains predefined configuration parameters like constants and limits.

Functions:
    - ang_conv(alpha_deg): Calculates the beta angle corresponding to the given alpha angle.
    - alpha_beta_maps(): Generates mappings between alpha and beta angles, including interpolated values for missing beta keys.

"""

import math
import Config


def ang_conv(alpha_deg):
    """
    Converts an alpha angle (in degrees) to a beta angle using cosine and sine laws.

    Args:
        alpha_deg (float): Alpha angle in degrees.

    Returns:
        int: Beta angle in degrees, rounded and adjusted based on the configuration.

    Details:
        - The function first converts alpha from degrees to radians.
        - It computes the components A, B, C, D, E, and F based on the cosine and sine laws.
        - The beta angle is determined from the roots of a quadratic equation derived from these components.
        - If the alpha angle is below a configured limit, the beta angle is negated.
    """
    alpha = math.radians(alpha_deg)

    # Compute components for the quadratic equation
    A = (Config.l2 - Config.l5 * math.cos(alpha)) / Config.l3
    B = -1 * (Config.l1 + Config.l5 * math.sin(alpha)) / Config.l3
    BS = (B ** 2)
    C = ((Config.l4 / Config.l3) ** 2) - 1
    D = (A ** 2) + BS
    E = A * (BS - C) / D
    F = (0.25 * ((BS - C) ** 2) - BS) / D

    # Calculate the discriminant and solve for roots
    discriminant = E ** 2 - 4 * F
    if discriminant < 0:
        discriminant = 0  # Handle negative discriminants due to numerical issues
    root = (-E + (discriminant ** 0.5)) / 2

    # Compute the angle in radians and convert to degrees
    angle_radians = math.acos(root)
    angle_degrees = math.degrees(angle_radians)

    # Adjust beta based on configuration
    if alpha_deg < Config.lim:
        angle_degrees *= -1
    return round(angle_degrees) + Config.s_cal


def alpha_beta_maps():
    """
    Generates maps for alpha-to-beta and beta-to-alpha conversions, including interpolation.

    Returns:
        tuple: Two dictionaries:
            - alpha_to_beta_map: Mapping from alpha angles to corresponding beta angles.
            - beta_to_alpha_map: Mapping from beta angles to lists of alpha angles.

    Details:
        - Creates maps for alpha values in the range [-16, 45].
        - Ensures that beta-to-alpha mapping covers all integer beta values within the range.
        - Missing beta keys are interpolated using weighted averages of the nearest keys.
    """
    print("Create alpha, beta maps")

    # Initialize maps
    alpha_to_beta_map = {}  # Maps alpha -> beta
    beta_to_alpha_map = {}  # Maps beta -> list of alphas

    # Populate maps with direct conversions
    for alpha in range(-16, 46):
        beta = ang_conv(alpha)
        alpha_to_beta_map[alpha] = beta

        # Add to beta-to-alpha map
        if beta in beta_to_alpha_map:
            beta_to_alpha_map[beta].append(alpha)
        else:
            beta_to_alpha_map[beta] = [alpha]

    # Get the range of beta values
    min_beta = min(beta_to_alpha_map.keys())
    max_beta = max(beta_to_alpha_map.keys())

    # Interpolate missing beta values
    for beta in range(min_beta, max_beta + 1):
        if beta not in beta_to_alpha_map:
            # Find nearest lower and higher beta keys
            lower_beta = max(k for k in beta_to_alpha_map if k < beta)
            higher_beta = min(k for k in beta_to_alpha_map if k > beta)

            # Calculate weights for interpolation
            weight_lower = (higher_beta - beta) / (higher_beta - lower_beta)
            weight_higher = (beta - lower_beta) / (higher_beta - lower_beta)

            # Interpolate alpha values as weighted averages
            lower_alphas = beta_to_alpha_map[lower_beta]
            higher_alphas = beta_to_alpha_map[higher_beta]
            beta_to_alpha_map[beta] = [
                weight_lower * alpha_low + weight_higher * alpha_high
                for alpha_low, alpha_high in zip(lower_alphas, higher_alphas)
            ]

    return alpha_to_beta_map, beta_to_alpha_map
