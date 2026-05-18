import numpy as np

g = 9.81  # m/s^2


# ---------- Building definition ----------

def build_matrices(masses, stiffnesses):
    """
    Build mass [M] and stiffness [K] matrices for a 2-DOF shear building.

    masses:      [m1, m2] in kg
    stiffnesses: [k1, k2] in N/m (story lateral stiffnesses)
    """
    m1, m2 = masses
    k1, k2 = stiffnesses

    # 2-DOF shear model:
    #   DOF 1 = 1st floor displacement
    #   DOF 2 = 2nd floor displacement
    M = np.diag([m1, m2])

    K = np.array([
        [k1 + k2, -k2],
        [-k2,      k2]
    ], dtype=float)

    return M, K


def modal_analysis(M, K):
    """
    Solve [K]{phi} = lambda [M]{phi} and return modal properties.

    Returns
    -------
    omegas : array, shape (n_modes,)
        Circular frequencies (rad/s).
    periods : array, shape (n_modes,)
        Periods (s).
    modes : array, shape (n_dof, n_modes)
        Mass-normalized mode shapes (phi^T M phi = 1).
    gammas : array, shape (n_modes,)
        Modal participation factors Γ_r (for uniform lateral excitation).
    """
    # Solve generalized eigenproblem
    evals, evecs = np.linalg.eig(np.linalg.inv(M) @ K)

    # Sort by increasing eigenvalue (frequency)
    idx = np.argsort(evals)
    evals = evals[idx]
    evecs = evecs[:, idx]

    omegas = np.sqrt(evals)
    periods = 2.0 * np.pi / omegas

    # Mass-normalize modes and compute participation factors
    n_dof = M.shape[0]
    one = np.ones((n_dof, 1))
    modes = np.zeros_like(evecs)
    gammas = np.zeros(len(omegas))

    for r in range(len(omegas)):
        phi = evecs[:, r:r+1]  # column vector
        m_norm = float(phi.T @ M @ phi)
        phi = phi / np.sqrt(m_norm)  # mass-normalize: phi^T M phi = 1

        Gamma_r = float(phi.T @ M @ one)  # denominator = 1 after normalization

        modes[:, r] = phi[:, 0]
        gammas[r] = Gamma_r

    return omegas, periods, modes, gammas


def compute_modal_effective_masses(M, gammas):
    """
    Compute effective modal masses and participation ratios
    in the direction of [1, 1, ..., 1]^T.

    For mass-normalized modes:
        M_eff_r = Γ_r^2
        M_total_dir = 1^T M 1
        participation_ratio_r = M_eff_r / M_total_dir
    """
    n_dof = M.shape[0]
    one = np.ones((n_dof, 1))
    M_total_dir = float(one.T @ M @ one)  # total "directional" mass

    M_eff = gammas**2
    ratios = M_eff / M_total_dir
    return M_eff, ratios, M_total_dir


def compute_modal_drift_shapes(modes, story_heights):
    """
    For each mode, compute the story drift pattern that defines that mode.

    We re-normalize each mode so that the roof displacement = 1.0,
    then compute story drifts and drift ratios.

    Parameters
    ----------
    modes : ndarray, shape (n_dof, n_modes)
        Mode shapes (any normalization, typically mass-normalized).
    story_heights : tuple
        (h1, h2) story heights in meters.

    Returns
    -------
    mode_drifts : ndarray, shape (n_modes, 2)
        For each mode r: [Δ1_r, Δ2_r] in meters, with roof displacement = 1.0.
        (Units are consistent but arbitrary, since this is a shape.)
    mode_drift_ratios : ndarray, shape (n_modes, 2)
        For each mode r: [θ1_r, θ2_r] = drift / story_height.
    mode_floor_shapes : ndarray, shape (n_modes, 2)
        Normalized floor displacements for each mode with roof = 1.0:
        [u1_r, u2_r] (u2_r is exactly 1.0 by definition).
    """
    h1, h2 = story_heights
    n_dof, n_modes = modes.shape

    mode_drifts = np.zeros((n_modes, 2))
    mode_drift_ratios = np.zeros((n_modes, 2))
    mode_floor_shapes = np.zeros((n_modes, 2))

    for r in range(n_modes):
        phi = modes[:, r].astype(float).copy()

        # Normalize so roof (top floor) displacement = 1.0
        roof_disp = phi[-1]
        phi /= roof_disp

        u1, u2 = phi
        Δ1 = u1
        Δ2 = u2 - u1

        θ1 = Δ1 / h1
        θ2 = Δ2 / h2

        mode_floor_shapes[r, :] = [u1, u2]
        mode_drifts[r, :] = [Δ1, Δ2]
        mode_drift_ratios[r, :] = [θ1, θ2]

    return mode_drifts, mode_drift_ratios, mode_floor_shapes


