"""
@author Akash Pallath

Analyse output file produced by GROMACS 4.5.3 modified to perform indirect
umbrella sampling, write data to output files, and generate plots

Dependencies:
- argparse
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file to plot, generated by GROMACS-INDUS")
    parser.add_argument("-avgstart", help="time to start averaging at")
    parser.add_argument("-avgend", help="time to stop averaging at")
    parser.add_argument("-avgto", help="file to append averages to")
    parser.add_argument("-o", help="name of output image file")
    parser.add_argument("-dpi", type=int, help="dpi of output image")
    parser.add_argument("--noshow", action='store_true', help="do not show interactive plot")
    args = parser.parse_args()

    f = open(args.file)
    t = []
    N = []
    Ntw = []
    mu = 0

    #read data file
    for l in f:
        lstrip = l.strip()
        #parse comments
        if lstrip[0]=='#':
            comment = lstrip[1:].split()
            if comment[0] == 'mu':
                mu = comment[2]
        #parse data
        if lstrip[0]!='#':
            (tcur,Ncur,Ntwcur) = map(float,lstrip.split())
            t.append(tcur)
            N.append(Ncur)
            Ntw.append(Ntwcur)

    t = np.array(t)
    N = np.array(N)
    Ntw = np.array(Ntw)

    if(len(N) != len(Ntw) or len(N) != len(t)):
        raise Exception("t, Ntw, N lengths do not match")

    #Electrostatics
    nsteps = len(N)
    tstep = t[1]

    #averaging
    start = 0
    end = nsteps
    if args.avgstart is not None:
        start = int(float(args.avgstart)//tstep)
    if args.avgend is not None:
        end = int(float(args.avgend)//tstep)
    Navg = np.mean(N[start:end])
    Nstd = np.std(N[start:end])
    Ntwavg = np.mean(Ntw[start:end])
    Ntwstd = np.std(Ntw[start:end])
    print("Averaged over frame {} to {}".format(start, end))
    print("<N> = {}, std = {}".format(Navg, Nstd))
    print("<Ntw> = {}, std = {}".format(Ntwavg, Ntwstd))

    #append averages
    if args.avgto is not None:
        f = open(args.avgto, "a+")
        f.write("{}  {}  {}  {}  {}\n".format(mu, Navg, Nstd, Ntwavg, Ntwstd))

    #plotting
    plt.figure()
    ax = plt.gca()
    plt.plot(t,N,label="$N$")
    plt.plot(t,Ntw,label="$Ntwiddle$")
    ax.set_xlabel("Time, in ps")
    ax.set_ylabel("$N_v$ and coarse-grained $N_v$")
    plt.legend()

    #save image
    imgout = args.o
    imgdpi = args.dpi

    if imgout is None:
        imgout = 'phiout.pdf'
    if imgdpi is not None:
        plt.savefig(imgout, dpi=imgdpi)
    else:
        plt.savefig(imgout)

    #display interactive plot
    if args.noshow == False:
        plt.show()
