"""
:mod:`kbtune` -- Keyboard tuning
================================

>>> print(cents_to_ratio(ratio_to_cents(1.05)))
1.05
>>> print(ratio_to_cents(cents_to_ratio(20)))
20.0
"""

from __future__ import division

import math # log

__version__ = '1.0'

def ratio_to_cents(ratio):
    """Convert ratio to cents.

    >>> ratio_to_cents(1.01) # doctest: +ELLIPSIS
    17.22635...
    """
    return 1200 * math.log(ratio, 2)

def cents_to_ratio(cents):
    """Convert cents to ratio.

    >>> cents_to_ratio(50) # doctest: +ELLIPSIS
    1.0293022...
    """
    return 2 ** (cents / 1200)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
