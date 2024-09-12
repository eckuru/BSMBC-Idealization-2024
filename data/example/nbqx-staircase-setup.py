#!/usr/bin/env python3

import numpy as np

# This is inspired by the staircase experiment,
# rate constants from Robert & Howe 2003 (rates for GluA4)

# parameters = {
#     'alpha': 8000,  # 1/s
#     'beta': 20000,  # 1/s
#     'kn': 9000,  # 1/s
#     'kp': 2e7,  # 1/(Ms)
#     'xA': 100*1e-3,  # M
#     # 'xB': 0,
# }
#
#
# setting kn=0 to account for blocker concentration = 0
# smaller kp to account for competitive binding
a = 3000  # 1/s Poulsen
b = 8000  # 1/s
kn = 0  # 1/s
kp = 2  # 1/(Ms)
xA = 10*1e-3  # M


Q = np.array([
    [0, a, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [b, 0, 4*kn, a, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, kp, 0, 0, a, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, b, 0, 0, 4*kn, 0, a, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, b, kp, 0, 3*kn, 0, a, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2*kp, 0, 0, 0, a, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, b, 0, 0, 0, 4*kn, 0, 0, a, 0, 0, 0, 0],
    [0, 0, 0, 0, b, 0, kp, 0, 3*kn, 0, 0, a, 0, 0, 0],
    [0, 0, 0, 0, 0, b, 0, 2*kp, 0, 2*kn, 0, 0, a, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 3*kp, 0, 0, 0, 0, a, 0],
    [0, 0, 0, 0, 0, 0, b, 0, 0, 0, 0, 4*kn, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, b, 0, 0, kp, 0, 3*kn, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, b, 0, 0, 2*kp, 0, 2*kn, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, b, 0, 0, 3*kp, 0, kn],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4*kp, 0]
])


for i, row in enumerate(Q):
    Q[i, i] = -sum(row)

np.save('./Q.npy', Q)
np.save(
    './conductances.npy',
    np.array(
        [30.8, 22.8, 22.8, 15.4, 15.4, 15.4, 7.6, 7.6, 7.6, 7.6, 0, 0, 0, 0, 0]
    )*1e-12
)
