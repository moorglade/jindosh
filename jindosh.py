#!/usr/bin/env python

import copy
import itertools
import numpy
import sys


class CategoryAlreadyAssociated(Exception):
    def __init__(self):
        Exception.__init__(self)


class Solution(object):
    class _Index(dict):
        def __init__(self, categories):
            item_to_category = {
                category_item: category_index
                for category_index, category_items in enumerate(categories)
                for category_item in category_items
                }
            items = [
                (item, (index, item_to_category[item]))
                for index, item in enumerate(itertools.chain(*categories))
                ]

            dict.__init__(self, items)
            self.__category_count = len(categories)

        def item_count(self):
            return len(self)

        def category_count(self):
            return self.__category_count

    _women = [
        'Lady Winslow',
        'Doctor Marcolla',
        'Countess Contee',
        'Madam Natsiou',
        'Baroness Finch'
    ]

    _heirlooms = [
        'Diamond',
        'Ring',
        'Bird Pendant',
        'War Medal',
        'Snuff Tin'
    ]

    _colors = [
        'purple',
        'red',
        'green',
        'white',
        'blue'
    ]

    _drinks = [
        'beer',
        'rum',
        'wine',
        'whiskey',
        'absinthe'
    ]

    _cities = [
        'Dunwall',
        'Dabokva',
        'Baleton',
        'Fraeport',
        'Karnaca'
    ]

    _seats = [
        'leftmost',
        'center-left',
        'center',
        'center-right',
        'rightmost'
    ]

    _index = _Index([
        _women,
        _heirlooms,
        _colors,
        _drinks,
        _cities,
        _seats
    ])

    def __init__(self):
        object.__init__(self)

        self.__mapping = numpy.zeros(
            (Solution._index.item_count(), Solution._index.item_count()),
            dtype=bool
        )
        self.__associated_categories = numpy.zeros(
            (Solution._index.item_count(), Solution._index.category_count()),
            dtype=bool
        )

        for index, category in Solution._index.itervalues():
            self.__associated_categories[index][category] = True

    def associate(self, item_a, item_b):
        item_a_index, item_a_category = Solution._index[item_a]
        item_b_index, item_b_category = Solution._index[item_b]

        if any([
            self.__associated_categories[item_a_index][item_b_category],
            self.__associated_categories[item_b_index][item_a_category]
        ]):
            raise CategoryAlreadyAssociated()

        self.__mapping[item_a_index][item_b_index] = True
        self.__mapping[item_b_index][item_a_index] = True
        self.__associated_categories[item_a_index][item_b_category] = True
        self.__associated_categories[item_b_index][item_a_category] = True

    def is_associated(self, item_a, item_b):
        item_a_index, _ = Solution._index[item_a]
        item_b_index, _ = Solution._index[item_b]
        return self.__mapping[item_a_index][item_b_index]

    def copy(self):
        return copy.deepcopy(self)

    def result(self):
        # while any(
        #         self.__fill_existing(),
        #         self.__fill_missing()
        # ):
        #     pass

        return {
            woman: [
                heirloom
                for heirloom in Solution._heirlooms
                if self.is_associated(woman, heirloom)
                ]
            for woman in Solution._women
            }


conditions = [
    # Madam Natsiou - purple
    [[('Madam Natsiou', 'purple')]],


    # Doctor Marcolla - Diamond
    [[('Doctor Marcolla', 'Diamond')]],
]


def main():
    solutions = [Solution()]

    for condition in conditions:
        solutions = _apply_condition(solutions, condition)

    print 'Found {} solution(s):'.format(len(solutions))

    for solution_index, solution in enumerate(solutions, 1):
        print '{}. {}'.format(solution_index, solution.result())


def _apply_condition(solutions, condition):
    new_solutions = []

    for old_solution in solutions:
        for condition_variant in condition:
            try:
                new_solution = old_solution if len(condition) == 1 else old_solution.copy()

                for condition_item_a, condition_item_b in condition_variant:
                    new_solution.associate(condition_item_a, condition_item_b)

                new_solutions.append(new_solution)

            except CategoryAlreadyAssociated:
                pass

    return new_solutions


if __name__ == '__main__':
    sys.exit(main())
