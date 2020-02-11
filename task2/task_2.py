from functools import total_ordering
import re


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

    @staticmethod
    def _normalize_len(seq1: tuple, seq2: tuple):
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

    def __init__(self, version: str):
        self._value = version
        self._value_tuple = None

    @property
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

    def __eq__(self, other):
        if self.value_tuple == other.value_tuple:
            return True
        else:
            seq1, seq2 = self._normalize_len(self.value_tuple, other.value_tuple)
            return seq1 == seq2

    def __lt__(self, other):
        seq1, seq2 = self._normalize_len(self.value_tuple, other.value_tuple)
        return seq1 < seq2

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
