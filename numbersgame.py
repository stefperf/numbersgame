# Code solving the May 31, 2019 riddler classic puzzle on https://fivethirtyeight.com/features/can-you-win-the-loteria/
# by exploring the whole space of all possible "Numbers Game" puzzles, as in: <cards, target> combinations.
# The code is efficient enough to run in about 30 minutes on a normal laptop.
# As a bonus, a function solve_puzzle(cards, target) is also given, which returns a solving expression, if it exists.


import itertools
import numpy as np
import random


# sets of allowed cards
SMALL_CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 2
LARGE_CARDS = [25, 50, 75, 100]

# minimum and maximum 3-digit number, delimiting the possible targets
MIN_TARGET = 100
MAX_TARGET = 999


def extract_cards(n_large):
    """
    extract the cards
    :param n_large: number of large cards
    :return: list of cards to be used
    """
    return random.sample(LARGE_CARDS, n_large) + random.sample(SMALL_CARDS, 6 - n_large)


def get_hands(n_large):
    """
    get all possible hands, i.e. card combinations, that are possible with a given choice of n_large large cards,
    considering the effect of the duplications among small cards
    :param n_large: number of large cards
    :return: dictionary matching every hand (as a tuple of integers) with its relative frequency within the set; 
             e.g. get_hands(n_large=2) will contain {... (1, 1, 2, 2, 25, 50): 1, ... (1, 2, 3, 4, 25, 50): 16, ...} 
             because the second combination will be extracted 16 times more frequently
    """
    n_small = 6 - n_large
    hands = {}
    for p_large in itertools.combinations(LARGE_CARDS, n_large):
        for p_small in itertools.combinations(SMALL_CARDS, n_small):
            hand = tuple(sorted(p_large + p_small))
            hands[hand] = hands.get(hand, 0) + 1
    return hands


def solve_puzzle(cards, target):
    """
    bonus function, unneeded to solve the riddle, which gives the solution of a specific puzzle, if possible
    :param cards: list of extracted card values
    :param target: extracted target number
    :return: string with a solving expression or with a message announcing that no solution exists

    Examples:
    >>> solve_puzzle([2, 3, 7, 8, 9, 75], 657)
    '((75 - 2) * 9) == 657'

    >>> solve_puzzle([2, 6, 25, 50, 75, 100], 818)
    'no combination of (100, 75, 50, 25, 6, 2) yields 818'
    """
    class CalcNode:
        """
        auxiliary class storing expressions
        """

        def __init__(self, val, expr=None):
            self.val = val
            self.expr = expr if expr is not None else str(val)

        def __repr__(self):
            return self.expr

        def __lt__(self, other):
            return self.val < other.val

        def __add__(self, other):
            return CalcNode(self.val + other.val, '(%s + %s)' % (self, other))

        def __mul__(self, other):
            return CalcNode(self.val * other.val, '(%s * %s)' % (self, other))

        def __sub__(self, other):
            sub_res = self.val - other.val
            if sub_res > 0:
                return CalcNode(sub_res, '(%s - %s)' % (self, other))
            else:
                raise ValueError

        def __truediv__(self, other):
            div_res = self.val // other.val
            if div_res * other.val == self.val:
                return CalcNode(div_res, '(%s / %s)' % (self, other))
            else:
                raise ValueError

    cards = [CalcNode(c) for c in cards]
    cards = tuple(sorted(cards, reverse=True))
    number_lists = set([cards])
    cardinality = len(cards)
    while cardinality > 1:
        new_number_lists = set()
        for number_set in number_lists:
            for i, m in enumerate(number_set):
                next_numbers = number_set[(i + 1):]
                for j, n in enumerate(next_numbers):
                    other_numbers = number_set[:i] + next_numbers[:j] + next_numbers[(j + 1):]
                    candidates = []
                    if n != 1:  # as multiplying or dividing by 1 never helps
                        candidates.append(m * n)
                        try:
                            candidates.append(m / n)
                        except:
                            pass
                    candidates.append(m + n)
                    try:
                        candidates.append(m - n)
                    except:
                        pass
                    for candidate in candidates:
                        if candidate.val == target:
                            return '%s == %s' % (candidate.expr, target)
                        if cardinality > 2 and candidate not in number_set:
                            new_number_lists.add(tuple(sorted([candidate] + list(other_numbers), reverse=True)))
        number_lists = new_number_lists
        cardinality -= 1
    return 'no combination of %s yields %s' % (cards, target)


