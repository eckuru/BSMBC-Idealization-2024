#!/usr/bin/env python3

import argparse
import numpy as np
import os
import scipy as sp


def step(dwellTimeDistributionRateConstant, transitionProbabilities):
    dwellTime = np.random.default_rng().exponential(
        -1 * dwellTimeDistributionRateConstant
    )
    nextState = np.random.choice(
        len(transitionProbabilities), p=transitionProbabilities
    )
    return nextState, dwellTime


def simulate_ground_truth(
        initialState, T, dwellTimeConstants, transitionProbabilities
):
    transitions = [initialState]
    dwellTimes = [0.5 + np.random.default_rng().exponential(
        -1 * dwellTimeConstants[initialState]
    )]
    t = dwellTimes[0]
    currentState = initialState
    while t < T:
        nextState, dwellTime = step(
            dwellTimeConstants[currentState],
            transitionProbabilities[currentState]
        )
        transitions.append(currentState)
        dwellTimes.append(dwellTime)

        currentState = nextState
        t += dwellTime
    return np.array(transitions), np.array(dwellTimes)


def constructTrace(
        groundTruthStates, groundTruthDwellTimes, trueStates, dt,
        V=-80*1e-3,
):
    trace = []
    carry = 0
    for state, dwellTime in zip(groundTruthStates, groundTruthDwellTimes):
        time = dwellTime + carry
        npoints = int(time / dt)
        trace += [state for i in range(npoints)]
        carry = time - (npoints * dt)
    current = trueStates[trace] * V
    return current


def makeNoise(cleanTrace, SNR, mean_delta_I):
    sigma = mean_delta_I / SNR
    noise = np.random.normal(0, sigma, len(cleanTrace))
    return noise


def main(args):
    dts = []
    for samplerate in args.samplerate:
        dts.append(1/samplerate)
    pyFiles = []
    with os.scandir(args.dataDir) as dataDir:
        for entry in dataDir:
            if entry.name.endswith('setup.py') and entry.is_file():
                pyFiles.append(entry)

    assert len(pyFiles) == 1, f"None or multiple files in {args.dataDir} end with 'setup.py'"
    with open(pyFiles[0]) as f:
        currentDir = os.getcwd()
        os.chdir(args.dataDir)  # so the Q matrix and conductances are saved in dataDir
        exec(f.read())
        os.chdir(currentDir)

    Q = np.load(f"{args.dataDir}/{args.QFilename}")
    trueStates = np.load(f"{args.dataDir}/{args.conductancesFilename}")

    dwellTimeDistributionRateConstants = 1/Q.diagonal()
    transitionProbabilities = [
        Q[state, :] / Q[state, state] * -1 for state in range(len(Q))
    ]
    for problist in transitionProbabilities:
        problist[problist < 0] = 0

    groundTruthStates, groundTruthDwellTimes = simulate_ground_truth(
        args.initialState, args.duration,
        dwellTimeDistributionRateConstants, transitionProbabilities,
    )

    np.save(f'{args.dataDir}/true-transitions.npy', groundTruthStates)
    np.save(f'{args.dataDir}/true-dwellTimes.npy', groundTruthDwellTimes)

    for dt, samplerate in zip(dts, args.samplerate):
        cleanTrace = constructTrace(
            groundTruthStates, groundTruthDwellTimes, trueStates, dt,
        )
        np.save(
            f'{args.dataDir}/clean-traces/clean-current-trace-samplerate{samplerate}.npy',
            cleanTrace
        )
        current_levels = np.sort(np.unique(cleanTrace))[-1::-1]
        mean_delta_I = np.mean(abs(np.diff(current_levels)))
        for SNR in args.SNR:
            noise = makeNoise(cleanTrace, SNR, mean_delta_I)
            noisyTrace = cleanTrace + noise

            # Prefilter with 8-pole Bessel at 10 kHz
            # Wn = cornerfreq/Nyquist freq = 1e4/4000
            b, a = sp.signal.bessel(8, 4e3/1e4, analog=False)
            trace = sp.signal.lfilter(b, a, noisyTrace)
            np.save(
                f'{args.dataDir}/traces/current-trace-samplerate{samplerate}-SNR{str(SNR).replace(".", "_")}.npy',
                trace
            )
            np.save(
                f'{args.dataDir}/noise/noise-samplerate{samplerate}-SNR{str(SNR).replace(".", "_")}.npy',
                trace
            )
    print(f"States with {np.unique(cleanTrace)} A are visited")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Single Channel Simulator',
        description='Given the Q matrix and corresponding states, simulate '
                    'single channel data.',
    )
    parser.add_argument(
        '--dataDir',
        help='Path to the directory with the setup script for scheme. '
        'Results will be stored here. The script should end with setup.py'
    )
    parser.add_argument('--conductancesFilename', default='conductances.npy')
    parser.add_argument('--QFilename', default='Q.npy')
    parser.add_argument('--duration', type=float, help='Simulation duration [s]')
    parser.add_argument(
        '--initialState', type=int,
        help='State at the start of simulation, states are 0 indexed!'
    )
    parser.add_argument(
        '--SNR', nargs='+', type=float,
        help='Signal to noise ratio based on fully open level.'
    )
    parser.add_argument(
        '--samplerate', help='Samples per second', default=40000, nargs='+', type=int,
    )
    args = parser.parse_args()
    main(args)
