#!/usr/bin/env python

import copy
import itertools
import sys


class AttributeTypeAlreadyAssociated(Exception):
    def __init__(self):
        Exception.__init__(self)


class Attribute(object):
    def __init__(self, name, values):
        object.__init__(self)
        self.name = name
        self.values = values


class Solution(object):
    def __init__(self):
        object.__init__(self)

        self.__mapping = numpy.eye(
            Solution._index.attribute_count(),
            dtype=bool
        )
        self.__associated_categories = numpy.zeros(
            (Solution._index.attribute_count(), Solution._index.category_count()),
            dtype=bool
        )

        for index, category in Solution._index.itervalues():
            self.__associated_categories[index][category] = True

    def associate(self, attribute_a, attribute_b):



        attribute_a_index, attribute_a_category = Solution._index[attribute_a]
        attribute_b_index, attribute_b_category = Solution._index[attribute_b]

        if any([
            self.__associated_categories[attribute_a_index][attribute_b_category],
            self.__associated_categories[attribute_b_index][attribute_a_category]
        ]):
            raise AttributeTypeAlreadyAssociated()

        self.__mapping[attribute_a_index][attribute_b_index] = True
        self.__mapping[attribute_b_index][attribute_a_index] = True
        self.__associated_categories[attribute_a_index][attribute_b_category] = True
        self.__associated_categories[attribute_b_index][attribute_a_category] = True

    def __associated_with(self, attribute):
        return [

        ]

    def __associate_pair(self, attribute_a, attribute_b):
        attribute_a_index, attribute_a_category = Solution._index[attribute_a]
        attribute_b_index, attribute_b_category = Solution._index[attribute_b]

        if any([
            self.__associated_categories[attribute_a_index][attribute_b_category],
            self.__associated_categories[attribute_b_index][attribute_a_category]
        ]):
            raise AttributeTypeAlreadyAssociated()

        self.__mapping[attribute_a_index][attribute_b_index] = True
        self.__mapping[attribute_b_index][attribute_a_index] = True
        self.__associated_categories[attribute_a_index][attribute_b_category] = True
        self.__associated_categories[attribute_b_index][attribute_a_category] = True

    def is_associated(self, attribute_a, attribute_b):
        attribute_a_index, _ = Solution._index[attribute_a]
        attribute_b_index, _ = Solution._index[attribute_b]
        return self.__mapping[attribute_a_index][attribute_b_index]

    def copy(self):
        return copy.deepcopy(self)

    def result(self):
        # while any(
        #         self.__fill_existing(),
        #         self.__fill_missing()
        # ):
        #     pass

        return {
            name: [
                heirloom
                for heirloom in Solution._heirlooms
                if self.is_associated(name, heirloom)
                ]
            for name in Solution._names
        }


class Condition(object):
    class Association(object):
        def __init__(self, attribute_a, attribute_b):
            object.__init__(self)
            self.attribute_a = attribute_a
            self.attribute_b = attribute_b

    class Alternative(object):
        def __init__(self, associations):
            object.__init__(self)
            self.associations = associations

    def __init__(self, alternatives):
        object.__init__(self)
        self.alternatives = alternatives

    def apply(self, solutions):
        new_solutions = []

        for solution in solutions:
            for alternative, new_solution in zip(
                self.alternatives,
                [solution] + [solution.copy() for _ in xrange(len(self.alternatives) - 1)]
            ):
                try:
                    for association in alternative.associations:
                        new_solution.associate(
                            association.attribute_a,
                            association.attribute_b
                        )

                    new_solutions.append(new_solution)

                except AttributeTypeAlreadyAssociated:
                    pass

        return new_solutions

    @classmethod
    def is_same_person(cls, attribute_a, attribute_b):
        return cls([
            cls.Alternative([
                cls.Association(attribute_a, attribute_b)
            ])
        ])





# ==================================================================================================================== #

attributes = [
    Attribute(
        'name',
        ['Lady Winslow', 'Doctor Marcolla', 'Countess Contee', 'Madam Natsiou', 'Baroness Finch']
    ),
    Attribute(
        'heirloom',
        ['Diamond', 'Ring', 'Bird Pendant', 'War Medal', 'Snuff Tin']
    ),
    Attribute(
        'color',
        ['purple', 'red', 'green', 'white', 'blue']
    ),
    Attribute(
        'drink',
        ['beer', 'rum', 'wine', 'whiskey', 'absinthe']
    ),
    Attribute(
        'city',
        ['Dunwall', 'Dabokva', 'Baleton', 'Fraeport', 'Karnaca']
    ),
    Attribute(
        'seat',
        ['leftmost', 'center-left', 'center', 'center-right', 'rightmost']
    )
]


conditions = [
    Condition.is_same_person('Madam Natsiou', 'purple'),
    Condition.is_same_person('Doctor Marcolla', 'Diamond')
]


def main():
    solutions = [Solution(attributes)]

    for condition in conditions:
        solutions = condition.apply(solutions)

    print 'Found {} solution(s):'.format(len(solutions))

    for solution_index, solution in enumerate(solutions, 1):
        print '{}. {}'.format(solution_index, solution.result())


if __name__ == '__main__':
    sys.exit(main())
