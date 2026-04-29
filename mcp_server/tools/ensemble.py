import numpy as np


def ensemble_predictions(*model_predictions):

    min_len = min(len(p) for p in model_predictions)

    trimmed = [p[:min_len] for p in model_predictions]

    stacked = np.array(trimmed)

    mean_preds = stacked.mean(axis=0)

    return mean_preds.tolist()