def solvable_targets(cards):
    """
    returns all the targets that can be solved with the given cards
    :param cards: list of extracted card values
    :return: array with elements 0 = unsolvable or 1 = solvable for each target, in order from MIN_TARGET to MAX_TARGET
    """
    cards = tuple(sorted(cards, reverse=True))
    targets_solvable = np.full((1000), fill_value=0, dtype=int)
    number_lists = set([cards])
    cardinality = len(cards)
    while cardinality > 1:
        new_number_lists = set()
        for number_set in number_lists:
            for i, m in enumerate(number_set):
                next_numbers = number_set[(i + 1):]
                for j, n in enumerate(next_numbers):
                    other_numbers = number_set[:i] + next_numbers[:j] + next_numbers[(j + 1):]
                    candidates = []
                    if n != 1:  # as multiplying or dividing by 1 never helps
                        candidates.append(m * n)
                        div_res = m // n
                        if n * div_res == m:
                            candidates.append(div_res)
                    candidates.append(m + n)
                    sub_res = m - n
                    if sub_res > 0:  # as getting a negative number is forbidden and getting a 0 never helps
                        candidates.append(sub_res)
                    for candidate in candidates:
                        if candidate <= MAX_TARGET:
                            targets_solvable[candidate] = 1
                        if cardinality > 2 and candidate not in number_set:
                            new_number_lists.add(tuple(sorted([candidate] + list(other_numbers), reverse=True)))
        number_lists = new_number_lists
        cardinality -= 1
    return targets_solvable[100:]


if __name__ == '__main__':
    milestone = 100
    all_counts = np.full((900, 5), fill_value=0, dtype=int)
    denoms = np.full((5), fill_value=0, dtype=int)
    count = 0
    for n_large in range(5):
        hands = get_hands(n_large)
        denoms[n_large] = sum(hands.values())
        for hand, hand_count in hands.items():
            count += 1
            all_counts[:, n_large] += (solvable_targets(hand) * hand_count)
            if not (count % milestone):
                print('Just processed the %s-th card hand = %s, having hand_count = %s' % (count, hand, hand_count))

    probs_by_choice = np.sum(all_counts, axis=0) / (900 * denoms)
    choice_order = np.argsort(probs_by_choice)
    print('\nSolvability probabilities by choice of n_large:')
    for n_large in choice_order[::-1]:
        print('A puzzle with n_large = %s is solvable with probability %.6f%%'
              % (n_large, 100 * probs_by_choice[n_large]))

    weights = 1. / denoms
    probs_by_target = all_counts.dot(weights) / 5
    target_order = np.argsort(probs_by_target)
    print('\nSolvability probabilities by extracted target with random choice of n_large:')
    for t in target_order[::-1]:
        target = t + MIN_TARGET
        print('A puzzle with target = %s is solvable with probability %.2f%%' % (target, 100 * probs_by_target[t]))

    probs_by_target_opt = all_counts[:, 2] / denoms[2]
    target_order_opt = np.argsort(probs_by_target_opt)
    print('\nSolvability probabilities by extracted target with optimal choice of n_large = 2:')
    for t in target_order_opt[::-1]:
        target = t + MIN_TARGET
        print('A puzzle with target = %s is solvable with probability %.2f%%' % (target, 100 * probs_by_target_opt[t]))