def interpolate_sa(spectrum_dict, T):
    """
    Linear interpolation of Sa(T) in g units from a dict {T: Sa_g}.
    Extrapolates linearly outside the given range.
    """
    Ts = np.array(sorted(spectrum_dict.keys()), dtype=float)
    Sas = np.array([spectrum_dict[t] for t in Ts], dtype=float)
    return float(np.interp(T, Ts, Sas))


def response_spectrum_drifts(M, K, spectrum_dict, story_heights=(3.5, 3.5)):
    """
    Compute peak floor displacements and story drifts from a response spectrum
    using SRSS modal combination.

    Parameters
    ----------
    M, K : ndarray
        Mass and stiffness matrices.
    spectrum_dict : dict
        {period: Sa_in_g} for the chosen hazard level (e.g. 10% in 50 years).
    story_heights : tuple
        (h1, h2) story heights in meters.

    Returns
    -------
    periods : array
        Modal periods.
    u_max : array
        Peak absolute floor displacements [u1, u2] in meters.
    drifts : tuple
        (Δ1, Δ2) story drifts in meters.
    drift_ratios : tuple
        (θ1, θ2) story drift ratios (Δ/h).
    u_modal : ndarray, shape (2, n_modes)
        Modal contributions to floor displacements (signed).
    omegas, modes, gammas : modal data (for convenience).
    """
    omegas, periods, modes, gammas = modal_analysis(M, K)
    n_dof = M.shape[0]
    n_modes = len(omegas)

    u_modal = np.zeros((n_dof, n_modes))

    for r in range(n_modes):
        T_r = periods[r]
        Sa_g = interpolate_sa(spectrum_dict, T_r)  # in units of g
        Sa = Sa_g * g  # convert to m/s^2

        # Sa = ω^2 * Sd  =>  Sd = Sa / ω^2
        Sd = Sa / (omegas[r] ** 2)

        phi_r = modes[:, r]
        Gamma_r = gammas[r]

        # Generalized coordinate peak response
        q_r = Gamma_r * Sd  # meters

        # Physical DOF displacements for mode r
        u_modal[:, r] = phi_r * q_r

    # SRSS combination of modal responses
    u_max = np.sqrt(np.sum(u_modal ** 2, axis=1))  # shape (n_dof,)

    # Story drifts
    h1, h2 = story_heights
    drift1 = u_max[0]                  # 1st floor vs ground
    drift2 = u_max[1] - u_max[0]       # 2nd floor vs 1st floor

    drift_ratio1 = drift1 / h1
    drift_ratio2 = drift2 / h2

    drifts = (drift1, drift2)
    drift_ratios = (drift_ratio1, drift_ratio2)

    return periods, u_max, drifts, drift_ratios, u_modal, omegas, modes, gammas


# ---------- Example: two cities with different spectra ----------

# Replace with your PSHA-based spectra (for 10% in 50 years),
# values are Sa in units of g.
city_A_spectrum = {
    0.10: 0.40,
    0.20: 0.60,
    0.30: 0.80,
    0.50: 0.90,
    0.75: 0.80,
    1.00: 0.60,
    1.50: 0.40,
    2.00: 0.30,
}

city_B_spectrum = {
    0.10: 0.25,
    0.20: 0.40,
    0.30: 0.55,
    0.50: 0.65,
    0.75: 0.60,
    1.00: 0.45,
    1.50: 0.30,
    2.00: 0.20,
}


