"""
Created on Jun 30, 2013

Wrappers around scipy.stats statistical tests to use 
Pandas data-structures and return Pandas objects as
results. 

@author: agross
"""

import pandas as pd
import numpy as np

from scipy import stats


def _match_series(a, b):
    """
    Matches two series on shared data.

    (copied from Processing.Helpers to remove that dependency,
     public use should go through Processing.Helpers)
    """
    a, b = a.align(b, join='inner', copy=False)
    valid = pd.notnull(a) & pd.notnull(b)
    a = a[valid]
    if not a.index.is_unique:
        a = a.groupby(lambda s: s).first()  # some sort of duplicate index bug
    b = b[valid]
    if not b.index.is_unique:
        b = b.groupby(lambda s: s).first()
    return a, b


def _split_on_index(s, matched=False, n_groups=2):
    """
    Splits a series on the second level of its index.
    """
    d = s.unstack()
    if matched is True:
        d = d.dropna()
    assert(d.shape[1] == n_groups)
    a, b = [i[1] for i in d.iteritems()]
    return a, b


def wilcoxon_pandas(a, b=None):
    """
    Wrapper to do a one way t-test on pandas matched samples
    ------------------------------------------------
    a,b: matched measurements

    OR

    a: Series of matched measurements with assignment on second level
       of multi-index.
    """
    if isinstance(b, pd.Series):
        a, b = _match_series(a, b)
    elif b is None and isinstance(a.index, pd.MultiIndex):
        a, b = _split_on_index(a, matched=True)
    z, p = stats.wilcoxon(a, b)
    return pd.Series({'T': z, 'p': p})


def ttest_rel(a, b=None):
    """
    Wrapper to do a one way t-test on pandas matched samples
    ------------------------------------------------
    a,b: matched measurements

    OR

    a: Series of matched measurements with assignment on second level
       of multi-index.
    """
    if isinstance(b, pd.Series):
        a, b = _match_series(a, b)
    elif b is None and isinstance(a.index, pd.MultiIndex):
        a, b = _split_on_index(a, matched=True)
    z, p = stats.ttest_rel(a, b)
    return pd.Series({'t': z, 'p': p})


def anova(hit_vec, response_vec, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels
    response_vec: Series of measurements
    """
    if hit_vec.value_counts().min < min_size:
        return np.nan
    if not np.alltrue(hit_vec.index == response_vec.index):
        hit_vec, response_vec = _match_series(hit_vec, response_vec)
    hit_vec, response_vec = _match_series(hit_vec, response_vec)
    res = stats.f_oneway(*[response_vec[hit_vec == num] for num in 
                           hit_vec.unique()])
    return pd.Series(res, index=['F', 'p'])


def fisher_exact_test(hit_vec, response_vec, alternative='two-sided'):
    """
    Wrapper to do a fischer's exact test on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels (boolean, or (0,1))
    response_vec: Series of measurements (boolean, or (0,1))
    """
    hit_vec.name = 'h'  # crosstab can't handle multi_index
    response_vec.name = 'd'  # so we use dummy names
    cont_table = pd.crosstab(hit_vec, response_vec)
    if cont_table.shape != (2, 2):
        return pd.Series(index=['odds_ratio', 'p'])
    return pd.Series(stats.fisher_exact(cont_table, alternative), index=['odds_ratio', 'p'])


def kruskal_pandas(hit_vec, response_vec, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels
    response_vec: Series of measurements
    """
    try:
        if not np.alltrue(hit_vec.index == response_vec.index):
            hit_vec, response_vec = _match_series(hit_vec, response_vec)
        res = stats.kruskal(*[response_vec[hit_vec == num] for num in 
                            hit_vec.unique()])
        return pd.Series(res, index=['H', 'p'])
    except:
        return pd.Series(index=['H', 'p'])


def rev_kruskal(response_vec, hit_vec, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series.
    Same code as kruskal_pandas, different order of arguments.
    ------------------------------------------------
    response_vec: Series of measurements
    hit_vec: Series of labels
    """
    return kruskal_pandas(hit_vec, response_vec)

    
def spearman_pandas(a, b, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels
    response_vec: Series of measurements
    """
    try:
        a, b = _match_series(a, b)
        res = stats.spearmanr(a, b)
        return pd.Series(res, index=['rho', 'p'])
    except:
        return pd.Series(index=['rho', 'p'])
    

def pearson_pandas(a, b, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels
    response_vec: Series of measurements
    """
    try:
        a, b = _match_series(a, b)
        res = stats.pearsonr(a, b)
        return pd.Series(res, index=['rho', 'p'])
    except:
        return pd.Series(index=['rho', 'p'])


def bartlett_pandas(group_vec, response_vec, min_size=5):
    """
    Wrapper to do a one way anova on pandas Series
    ------------------------------------------------
    group_vec: Series of labels
    response_vec: Series of measurements
    """
    if group_vec.value_counts().min() < min_size:
        return np.nan
    group_vec, response_vec = _match_series(group_vec, response_vec)
    res = stats.bartlett(*[response_vec[group_vec == num] for num in 
                     group_vec.unique()])
    return pd.Series(res, index=['T', 'p'])


def chi2_cont_test(hit_vec, response_vec):
    """
    Wrapper to do a fischer's exact test on pandas Series
    ------------------------------------------------
    hit_vec: Series of labels (boolean, or (0,1))
    response_vec: Series of measurements (boolean, or (0,1))
    """
    hit_vec.name = 'h'  # crosstab can't handle multi_index
    response_vec.name = 'd'  # so we use dummy names
    cont_table = pd.crosstab(hit_vec, response_vec)
    # if (cont_table.shape != (2,2)):
    #    return pd.Series(index=['odds_ratio','p'])
    # return cont_table
    return pd.Series(stats.chi2_contingency(cont_table)[:3], index=['chi2', 'p', 'dof'])
