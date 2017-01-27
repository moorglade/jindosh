#!/usr/bin/env python

import copy
import itertools
import sys


class Attribute(object):
    def __init__(self, name, values):
        object.__init__(self)
        self.name = name
        self.values = values


class AttributeValue(object):
    def __init__(self, name, value):
        object.__init__(self)
        self.name = name
        self.value = value

    def __eq__(self, other):
        return all([
            self.name == other.name,
            self.value == other.value
        ])

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'AttributeValue({}, {})'.format(self.name, self.value)


class AttributeValueAlreadyAssociated(Exception):
    def __init__(self):
        Exception.__init__(self)


class Solution(object):
    def __init__(self, attributes):
        object.__init__(self)

        self.__associations = {
            attribute.name: {
                attribute_value: {
                    associated_attribute.name:
                        None if attribute.name != associated_attribute.name
                        else attribute_value
                    for associated_attribute in attributes
                }
                for attribute_value in attribute.values
            }
            for attribute in attributes
        }

    def copy(self):
        return copy.deepcopy(self)

    def __str__(self):
        import yaml
        return yaml.dump(self.__associations)

    def associate(self, attribute_value_a, attribute_value_b):
        print self.__all_associated(attribute_value_a)
        print self.__all_associated(attribute_value_b)

        for associated_value_a in self.__all_associated(attribute_value_a):
            for associated_value_b in self.__all_associated(attribute_value_b):
                self.__associate_pair(associated_value_a, associated_value_b)

    def __all_associated(self, attribute_value):
        return [
            AttributeValue(associated_attribute_name, associated_attribute_value)
            for associated_attribute_name, associated_attribute_value
            in self.__associations[attribute_value.name][attribute_value.value].iteritems()
            if associated_attribute_value
        ]

    def __associate_pair(self, attribute_value_a, attribute_value_b):
        self.__associate_pair_one_way(attribute_value_a, attribute_value_b)
        self.__associate_pair_one_way(attribute_value_b, attribute_value_a)

    def __associate_pair_one_way(self, attribute_value_from, attribute_value_to):
        # check if attributes are different
        if attribute_value_from != attribute_value_to:
            current_association = self.__associations[attribute_value_from.name][attribute_value_from.value][attribute_value_to.name]

            # check if the attribute is already associated
            if current_association is not None:
                # check if the attribute is associated to a different value
                if current_association != attribute_value_to.value:
                    raise AttributeValueAlreadyAssociated()
            else:
                # associate the attribute
                self.__associations[attribute_value_from.name][attribute_value_from.value][attribute_value_to.name] = attribute_value_to.value

    def infer(self):
        attribute_names = self.__associations.keys()

        while True:
            inferred_pairs = []
            attribute_names_checked = []

            for attribute_name_a in attribute_names:
                attribute_names_checked.append(attribute_name_a)

                for attribute_name_b in attribute_names:
                    # skip the already checked attributes (remember - it's a two-way mapping)
                    if attribute_name_b not in attribute_names_checked:
                        unassociated_values_a = self.__find_unassociated_values(attribute_name_a, attribute_name_b)

                        # single leftover value - let's associate it!
                        if len(unassociated_values_a) == 1:
                            unassociated_values_b = self.__find_unassociated_values(attribute_name_b, attribute_name_a)
                            assert len(unassociated_values_b) == 1

                            unassociated_value_a = unassociated_values_a[0]
                            unassociated_value_b = unassociated_values_b[0]

                            inferred_pairs.append((
                                AttributeValue(attribute_name_a, unassociated_value_a),
                                AttributeValue(attribute_name_b, unassociated_value_b)
                            ))

            if len(inferred_pairs) == 0:
                break

            for attribute_value_a, attribute_value_b in inferred_pairs:
                self.associate(attribute_value_a, attribute_value_b)

    def __find_unassociated_values(self, attribute_name_from, attribute_name_to):
        return [
            attribute_value_from
            for attribute_value_from in self.__associations[attribute_name_from]
            if self.__associations[attribute_name_from][attribute_value_from][attribute_name_to] is None
        ]


