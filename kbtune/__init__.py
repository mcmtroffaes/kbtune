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

class Note:
    """Note as key with accidental."""
    KEYS = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
    KEY_NAMES = {0: 'C', 1: 'D', 2: 'E', 3: 'F', 4: 'G', 5: 'A', 6: 'B'}
    ACCIDENTAL_NAMES = {-2: 'bb', -1: 'b', 0: '', 1: '#', 2: 'x'}
    POSITIONS = {0: 0, 1: 2, 2: 4, 3: 5, 4: 7, 5: 9, 6: 11}

    key = None
    """Note (0=C, 1=D, and so on)."""
    accidental = None
    """Accidental (-1=b, -2=bb, +1=#, +2=x, and so on)."""

    def __init__(self, key=6, accidental=0):
        if isinstance(key, str):
            self.key = self.KEYS[key[0]]
            self.accidental = accidental
            for accidental in key[1:]:
                if accidental == 'b':
                    self.accidental -= 1
                elif accidental == '#':
                    self.accidental += 1
                elif accidental == 'x':
                    self.accidental += 2
                else:
                    raise ValueError("Unknown accidental '%s'." % accidental)
        elif isinstance(key, int):
            self.key = key
            self.accidental = accidental

    def __repr__(self):
        """Return string representation.

        >>> Note('Gbb')
        Note(key=4, accidental=-2)
        >>> Note('Gb')
        Note(key=4, accidental=-1)
        >>> Note('G')
        Note(key=4)
        >>> Note('G#')
        Note(key=4, accidental=1)
        >>> Note('Gx')
        Note(key=4, accidental=2)
        """
        if self.accidental:
            return 'Note(key=%i, accidental=%i)' % (self.key, self.accidental)
        else:
            return 'Note(key=%i)' % self.key

    def __str__(self):
        """Return string representation for printing.

        >>> print(Note(key=0))
        C
        >>> print(Note(key=6, accidental=-1))
        Bb
        >>> print(Note(key=4, accidental=-2))
        Gbb
        >>> print(Note(key=3, accidental=1))
        F#
        >>> print(Note(key=1, accidental=2))
        Dx
        """
        return (self.KEY_NAMES[self.key]
                + self.ACCIDENTAL_NAMES[self.accidental])

    @property
    def position(self):
        """Get position (a number between 0 and 11) of a key on the
        keyboard.

        >>> Note(key=0).position
        0
        >>> Note(key=0, accidental=1).position
        1
        >>> Note(key=0, accidental=-1).position
        11
        >>> Note(key=4, accidental=2).position
        9
        """
        return (self.POSITIONS[self.key] + self.accidental) % 12

class Interval:
    """An interval between two notes."""
    NAMES = {
        (0, 0): 'P1',   # perfect unison
        (0, 1): 'aug1', # augmented unison
        (1, 0): 'dim2', # diminished second
        (1, 1): 'm2',   # minor second
        (1, 2): 'M2',   # major second
        (1, 3): 'aug2', # augmented second
        (2, 2): 'dim3', # diminished third
        (2, 3): 'm3',   # minor third
        (2, 4): 'M3',   # major third
        (2, 5): 'M3',   # augmented third
        (3, 4): 'dim4', # diminished fourth
        (3, 5): 'P4',   # perfect fourth
        (3, 6): 'aug4', # augmented fourth
        (4, 6): 'dim5', # diminished fifth
        (4, 7): 'P5',   # perfect fifth
        (4, 8): 'aug5', # augmented fifth
        (5, 7): 'dim6', # diminished sixth
        (5, 8): 'm6',   # minor sixth
        (5, 9): 'M6',   # major sixth
        (5, 10): 'aug6',# augmented sixth
        (6, 9): 'dim7', # diminished seventh
        (6, 10): 'm7',  # minor seventh
        (6, 11): 'M7',  # major seventh
        (6, 12): 'aug7',# augmented seventh
        }

    def __init__(self, note1, note2):
        key_distance = note2.key - note1.key
        position_distance = note2.position - note1.position
        if key_distance > 0:
            self.key_distance = key_distance
            self.position_distance = position_distance
            self.up = True
        elif key_distance < 0:
            self.key_distance = -key_distance
            self.position_distance = -position_distance
            self.up = False
        elif key_distance == 0:
            self.key_distance = 0
            self.position_distance = abs(position_distance)
            self.up = (position_distance >= 0)

    def __repr__(self):
        return 

    def __str__(self):
        """String representation.

        >>> print(Interval(Note("C"), Note("F")))
        +P4
        >>> print(Interval(Note("F"), Note("C")))
        -P4
        >>> print(Interval(Note("C"), Note("C")))
        +P1
        >>> print(Interval(Note("E"), Note("F")))
        +m2
        >>> print(Interval(Note("F"), Note("G")))
        +M2
        >>> print(Interval(Note("E"), Note("G")))
        +m3
        >>> print(Interval(Note("C"), Note("E")))
        +M3
        >>> print(Interval(Note("C"), Note("F#")))
        +aug4
        >>> print(Interval(Note("D"), Note("A")))
        +P5
        >>> print(Interval(Note("C#"), Note("A")))
        +m6
        >>> print(Interval(Note("D"), Note("B")))
        +M6
        >>> print(Interval(Note("C"), Note("Bb")))
        +m7
        >>> print(Interval(Note("C"), Note("B")))
        +M7
        """
        return (("+" if self.up else "-")
                + self.NAMES[(self.key_distance, self.position_distance)])

class Temperament:
    """A single octave tunable keyboard instrument abstraction.

    >>> [str(note) for note in Temperament.NOTES]
    ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
    """
    NOTES = [
        Note(0),     # C
        Note(0, 1),  # C#
        Note(1),     # D
        Note(2, -1), # Eb
        Note(2),     # E
        Note(3),     # F
        Note(3, 1),  # F#
        Note(4),     # G
        Note(4, 1),  # G#
        Note(5),     # A
        Note(6, -1), # Bb
        Note(6),     # B
        ]
    """The twelve notes in an octave on a keyboard."""

    def __init__(self):
        self.frequencies = [None] * 12
        """List of frequencies for each note."""

    def is_tuned(self, position):
        """Checks whether the note at the given position is tuned.

        >>> temp = Temperament()
        >>> temp.is_tuned(4)
        False
        >>> temp.frequencies[4] = 380
        >>> temp.is_tuned(4)
        True
        """
        return self.frequencies[position] is not None

if __name__ == '__main__':
    import doctest
    doctest.testmod()
