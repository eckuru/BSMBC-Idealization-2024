#!/usr/bin/env python3

import argparse
import numpy as np
from ASCAM.src.core.filtering import gaussian_filter


def main(args):
    trace = np.load(args.traceFile)
    samplerate = int(args.traceFile.split('samplerate')[1].split('-')[0])
    for freq in args.gaussFilter:
        gf_trace = gaussian_filter(trace, freq, samplerate)

        newpath = f"{args.traceFile.split('.npy')[0]}-gf{freq}.npy"
        np.save(newpath, gf_trace)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'Prepare simulation data for analysis by filtering the trace')
    parser.add_argument('--traceFile')
    parser.add_argument('--gaussFilter', type=int, nargs='+', default=1000)
    args = parser.parse_args()
    main(args)