#         attribute_a_index, attribute_a_category = Solution._index[attribute_a]
#         attribute_b_index, attribute_b_category = Solution._index[attribute_b]
#
#         if any([
#             self.__associated_categories[attribute_a_index][attribute_b_category],
#             self.__associated_categories[attribute_b_index][attribute_a_category]
#         ]):
#             raise AttributeValueAlreadyAssociated()
#
#         self.__mapping[attribute_a_index][attribute_b_index] = True
#         self.__mapping[attribute_b_index][attribute_a_index] = True
#         self.__associated_categories[attribute_a_index][attribute_b_category] = True
#         self.__associated_categories[attribute_b_index][attribute_a_category] = True
#
#     def __associated_with(self, attribute):
#         return [
#
#         ]
#
#     def __associate_pair(self, attribute_a, attribute_b):
#         attribute_a_index, attribute_a_category = Solution._index[attribute_a]
#         attribute_b_index, attribute_b_category = Solution._index[attribute_b]
#
#         if any([
#             self.__associated_categories[attribute_a_index][attribute_b_category],
#             self.__associated_categories[attribute_b_index][attribute_a_category]
#         ]):
#             raise AttributeValueAlreadyAssociated()
#
#         self.__mapping[attribute_a_index][attribute_b_index] = True
#         self.__mapping[attribute_b_index][attribute_a_index] = True
#         self.__associated_categories[attribute_a_index][attribute_b_category] = True
#         self.__associated_categories[attribute_b_index][attribute_a_category] = True
#
#     def is_associated(self, attribute_a, attribute_b):
#         attribute_a_index, _ = Solution._index[attribute_a]
#         attribute_b_index, _ = Solution._index[attribute_b]
#         return self.__mapping[attribute_a_index][attribute_b_index]
#
#     def copy(self):
#         return copy.deepcopy(self)
#
#     def result(self):
#         # while any(
#         #         self.__fill_existing(),
#         #         self.__fill_missing()
#         # ):
#         #     pass
#
#         return {
#             name: [
#                 heirloom
#                 for heirloom in Solution._heirlooms
#                 if self.is_associated(name, heirloom)
#                 ]
#             for name in Solution._names
#         }
#
#
# class Condition(object):
#     class Association(object):
#         def __init__(self, attribute_a, attribute_b):
#             object.__init__(self)
#             self.attribute_a = attribute_a
#             self.attribute_b = attribute_b
#
#     class Alternative(object):
#         def __init__(self, associations):
#             object.__init__(self)
#             self.associations = associations
#
#     def __init__(self, alternatives):
#         object.__init__(self)
#         self.alternatives = alternatives
#
#     def apply(self, solutions):
#         new_solutions = []
#
#         for solution in solutions:
#             for alternative, new_solution in zip(
#                 self.alternatives,
#                 [solution] + [solution.copy() for _ in xrange(len(self.alternatives) - 1)]
#             ):
#                 try:
#                     for association in alternative.associations:
#                         new_solution.associate(
#                             association.attribute_a,
#                             association.attribute_b
#                         )
#
#                     new_solutions.append(new_solution)
#
#                 except AttributeValueAlreadyAssociated:
#                     pass
#
#         return new_solutions
#
#     @classmethod
#     def is_same_person(cls, attribute_a, attribute_b):
#         return cls([
#             cls.Alternative([
#                 cls.Association(attribute_a, attribute_b)
#             ])
#         ])
#
#



# ==================================================================================================================== #

riddle_attributes = [
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

#
# conditions = [
#     Condition.is_same_person('Madam Natsiou', 'purple'),
#     Condition.is_same_person('Doctor Marcolla', 'Diamond')
# ]


def main():
    solutions = [Solution(riddle_attributes)]

    solutions[0].associate(
        AttributeValue('drink', 'beer'),
        AttributeValue('color', 'purple')
    )
    solutions[0].associate(
        AttributeValue('drink', 'rum'),
        AttributeValue('color', 'red')
    )
    solutions[0].associate(
        AttributeValue('drink', 'wine'),
        AttributeValue('color', 'green')
    )
    solutions[0].associate(
        AttributeValue('drink', 'whiskey'),
        AttributeValue('color', 'white')
    )

    solutions[0].infer()

    print solutions[0]


    #
    # for condition in conditions:
    #     solutions = condition.apply(solutions)
    #
    # print 'Found {} solution(s):'.format(len(solutions))
    #
    # for solution_index, solution in enumerate(solutions, 1):
    #     print '{}. {}'.format(solution_index, solution.result())


if __name__ == '__main__':
    sys.exit(main())
