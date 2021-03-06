# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/006_data.validation.ipynb (unless otherwise specified).

__all__ = ['get_train_val_test_idxs', 'leakage_finder', 'check_overlap', 'oversampled_idxs']

# Cell
from ..imports import *

# Cell
from sklearn.model_selection import StratifiedKFold, KFold
from imblearn.over_sampling import RandomOverSampler
from collections import Counter

# Cell
def get_train_val_test_idxs(y, n_folds, test_fold=False, stratified=False, oversample=False, seed=1):
    splitter = StratifiedKFold if stratified else KFold
    if isinstance(y, np.ndarray): y = torch.Tensor(y).to(dtype=torch.int64)
    folds = 5 if n_folds == 1 else n_folds
    if test_fold:
        outer_folds = list(splitter(n_splits=folds + 1, shuffle=True, random_state=seed).split(np.zeros(len(y)), y))
        test_idx = outer_folds[0][1]
        inner_idxs = outer_folds[0][0]
        inner_folds = splitter(n_splits=folds, shuffle=True, random_state=seed).split(np.zeros(len(inner_idxs)), y[inner_idxs])
        train_idx = []
        val_idx = []
        for train, val in inner_folds:
            if oversample:train = oversampled_idxs(y[inner_idxs], train, seed=seed)
            train_idx.append(inner_idxs[train])
            val_idx.append(inner_idxs[val])
        if n_folds == 1: return [train_idx[0]], [val_idx[0]], test_idx
        return train_idx, val_idx, test_idx
    else:
        inner_folds = splitter(n_splits=folds, shuffle=True, random_state=seed).split(np.zeros(len(y)), y)
        train_idx = []
        val_idx = []
        for train, val in inner_folds:
            if oversample: train = oversampled_idxs(y, train, seed=seed)
            train_idx.append(train)
            val_idx.append(val)
        if n_folds == 1: return [train_idx[0]], [val_idx[0]], None
        return train_idx, val_idx, None

# Cell
def leakage_finder(train, val, test=None):
    if check_overlap(train, val) is not None:
        print('train-val leakage!')
        return check_overlap(train, val)
    if test is not None:
        if check_overlap(train, test) is not None:
            print('train-test leakage!')
            return check_overlap(train, test)
        if check_overlap(val, test) is not None:
            print('val-test leakage!')
            return check_overlap(val, test)
    return

def check_overlap(a, b):
    overlap = [i for i in a if i in b]
    if overlap == []: return
    return overlap

# Cell
def oversampled_idxs(y, idx, seed=1, verbose=False):
    ros = RandomOverSampler(random_state=seed)
    resampled_idxs, y_resampled = ros.fit_resample(idx.reshape(-1, 1), y[idx])
    if verbose: print('classes:', count_classes(y_resampled))
    return np.sort(resampled_idxs.ravel())