import numpy as np


def ensemble(*predictions):
    return np.mean(predictions, axis=0)