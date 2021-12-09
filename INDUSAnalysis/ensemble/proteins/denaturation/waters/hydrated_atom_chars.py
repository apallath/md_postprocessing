"""
Plots phi-series and generates pie-chart movies of
A) Hydration with phi, of
- atoms from charged or hydrophobic or hydrophilic residues
- polar or nonpolar atoms (as per the Kapcha-Rossky scale)
- buried or surface atoms
B) Hydration of atoms belonging to different secondary structure classes
C) Hydration of atoms belonging to different secondary structure groups
"""
import argparse
import os
from os.path import expanduser
import pickle

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from tqdm import tqdm
import MDAnalysis as mda

# Use text-only Matplotlib backend
matplotlib.use('Agg')

###############################################################################
# Functions returning values to plot on pie chart movie frames
###############################################################################


def buried_surface_valueslist(indices, protein_heavy, buried_indicator):
    n_atoms_buried = 0
    n_atoms_surface = 0

    for heavyidx in indices:
        if buried_indicator[heavyidx]:
            n_atoms_buried += 1
        else:
            n_atoms_surface += 1

    return np.array([n_atoms_buried, n_atoms_surface])


def charged_hydrophobic_hydrophilic_residues_valueslist(indices, protein_heavy):
    # TODO MOD: Residue hydrates when over 1/2 of its heavy atoms hydrate
    n_res_charged = 0
    n_res_hydrophobic = 0
    n_res_hydrophilic = 0

    hydrophobic = ['ALA', 'VAL', 'LEU', 'ILE', 'PHE', 'PRO', 'TRP']

    for res in protein_heavy.atoms[indices].residues:
        if np.abs(res.charge) > 0.5:
            n_res_charged += 1
        elif res.resname in hydrophobic:
            n_res_hydrophobic += 1
        else:
            n_res_hydrophilic += 1

    return(np.array([n_res_charged, n_res_hydrophobic, n_res_hydrophilic]))


def polar_nonpolar_atoms_valueslist(indices, protein_heavy, kr_scale, ff):
    n_atoms_polar = 0
    n_atoms_nonpolar = 0

    for heavyidx in indices:
        atom = protein_heavy.atoms[heavyidx]
        atom_res = atom.residue.resname
        atom_name = atom.name

        # Force-field specific corrections
        if ff == "amber99sb":
            if atom_name in ["OC1", "OC2"]:
                atom_name = "O"

        atom_polar = kr_scale.get("{} {}".format(atom_res, atom_name))
        if atom_polar == 1:
            n_atoms_polar += 1
        elif atom_polar == -1:
            n_atoms_nonpolar += 1
        else:
            print("Exception at {} {}".format(atom_res, atom_name))

    return(np.array([n_atoms_polar, n_atoms_nonpolar]))


def sec_struct_class_valueslist(indices, protein_heavy, stride_dict):
    mapper = {"H": 0, "G": 1, "I": 2, "E": 3, "T": 4, "B": 5, "C": 6}
    comp = [0, 0, 0, 0, 0, 0, 0]

    for heavyidx in indices:
        atom = protein_heavy.atoms[heavyidx]
        resid = atom.residue.resid
        comp[mapper[stride_dict[resid + 1]]] += 1

    return(np.array(comp))


def sec_struct_group_valueslist(indices, protein_heavy, all_groups, stride_group):
    idx_to_group = dict()
    group_to_idx = dict()

    for gidx, gname in enumerate(all_groups):
        idx_to_group[gidx] = gname
        group_to_idx[gname] = gidx

    comp = len(all_groups) * [0]

    for i in indices:
        atomi = protein_heavy.atoms[i]
        residi = atomi.residue.resid
        atomi_group = stride_group[residi + 1]

        comp[group_to_idx[atomi_group]] += 1

    return(np.array(comp))


def nonzero_autopct(pct):
    return ('%.2f' % pct) if pct > 0 else ''


###############################################################################
# Main calculation function
###############################################################################


