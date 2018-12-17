from pandas.util import hash_pandas_object
from pandas import DataFrame, Series
from copy import copy
from hashlib import sha512


def deep_hash(item):
    if isinstance(item, tuple):
        item = tuple(
            deep_hash(i)
            for i in item
        )
    if isinstance(item, dict):
        item = tuple(item.items())
    return hash(item)


def power_hash(obj):
    hashable = copy(obj)
    if isinstance(hashable, dict):
        hashable = hash(tuple(
            (key, power_hash(value))
            for key, value in obj.items()
        ))
    elif isinstance(hashable, DataFrame) or isinstance(hashable, Series):
        if isinstance(hashable, DataFrame):
            for column in hashable.columns:
                hashable[column] = hashable[column].apply(deep_hash)
        hashable = sha512(
            hash_pandas_object(hashable).values
        ).hexdigest()
    elif isinstance(hashable, list) or isinstance(hashable, tuple):
        hashable = tuple(
            power_hash(o)
            for o in obj
        )
    elif isinstance(hashable, set):
        hashable = frozenset(hashable)
    return hashable


verbose = 0


def cache_decorator(function, ignore_first=False):

    def cached(*args, **kwargs):
        key_args = args[1:] if ignore_first else args
        hashable = power_hash((key_args, kwargs))
        if not hasattr(function, '__cache__'):
            function.__cache__ = {}
        if hashable not in function.__cache__:
            if verbose > 1:
                print(f'Adding to cache; key: {hashable}')
            function.__cache__[hashable] = function(*args, **kwargs)
        elif verbose > 1:
            print(f'Reusing cache; key: {hashable}')
        return function.__cache__[hashable]

    return cached


def cached_property(function):
    
    def cached(self, *args, **kwargs):
        hashable = power_hash(self)
        if not hasattr(function, '__cache__'):
            function.__cache__ = {}
        if hashable not in function.__cache__:
            function.__cache__[hashable] = function(self, *args, **kwargs)
        return function.__cache__[hashable]
    
    return property(cached)
