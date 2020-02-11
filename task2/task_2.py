from functools import total_ordering
import re


HASH_NORMALIZATION_LIMIT = 10

RELEASE_CANDIDATE_WEIGHT = -1
BETA_WEIGHT = -2
ALPHA_WEIGHT = -3


@total_ordering
class Version:

    _word_priority = {"a": ALPHA_WEIGHT, "alpha": ALPHA_WEIGHT,
                      "b": BETA_WEIGHT, "beta": BETA_WEIGHT,
                      "rc": RELEASE_CANDIDATE_WEIGHT
                      }

    _version_parser = re.compile(r"[0-9]+|[a-zA-Z]+")

    def __init__(self, version: str):
        self._value: str = version
        self._value_tuple: tuple = None
        self._hash_value: int = None

    @property  # This class produces immutable objects
    def value(self):
        return self._value

    @property
    def value_tuple(self):
        if self._value_tuple is None:
            value_list_row = self._version_parser.findall(self.value)
            for index, value in enumerate(value_list_row):
                if value.isnumeric():
                    value_list_row[index] = int(value)
                else:
                    value_list_row[index] = self._word_priority[value.lower()]

            self._value_tuple = tuple(value_list_row)

        return self._value_tuple

    @staticmethod
    def _normalize_len_for_compares(seq1: tuple, seq2: tuple):
        """
        This is used so that comparative operators calculate correctly in this class.
        This function takes sequences and enlarge shorter sequence up to a larger sequence using zeros.
        For example:
          Input: seq1 == (1, 0), seq2 == (1, 0, 0)
          Output: seq == (1, 0, 0), seq2 == (1, 0, 0)
        Without this function comparing logic for this class would work wrong.
        Normal version logic looks like [version 1.7 == version 1.7.0] but (1, 7) != (1, 7, 0).
        But if sequences have equal length, it works as it should because (1, 7, 0) == (1, 7, 0)
        """
        if len(seq1) == len(seq2):
            return seq1, seq2

        elif len(seq1) > len(seq2):
            diff = len(seq1) - len(seq2)
            seq2_extended = seq2 + (0,) * diff
            return seq1, seq2_extended

        else:
            diff = len(seq2) - len(seq1)
            seq1_extended = seq1 + (0,) * diff
            return seq1_extended, seq2

    def __eq__(self, other):
        if self.value_tuple == other.value_tuple:
            return True
        else:
            seq1, seq2 = self._normalize_len_for_compares(self.value_tuple, other.value_tuple)
            return seq1 == seq2

    def __lt__(self, other):
        seq1, seq2 = self._normalize_len_for_compares(self.value_tuple, other.value_tuple)
        return seq1 < seq2

    @staticmethod
    def _normalize_len_for_hash(seq: tuple, up_to_value: int):
        """
        This function uses the same way as "_normalize_len_for_compares".
        But the maximum length cannot be known. It can be just suggested.
        So hash function works correctly if quantity of version parts (for example '1.0.0-alpha.1' has 5 ones) is
        less then constant HASH_NORMALIZATION_LIMIT.
        """
        if len(seq) <= up_to_value:
            diff = up_to_value - len(seq)
            return seq + (0,) * diff
        else:
            raise Exception("Version has more parts than expected. HASH_NORMALIZATION_LIMIT should be increased.")

    def __hash__(self):
        """
        This way was chosen because source version string say nothing to comparator.
        Version("2.0") == Version("2.0.0.0") so hashes must be equal too.
        The function like [hash(hash(a)^hash(b)^...)] cannot be used because it creates many collisions using
        small ints and those hashes would have no sense.
        Should be replaced by more faster algorithm if it's necessary.
        """
        if self._hash_value is None:
            self._hash_value = hash(self._normalize_len_for_hash(self.value_tuple, HASH_NORMALIZATION_LIMIT))
        return self._hash_value

    def __repr__(self):
        return f"{type(self).__name__}('{self.value}')"


def main():
    to_test = [
        ('1.0.0', '2.0.0'),
        ('1.0.0', '1.42.0'),
        ('1.2.0', '1.2.42'),
        ('1.1.0-alpha', '1.2.0-alpha.1'),
        ('1.0.1b', '1.0.10-alpha.beta'),
        ('1.0.0-rc.1', '1.0.0'),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), 'le failed'
        assert Version(version_2) > Version(version_1), 'ge failed'
        assert Version(version_2) != Version(version_1), 'neq failed'


if __name__ == "__main__":
    main()