def hydrated_atom_chars(protname,
                        pklfile,
                        structfile,
                        phi_bins,
                        buried_npyfile, buried_surface_imgfile, buried_surface_movieformat,
                        restype_imgfile, restype_movieformat,
                        kr_pklfile, ff, atomtype_imgfile, atomtype_movieformat,
                        stride_pklclass, ssclass_imgfile, ssclass_movieformat):
                        # ssgroup_imgfile, ssgroup_imgformat):
    print("Already generated the images?")
    print("Here are the bash commands to stitch them into movies:")
    for movieformat in [buried_surface_movieformat, restype_movieformat, atomtype_movieformat]:
        print("ffmpeg -r 5 -i {} -vcodec mpeg4 -y -vb 40M {}".format(
              movieformat.format("%05d"), movieformat.split(".")[0] + ".mp4"))
    ############################################################################
    # Load data
    ############################################################################

    # phi_i* data
    with open(pklfile, "rb") as infile:
        phi_i_star_data = pickle.load(infile)

    phi_i_stars = phi_i_star_data['phi_i_stars']

    # load structure
    u = mda.Universe(structfile)
    protein_heavy = u.select_atoms("protein and not name H*")

    ############################################################################
    # Bin phi_i* data
    ############################################################################
    phivals = np.hstack((np.array([np.inf, phi_bins[0]]),
                         np.linspace(phi_bins[0], phi_bins[1], int(phi_bins[2]))))

    hyd_indices = {}

    for i in range(1, len(phivals)):
        hyd_indices[(phivals[i], phivals[i - 1])] = np.argwhere(np.logical_and(phi_i_stars > phivals[i], phi_i_stars <= phivals[i - 1]))

    ############################################################################
    #
    # Buried/surface
    #
    ############################################################################

    # phi-series
    phiseries = np.zeros((len(phivals) - 1, 2))

    # buried-surface indicator
    buried_indicator = np.load(buried_npyfile)

    # Plot overall surface composition
    # --------------------------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_indices = np.array(tuple(list(range(len(protein_heavy.atoms)))))
    values = buried_surface_valueslist(all_indices, protein_heavy, buried_indicator)

    ax.pie(values,
           labels=["Buried", "Surface"],
           colors=["salmon", "skyblue"],
           autopct=nonzero_autopct)
    ax.set_title("{} composition".format(protname))

    fig.savefig(buried_surface_movieformat.format("{:05d}".format(0)))

    # Plot linear atoms
    # -----------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_atoms_values = buried_surface_valueslist(all_indices, protein_heavy, buried_indicator)
    linear_atoms_values = buried_surface_valueslist(hyd_indices[(phivals[1], phivals[0])].flatten(),
                                                    protein_heavy, buried_indicator)

    non_linear_atoms_values = all_atoms_values - linear_atoms_values

    comb_atoms_values = [None] * (len(linear_atoms_values) + len(non_linear_atoms_values))
    comb_atoms_values[::2] = linear_atoms_values
    comb_atoms_values[1::2] = non_linear_atoms_values

    for field in range(len(linear_atoms_values)):
        phiseries[0, field] = linear_atoms_values[field]

    ax.pie(comb_atoms_values,
           labels=["Buried-hydrated", "Buried",
                   "Surface-hydrated", "Surface"],
           colors=["white", "salmon",
                   "white", "skyblue"],
           autopct=nonzero_autopct)
    ax.set_title("Linear fit atoms" + r" ($\phi={}\ \leftarrow\ {}$)".format(phivals[1], r"\infty"))

    fig.savefig(buried_surface_movieformat.format("{:05d}".format(1)))

    # Plot over phi-ensemble
    # ----------------------

    prev_indices = np.array([])

    for phiidx in tqdm(range(2, len(phivals))):
        phi_range = (phivals[phiidx], phivals[phiidx - 1])

        union_indices = np.concatenate((prev_indices, hyd_indices[phi_range].flatten())).astype(int)

        wet_atoms_values = buried_surface_valueslist(union_indices, protein_heavy, buried_indicator)
        non_linear_wet_atoms_values = all_atoms_values - linear_atoms_values - wet_atoms_values

        comb_atoms_values = [None] * (len(linear_atoms_values) + len(wet_atoms_values) + len(non_linear_wet_atoms_values))
        comb_atoms_values[::3] = linear_atoms_values
        comb_atoms_values[1::3] = wet_atoms_values
        comb_atoms_values[2::3] = non_linear_wet_atoms_values

        for field in range(len(wet_atoms_values)):
            phiseries[phiidx - 1, field] = phiseries[0, field] + wet_atoms_values[field]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

        ax.pie(comb_atoms_values,
               labels=["", "", "Buried",
                       "", "", "Surface"],
               colors=["white", "red", "salmon",
                       "white", "dodgerblue", "skyblue"],
               autopct=nonzero_autopct,
               wedgeprops={'linewidth': 3})

        ax.set_title(r"$\phi$={:.2f} $\leftarrow {:.2f}$".format(phi_range[0], phivals[1]))

        y_minor_locator = AutoMinorLocator(5)
        ax.yaxis.set_minor_locator(y_minor_locator)
        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')

        fig.savefig(buried_surface_movieformat.format("{:05d}".format(phiidx)))

        plt.close('all')

        prev_indices = union_indices

    ############################################################################
    #
    # Residue type: charged/hydrophobic/hydrophilic
    #
    ############################################################################

    # phi-series
    phiseries = np.zeros((len(phivals) - 1, 3))

    # Plot overall surface composition
    # --------------------------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_indices = np.array(tuple(list(range(len(protein_heavy.atoms)))))
    values = charged_hydrophobic_hydrophilic_residues_valueslist(all_indices, protein_heavy)

    ax.pie(values,
           labels=["Charged", "Hydrophobic", "Hydrophilic"],
           colors=["limegreen", "salmon", "skyblue"],
           autopct=nonzero_autopct)
    ax.set_title("{} composition".format(protname))

    fig.savefig(restype_movieformat.format("{:05d}".format(0)))

    # Plot linear atoms
    # -----------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_atoms_values = charged_hydrophobic_hydrophilic_residues_valueslist(all_indices, protein_heavy)
    linear_atoms_values = charged_hydrophobic_hydrophilic_residues_valueslist(hyd_indices[(phivals[1], phivals[0])].flatten(),
                                                                              protein_heavy)
    non_linear_atoms_values = all_atoms_values - linear_atoms_values

    comb_atoms_values = [None] * (len(linear_atoms_values) + len(non_linear_atoms_values))
    comb_atoms_values[::2] = linear_atoms_values
    comb_atoms_values[1::2] = non_linear_atoms_values

    for field in range(len(linear_atoms_values)):
        phiseries[0, field] = linear_atoms_values[field]

    ax.pie(comb_atoms_values,
           labels=["Charged-hydrated", "Charged",
                   "Hydrophobic-hydrated", "Hydrophobic",
                   "Hydrophilic-hydrated", "Hydrophilic"],
           colors=["white", "limegreen",
                   "white", "salmon",
                   "white", "skyblue"],
           autopct=nonzero_autopct)
    ax.set_title("Linear fit atoms" + r" ($\phi={}\ \leftarrow\ {}$)".format(phivals[1], r"\infty"))

    fig.savefig(restype_movieformat.format("{:05d}".format(1)))

    # Plot over phi-ensemble
    # ----------------------

    prev_indices = np.array([])

    for phiidx in tqdm(range(2, len(phivals))):
        phi_range = (phivals[phiidx], phivals[phiidx - 1])

        union_indices = np.concatenate((prev_indices, hyd_indices[phi_range].flatten())).astype(int)

        wet_atoms_values = charged_hydrophobic_hydrophilic_residues_valueslist(union_indices, protein_heavy)
        non_linear_wet_atoms_values = all_atoms_values - linear_atoms_values - wet_atoms_values

        comb_atoms_values = [None] * (len(linear_atoms_values) + len(wet_atoms_values) + len(non_linear_wet_atoms_values))
        comb_atoms_values[::3] = linear_atoms_values
        comb_atoms_values[1::3] = wet_atoms_values
        comb_atoms_values[2::3] = non_linear_wet_atoms_values

        for field in range(len(wet_atoms_values)):
            phiseries[phiidx - 1, field] = phiseries[0, field] + wet_atoms_values[field]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

        ax.pie(comb_atoms_values,
               labels=["", "", "Charged",
                       "", "", "Hydrophobic",
                       "", "", "Hydrophilic"],
               colors=["white", "green", "limegreen",
                       "white", "red", "salmon",
                       "white", "dodgerblue", "skyblue"],
               autopct=nonzero_autopct,
               wedgeprops={'linewidth': 3})

        ax.set_title(r"$\phi$={:.2f} $\leftarrow {:.2f}$".format(phi_range[0], phivals[1]))

        y_minor_locator = AutoMinorLocator(5)
        ax.yaxis.set_minor_locator(y_minor_locator)
        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')

        fig.savefig(restype_movieformat.format("{:05d}".format(phiidx)))

        plt.close('all')

        prev_indices = union_indices

    ############################################################################
    #
    # Atom type: hydrophobic/hydrophilic
    #
    ############################################################################

    # phi-series
    phiseries = np.zeros((len(phivals) - 1, 2))

    # kapcha rossky scale dictionary
    with open(kr_pklfile, 'rb') as kr_dict_file:
        kr_scale = pickle.load(kr_dict_file)

    # Plot overall surface composition
    # --------------------------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_indices = np.array(tuple(list(range(len(protein_heavy.atoms)))))
    values = polar_nonpolar_atoms_valueslist(all_indices, protein_heavy, kr_scale, ff)

    ax.pie(values,
           labels=["Polar", "Nonpolar"],
           colors=["skyblue", "salmon"],
           autopct=nonzero_autopct)
    ax.set_title("{} composition".format(protname))

    fig.savefig(atomtype_movieformat.format("{:05d}".format(0)))

    # Plot linear atoms
    # -----------------

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    all_atoms_values = polar_nonpolar_atoms_valueslist(all_indices, protein_heavy, kr_scale, ff)
    linear_atoms_values = polar_nonpolar_atoms_valueslist(hyd_indices[(phivals[1], phivals[0])].flatten(), protein_heavy,
                                                          kr_scale, ff)

    non_linear_atoms_values = all_atoms_values - linear_atoms_values

    comb_atoms_values = [None] * (len(linear_atoms_values) + len(non_linear_atoms_values))
    comb_atoms_values[::2] = linear_atoms_values
    comb_atoms_values[1::2] = non_linear_atoms_values

    for field in range(len(linear_atoms_values)):
        phiseries[0, field] = linear_atoms_values[field]

    ax.pie(comb_atoms_values,
           labels=["Polar-hydrated", "Polar",
                   "Nonpolar-hydrated", "Nonpolar"],
           colors=["white", "skyblue",
                   "white", "salmon"],
           autopct=nonzero_autopct)
    ax.set_title("Linear fit atoms" + r" ($\phi={}\ \leftarrow\ {}$)".format(phivals[1], r"\infty"))

    fig.savefig(atomtype_movieformat.format("{:05d}".format(1)))

    # Plot over phi-ensemble
    # ----------------------

    prev_indices = np.array([])

    for phiidx in tqdm(range(2, len(phivals))):
        phi_range = (phivals[phiidx], phivals[phiidx - 1])

        union_indices = np.concatenate((prev_indices, hyd_indices[phi_range].flatten())).astype(int)

        wet_atoms_values = polar_nonpolar_atoms_valueslist(union_indices, protein_heavy, kr_scale, ff)
        non_linear_wet_atoms_values = all_atoms_values - linear_atoms_values - wet_atoms_values

        comb_atoms_values = [None] * (len(linear_atoms_values) + len(wet_atoms_values) + len(non_linear_wet_atoms_values))
        comb_atoms_values[::3] = linear_atoms_values
        comb_atoms_values[1::3] = wet_atoms_values
        comb_atoms_values[2::3] = non_linear_wet_atoms_values

        for field in range(len(wet_atoms_values)):
            phiseries[phiidx - 1, field] = phiseries[0, field] + wet_atoms_values[field]

        fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

        ax.pie(comb_atoms_values,
               labels=["", "", "Polar",
                       "", "", "Nonpolar"],
               colors=["white", "dodgerblue", "skyblue",
                       "white", "red", "salmon"],
               autopct=nonzero_autopct,
               wedgeprops={'linewidth': 3})

        ax.set_title(r"$\phi$={:.2f} $\leftarrow {:.2f}$".format(phi_range[0], phivals[1]))

        y_minor_locator = AutoMinorLocator(5)
        ax.yaxis.set_minor_locator(y_minor_locator)
        ax.grid(which='major', linestyle='--')
        ax.grid(which='minor', linestyle=':')

        fig.savefig(atomtype_movieformat.format("{:05d}".format(phiidx)))

        plt.close('all')

        prev_indices = union_indices

    ############################################################################
    # Generate plot and movie frames for ssclass
    ############################################################################

    ############################################################################
    # Generate plot and movie frames for ssgroup
    ############################################################################

    ############################################################################
    # Stitch movie frames into movie
    ############################################################################

    for movieformat in [buried_surface_movieformat, restype_movieformat, atomtype_movieformat]:
        os.system("ffmpeg -r 5 -i {} -vcodec mpeg4 -y -vb 40M {}".format(
                  movieformat.format("%05d"), movieformat.split(".")[0] + ".mp4"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot Nv v/s phi and phi* for simulation.")
    parser.add_argument("-protname", help="name of protein")
    parser.add_argument("-pklfile", help="file to read phi_i* data from (.pkl)")

    parser.add_argument("-structfile", help="path to structure file (.gro, .tpr)")
    parser.add_argument("-phi_bins", nargs=3, type=float, help="parameters to choose phi values for static PDB (start end spacing)")

    bsargs = parser.add_argument_group('Arguments for buried/surface classification')
    bsargs.add_argument("-buried_npyfile", help="file to read buried/surface heavy atom indicator array from (.npy)")
    bsargs.add_argument("-buried_surface_imgfile", help="output file for buried-surface plot")
    bsargs.add_argument("-buried_surface_movieformat", help="output format for buried-surface movie frames, with {} placeholder for frame index")

    restypeargs = parser.add_argument_group('Arguments for residue type (charged/hydrophobic/hydrophilic) classification')
    restypeargs.add_argument("-restype_imgfile", help="output file for residue types plot")
    restypeargs.add_argument("-restype_movieformat", help="output format for residue types movie frames, with {} placeholder for frame index")

    atomtypeargs = parser.add_argument_group('Arguments for atom type (polar/nonpolar) classification')
    atomtypeargs.add_argument("-kr_pklfile", default=expanduser("~") + "/analysis_scripts/data/kapcha_rossky_amber99sb/kapcha_rossky_scale.pkl",
                              help="file to read Kapcha-Rossky dictionary from (.pkl) [default=load from INDUSAnalysis default install location]")
    atomtypeargs.add_argument("-ff", default="amber99sb",
                              help="force field (for Kapcha-Rossky FF-specific atom type corrections)")
    atomtypeargs.add_argument("-atomtype_imgfile", help="output file for atom types plot")
    atomtypeargs.add_argument("-atomtype_movieformat", help="output format for atom types movie frames, with {} placeholder for frame index")

    ssclassargs = parser.add_argument_group('Arguments for residue secondary structure type classification')
    ssclassargs.add_argument("-stride_pklfile",
                             help="file to read STRIDE classification of each residue from (.pkl)")
    ssclassargs.add_argument("-ssclass_imgfile", help="output file for secondary structure types plot")
    ssclassargs.add_argument("-ssclass_movieformat", help="output format for secondary structure types movie frames, with {} placeholder for frame index")

    a = parser.parse_args()

    hydrated_atom_chars(a.protname,
                        a.pklfile,
                        a.structfile,
                        a.phi_bins,
                        a.buried_npyfile, a.buried_surface_imgfile, a.buried_surface_movieformat,
                        a.restype_imgfile, a.restype_movieformat,
                        a.kr_pklfile, a.ff, a.atomtype_imgfile, a.atomtype_movieformat,
                        a.ssclass_imgfile, a.ssclass_movieformat)
                        #a.ssgroup_imgfile, a.ssgroup_imgformat)
