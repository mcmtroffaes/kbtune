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

# from http://code.activestate.com/recipes/576685/
# we can import this from functools from Python 2.7 / 3.2 onwards
def total_ordering(cls):
    'Class decorator that fills-in missing ordering methods'    
    convert = {
        '__lt__': [('__gt__', lambda self, other: other < self),
                   ('__le__', lambda self, other: not other < self),
                   ('__ge__', lambda self, other: not self < other)],
        '__le__': [('__ge__', lambda self, other: other <= self),
                   ('__lt__', lambda self, other: not other <= self),
                   ('__gt__', lambda self, other: not self <= other)],
        '__gt__': [('__lt__', lambda self, other: other > self),
                   ('__ge__', lambda self, other: not other > self),
                   ('__le__', lambda self, other: not self > other)],
        '__ge__': [('__le__', lambda self, other: other >= self),
                   ('__gt__', lambda self, other: not other >= self),
                   ('__lt__', lambda self, other: not self >= other)]
    }
    roots = set(dir(cls)) & set(convert)
    assert roots, 'must define at least one ordering operation: < > <= >='
    root = max(roots)       # prefer __lt __ to __le__ to __gt__ to __ge__
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
    return cls

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

@total_ordering
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
            self.key = key % 7
            self.accidental = accidental

    def __add__(self, interval):
        """Add an interval to the note.

        >>> print(Note('C') + Interval(Note('E'), Note('G')))
        Eb
        >>> print(Note('C') + Interval(Note('G'), Note('E')))
        A
        >>> print(Note('D') + Interval(Note('C'), Note('E')))
        F#
        """
        direction = +1 if interval.up else -1
        # create the new note at the right key, without accidentals for now
        new_note = Note(self.key + interval.key_distance * direction)
        # change the accidentals to match the desired position
        new_note.accidental = (
            (self.position + interval.position_distance * direction) % 12
            - new_note.position)
        return new_note

    def __eq__(self, other):
        return self.key == other.key and self.accidental == other.accidental

    def __ne__(self, other):
        return not(self == other)

    def __lt__(self, other):
        if self.key < other.key:
            return True
        elif self.key == other.key:
            return self.accidental < other.accidental
        else:
            return False

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
        (2, 5): 'aug3', # augmented third
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

    def get_ratio(self):
        """Get the ratio of the natural frequencies of the interval.

        >>> Interval(Note('E'), Note('B')).get_ratio()
        1.5
        >>> Interval(Note('A'), Note('E')).get_ratio()
        0.75
        """
        if self.key_distance == 0 and self.position_distance == 0:
            # perfect unison
            ratio = 1
        elif self.key_distance == 1 and self.position_distance == 2:
            # major second
            ratio = 8 / 7
        elif self.key_distance == 2 and self.position_distance == 3:
            # minor third
            ratio = 6 / 5
        elif self.key_distance == 2 and self.position_distance == 4:
            # major third
            ratio = 5 / 4
        elif self.key_distance == 3 and self.position_distance == 5:
            # perfect fourth
            ratio = 4 / 3
        elif self.key_distance == 3 and self.position_distance == 6:
            # augmented fourth
            ratio = 10 / 7
        elif self.key_distance == 4 and self.position_distance == 6:
            # diminished fifth
            ratio = 7 / 5 # (is less than augmented fourth!!)
        elif self.key_distance == 4 and self.position_distance == 7:
            # perfect fifth
            ratio = 3 / 2
        elif self.key_distance == 5 and self.position_distance == 8:
            # minor sixth
            ratio = 8 / 5
        elif self.key_distance == 5 and self.position_distance == 9:
            # major sixth
            ratio = 10 / 6
        elif self.key_distance == 5 and self.position_distance == 9:
            # minor seventh
            ratio = 7 / 4
        else:
            raise ValueError("Not a natural interval.")
        if self.up:
            return ratio
        else:
            return 1 / ratio
        

    def get_cents(self):
        return ratio_to_cents(self.get_ratio())

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
        >>> print(Interval(Note('G'), Note('E')))
        -m3
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

    MAJOR_THIRD = Interval(Note('C'), Note('E'))
    PERFECT_FIFTH = Interval(Note('C'), Note('G'))

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

    def set_frequency(self, note, freq):
        """Tune a note at a particular frequency.

        >>> temp = Temperament()
        >>> temp.set_frequency(Note('A'), 415)
        >>> temp.frequencies
        [None, None, None, None, None, None, None, None, None, 415, None, None]
        """
        self.frequencies[note.position] = freq

    def get_frequency(self, note):
        """Get frequency of a note.

        >>> temp = Temperament()
        >>> temp.set_frequency(Note('G#'), 400)
        >>> temp.get_frequency(Note('Ab'))
        400
        """
        return self.frequencies[note.position]

    def get_cents(self, note1, note2):
        """Get the (signed) size of the interval in cents."""
        return ratio_to_cents(
            self.get_frequency(note2)
            / self.get_frequency(note1))

    def get_dev_cents(self, note1, note2):
        """Get the deviation of the interval in cents."""
        return (
            self.get_cents(note1, note2)
            - Interval(note1, note2).get_cents())

    def get_dev_bps(self, note1, note2):
        """Get the difference of the first common harmonic in beats
        per second.
        """
        interval = Interval(note1, note2)
        # check that interval is up, if not, reduce to that case
        if not interval.up:
            return -self.get_dev_bps(note2, note1)
        # get frequencies
        freq1 = self.get_frequency(note1)
        freq2 = self.get_frequency(note2)
        # calculate difference in first harmonic, in all cases
        if interval.key_distance == 0 and interval.position_distance == 0:
            # perfect unison
            return freq2 - freq1
        elif interval.key_distance == 1 and interval.position_distance == 2:
            # major second
            return 7 * freq2 - 8 * freq1
        elif interval.key_distance == 2 and interval.position_distance == 3:
            # minor third
            return 5 * freq2 - 6 * freq1
        elif interval.key_distance == 2 and interval.position_distance == 4:
            # major third
            ratio = 4 * freq2 - 5 * freq1
        elif interval.key_distance == 3 and interval.position_distance == 5:
            # perfect fourth
            ratio = 3 * freq2 - 4 * freq1
        elif interval.key_distance == 3 and interval.position_distance == 6:
            # augmented fourth
            ratio = 7 * freq2 - 10 * freq1
        elif interval.key_distance == 4 and interval.position_distance == 6:
            # diminished fifth
            ratio = 5 * freq2 - 7 * freq1 # (is less than augmented fourth!!)
        elif interval.key_distance == 4 and interval.position_distance == 7:
            # perfect fifth
            ratio = 2 * freq2 - 3 * freq1
        elif interval.key_distance == 5 and interval.position_distance == 8:
            # minor sixth
            ratio = 5 * freq2 - 8 * freq1
        elif interval.key_distance == 5 and interval.position_distance == 9:
            # major sixth
            ratio = 6 * freq2 - 10 * freq1
        elif interval.key_distance == 5 and interval.position_distance == 9:
            # minor seventh
            ratio = 4 * freq2 - 7 * freq1
        else:
            raise ValueError("Not a natural interval.")
        if interval.up:
            return ratio
        else:
            return 1 / ratio

    def get_dev_bpm(self, note1, note2):
        """Get the difference of the first common harmonic in beats
        per minute.
        """
        return 60 * self.get_dev_bps(note1, note2)

    def __str__(self):
        """Print information about the temperament.

        >>> temp = Temperament()
        >>> temp.set_frequency(Note('Eb'), 145.73388203017834)
        >>> temp.tune_fifths_up(Note('Eb'), Note('G#'))
        >>> print(temp)
                   INT/c      DEV/c    DEV/bpm
                  % 1200                      
        --------------------------------------
        A -E      701.96       0.00       0.00
        E -B      701.96       0.00       0.00
        B -F#     701.96       0.00       0.00
        F#-C#     701.96       0.00       0.00
        C#-G#     701.96       0.00       0.00
        G#-D#     678.49     -23.46    -477.19
        Eb-Bb     701.96       0.00       0.00
        Bb-F      701.96       0.00       0.00
        F -C      701.96       0.00       0.00
        C -G      701.96       0.00       0.00
        G -D      701.96       0.00       0.00
        D -A      701.96       0.00       0.00
        <BLANKLINE>
        """
        result = (
            "      {0: >10} {1: >10} {2: >10}\n"
            .format("INT/c", "DEV/c", "DEV/bpm"))
        result += (
            "      {0: >10} {1: >10} {2: >10}\n"
            .format("% 1200", "", ""))
        result += (
            "------{0:->10}-{1:->10}-{2:->10}\n"
            .format("", "", ""))
        note = Note('A')
        fifth = Interval(Note('C'), Note('G'))
        while True:
            next_note = note + fifth
            # note: add 1e-8 to avoid -0.00
            result += (
                "{0: <2}-{1: <2} {2: >10.2f} {3: >10.2f} {4: >10.2f}\n"
                .format(
                    note, next_note,
                    self.get_cents(note, next_note) % 1200 + 1e-8,
                    self.get_dev_cents(note, next_note) + 1e-8,
                    self.get_dev_bpm(note, next_note) + 1e-8
                    ))
            note = self.NOTES[next_note.position]
            if note == Note('A'):
                break
        return result

    def tune_fifth_up(self, note, cents=0):
        """Tune a fifth, and return the tuned note.

        >>> temp = Temperament()
        >>> temp.set_frequency(Note('C#'), 300)
        >>> temp.get_frequency(temp.tune_fifth_up(Note('C#')))
        450.0
        >>> temp.get_frequency(temp.tune_fifth_up(Note('G#')))
        337.5
        >>> temp.get_frequency(temp.tune_fifth_up(Note('G#'), -20)) # doctest: +ELLIPSIS
        341.42...
        """
        ratio = cents_to_ratio(cents)
        next_note = note + self.PERFECT_FIFTH
        if next_note > note:
            self.set_frequency(next_note,
                               self.get_frequency(note) * (ratio * 3 / 2))
        else:
            self.set_frequency(next_note,
                               self.get_frequency(note) / (ratio * 4 / 3))
        return next_note

    def tune_fifths_up(self, note1, note2, cents=0):
        """Tune fifths going up (or fourths going down), from note1 to note2,
        such that each fifth has exactly the given deviation in cents.

        >>> # test this with pythagoras
        >>> temp = Temperament()
        >>> temp.set_frequency(Note('Eb'),
        ...                    (415/2)/(3/2)*(4/3)/(3/2)*(4/3)*(4/3)/(3/2))
        >>> temp.tune_fifths_up(Note('Eb'), Note('G#'))
        >>> print(2 * temp.get_frequency(Note('A')))
        415.0
        """
        note = note1
        while note != note2:
            note = self.tune_fifth_up(note, cents)

    def tune_major_third(self, note1, note2, cents=0):
        """Tune a major third by tuning four identical fifths, such that the
        resulting third has the given deviation in cents.
        """

if __name__ == '__main__':
    import doctest
    doctest.testmod()
