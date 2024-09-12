#!/usr/bin/env python
import argparse
import numpy as np
import os
if os.uname().sysname == 'Darwin':
    os.chdir('/Users/ecekuru/Projects')
else:
    os.chdir('/home/ecek/Projects')
try:
    from ASCAM.src.core import DISC
except ImportError:
    import sys
    if os.uname().sysname == 'Darwin':
        sys.path.append('/Users/ecekuru/Projects')
    else:
        sys.path.append('/home/ecek/Projects')
    from ASCAM.src.core import DISC


def fitdata(args, data, nameaddition=''):
    fit = DISC.run_DISC(
        data,
        alpha=args.alpha,
        IC_HAC=args.IC_HAC,
        IC_div_seg=args.IC_div_seg,
        min_seg_length=args.min_seg_length,
        min_cluster_size=args.min_cluster_size,
        BIC_method=args.BIC_method,
    )
    states = np.unique(fit)
    print(f'Found {len(states)} states at {states}.')
    dataname = args.inputfile.split('/')[-1].split('.npy')[0]
    a = str(args.alpha).replace('.', '_')
    fpath = (
        f'{args.outdir}/{dataname}_Alpha{a}_ICHAC{args.IC_HAC}_'
        f'ICdivseg{args.IC_div_seg}_minseg{args.min_seg_length}_'
        f'mincluster{args.min_cluster_size}_BIC{args.BIC_method}_'
        f'{nameaddition}'
    )
    np.save(f'{fpath}.npy', fit)
    print(f'Fit saved in {fpath}.npy')
    return fit, fpath


def main(args):
    print(f'Fitting data from {args.inputfile} with DISC.')
    alldata = np.load(args.inputfile)
    # remove baseline
    if 'samplerate' in args.inputfile:
        samplerate = int(args.inputfile.split('samplerate')[-1].split('-')[0])
    else:
        samplerate = 40000
    baselineEndIndex = int(args.baseline * samplerate)
    data = alldata[baselineEndIndex:]
    if args.downsample:
        print(f'Downsampling from 40kHz to {args.downsample}')
        new = data[::int(40000/args.downsample)]
        data = new
    if args.episodic:
        eplength = int(args.inputfile.split('_')[-2].split('episodePoints')[0])
        print(f'Fitting each episode with {eplength} points separately.')
    print(
        f'Parameters: alpha: {args.alpha}, '
        f'ICHAC: {args.IC_HAC}, '
        f'ICdivseg: {args.IC_div_seg}, '
        f'minseg: {args.min_seg_length}, '
        f'mincluster: {args.min_cluster_size}, '
        f'BIC: {args.BIC_method}'
    )
    if args.episodic:
        episodes = np.split(data, int(len(data)/eplength))
        print(len(data))
        print(eplength)
        fits = []
        for i, episode in enumerate(episodes):
            fit, fpath = fitdata(args, episode, i)
            fits.append(fit)
        fullfit = np.hstack(fits)
        print(fullfit.shape)
        np.save(f'{fpath}_full.npy', fullfit)
    else:
        fitdata(args, data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Test DISC implementation in ASCAM',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('inputfile')
    parser.add_argument(
        '--BIC_method', choices=('full', 'approx'), default='full',
        help='BIC implementation to use'
    )

    parser.add_argument('--outdir')
    parser.add_argument('--IC_HAC', default='BIC', help='IC for HAC')
    parser.add_argument(
        '--IC_div_seg', default='BIC', help='IC for divisive segmentation'
    )
    parser.add_argument('--alpha', type=float)
    parser.add_argument(
        '--min_seg_length', type=int, default=3,
        help='Minimum segment length for divisive segmentation',
    )
    parser.add_argument(
        '--min_cluster_size', type=int, default=3,
        help='Minmum cluster size'
    )
    parser.add_argument(
        '--episodic', action='store_true',
    )
    parser.add_argument(
        '--downsample', default=None, type=int,
        help='Downsample to the given frequency in Hz',
    )
    parser.add_argument(
        '--baseline', type=float, default=0.5,
        help="Baseline duration.",
    )
    args = parser.parse_args()
    main(args)