def main():
    # Building parameters (you can tweak these)
    masses = [200_000.0, 200_000.0]       # kg
    stiffnesses = [20e6, 20e6]            # N/m
    story_heights = (3.5, 3.5)            # m

    M, K = build_matrices(masses, stiffnesses)

    # ---- Modal properties ----
    omegas, periods, modes, gammas = modal_analysis(M, K)
    print("Modal analysis:")
    for i, (w, T, Gamma) in enumerate(zip(omegas, periods, gammas), start=1):
        print(f"  Mode {i}: T = {T:.3f} s, f = {w / (2*np.pi):.2f} Hz, Γ = {Gamma:.2f}")
    print()

    # ---- Modal effective masses / participation ----
    M_eff, ratios, M_total_dir = compute_modal_effective_masses(M, gammas)
    print("Modal effective masses and participation (direction [1,1]):")
    print(f"  Total directional mass = {M_total_dir:.2e} kg")
    for i in range(len(periods)):
        print(f"  Mode {i+1}: M_eff = {M_eff[i]:.2e} kg, "
              f"participation = {ratios[i]*100:.1f} %")
    print()

    # ---- Mode drift shapes ----
    mode_drifts, mode_drift_ratios, mode_floor_shapes = compute_modal_drift_shapes(
        modes, story_heights
    )

    print("Mode drift shapes (normalized so roof displacement = 1.0):")
    for r in range(len(periods)):
        u1, u2 = mode_floor_shapes[r]
        d1, d2 = mode_drifts[r]
        th1, th2 = mode_drift_ratios[r]
        print(f"  Mode {r+1}:")
        print(f"    Floor displacements [u1, u2] = [{u1:.3f}, {u2:.3f}] (u2 = 1.0)")
        print(f"    Story drifts Δ1 = {d1:.3f}, Δ2 = {d2:.3f}")
        print(f"    Drift ratios θ1 = {th1*100:.2f} %, θ2 = {th2*100:.2f} %")
    print()

    # ---- City A ----
    print("=== City A (e.g. softer site, higher spectral accelerations) ===")
    (periods_A, u_max_A, drifts_A, drift_ratios_A,
     u_modal_A, omegas_A, modes_A, gammas_A) = response_spectrum_drifts(
        M, K, city_A_spectrum, story_heights=story_heights
    )
    print(f"Peak floor displacements [u1, u2] = [{u_max_A[0]:.4f}, {u_max_A[1]:.4f}] m")
    print(f"Story drifts Δ1 = {drifts_A[0]:.4f} m, Δ2 = {drifts_A[1]:.4f} m")
    print(f"Drift ratios θ1 = {drift_ratios_A[0]*100:.2f} %, "
          f"θ2 = {drift_ratios_A[1]*100:.2f} %")
    print()

    # Modal contributions to story drifts (City A)
    drift1_modal = u_modal_A[0, :]                     # DOF1 vs ground
    drift2_modal = u_modal_A[1, :] - u_modal_A[0, :]   # DOF2 vs DOF1

    w1 = drift1_modal**2 / np.sum(drift1_modal**2)
    w2 = drift2_modal**2 / np.sum(drift2_modal**2)

    print("Modal contributions to story drifts (City A, SRSS weights):")
    for r in range(len(periods_A)):
        print(f"  Mode {r+1}: "
              f"contribution to Δ1 ≈ {w1[r]*100:.1f} %, "
              f"to Δ2 ≈ {w2[r]*100:.1f} %")
    print()

    # ---- City B ----
    print("=== City B (e.g. stiffer site, lower spectral accelerations) ===")
    (periods_B, u_max_B, drifts_B, drift_ratios_B,
     u_modal_B, omegas_B, modes_B, gammas_B) = response_spectrum_drifts(
        M, K, city_B_spectrum, story_heights=story_heights
    )
    print(f"Peak floor displacements [u1, u2] = [{u_max_B[0]:.4f}, {u_max_B[1]:.4f}] m")
    print(f"Story drifts Δ1 = {drifts_B[0]:.4f} m, Δ2 = {drifts_B[1]:.4f} m")
    print(f"Drift ratios θ1 = {drift_ratios_B[0]*100:.2f} %, "
          f"θ2 = {drift_ratios_B[1]*100:.2f} %")


if __name__ == "__main__":
    main()
