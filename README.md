# BSMBC-Idealization-2024
Code for simulating single channel recordings and idealizing them with ASCAM code

1. Clone this repository
2. Clone [ASCAM](https://github.com/AGPlested/ASCAM) and follow the desctiption to get it running.
3. `src/processSimulationData.py --traceFile data/example/traces/current-trace-samplerate40000-SNR2_0.npy --gaussFilter 5000`
4. `src/simulate-trace.py --dataDir data/example --conductancesFilename conductances.npy --QFilename Q.npy --duration 2 --initialState 14 --SNR 2 --samplerate 40000`
5. `src/testDISC.py --BIC_method full --outdir data/example --alpha 1e-6`

Now you can open the jupyter notebook and examine the results of the simulation and idealization.
