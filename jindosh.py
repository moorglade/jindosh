#!/usr/bin/env python

import copy
import sys


# -------------------------------------------------------------------------------------------------------------------- #
# General riddling apparatus                                                                                           #
# -------------------------------------------------------------------------------------------------------------------- #

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

    def __repr__(self):
        attribute_names_sorted = sorted(self.__attribute_names())

        lines = []

        for attribute_name in attribute_names_sorted:
            attribute_lines = []

            for attribute_value in sorted(self.__attribute_values(attribute_name)):
                associated_attribute_values = []
                for associated_attribute_name in attribute_names_sorted:
                    if attribute_name != associated_attribute_name:
                        associated_attribute_value = self.__associations[attribute_name][attribute_value][associated_attribute_name]
                        if associated_attribute_value is not None:
                            associated_attribute_values.append(associated_attribute_value)

                if len(associated_attribute_values) > 0:
                    attribute_line = \
                        '{:<16} [ '.format(attribute_value).upper() \
                        + ' | '.join([
                            '{:<16}'.format(associated_attribute_value)
                            for associated_attribute_value in associated_attribute_values
                        ]) \
                        + ']'

                    attribute_lines.append(attribute_line)

            if len(attribute_lines) > 0:
                lines.extend(attribute_lines)
                lines.append('')

        return '\n'.join(lines)

    def __attribute_names(self):
        return self.__associations.iterkeys()

    def __attribute_values(self, attribute_name):
        return self.__associations[attribute_name].iterkeys()

    def associate(self, attribute_value_a, attribute_value_b):
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
        # check if attributes are different
        if attribute_value_a != attribute_value_b:
            self.__associate_pair_one_way(attribute_value_a, attribute_value_b)
            self.__associate_pair_one_way(attribute_value_b, attribute_value_a)

    def __associate_pair_one_way(self, attribute_value_from, attribute_value_to):
            current_association_value = self.__associations[attribute_value_from.name][attribute_value_from.value][attribute_value_to.name]

            # check if the attribute is already associated
            if current_association_value is not None:
                # check if the attribute is associated to a different value
                if current_association_value != attribute_value_to.value:
                    raise AttributeValueAlreadyAssociated()
            else:
                # associate the attribute
                self.__associations[attribute_value_from.name][attribute_value_from.value][attribute_value_to.name] = attribute_value_to.value

    def infer(self):
        while True:
            inferred_pairs = []
            attribute_names_checked = []

            for attribute_a_name in self.__attribute_names():
                attribute_names_checked.append(attribute_a_name)

                for attribute_a_value in self.__attribute_values(attribute_a_name):
                    for attribute_b_name in self.__attribute_names():
                        if all([
                            attribute_b_name not in attribute_names_checked,
                            self.__associations[attribute_a_name][attribute_a_value][attribute_b_name] is None
                        ]):
                            attribute_b_possible_values = [
                                attribute_b_value
                                for attribute_b_value in self.__attribute_values(attribute_b_name)
                                if self.__is_association_possible(
                                    attribute_a_name, attribute_a_value,
                                    attribute_b_name, attribute_b_value
                                )
                            ]

                            # single leftover value - let's associate it!
                            if len(attribute_b_possible_values) == 1:
                                attribute_b_value = attribute_b_possible_values[0]

                                inferred_pairs.append((
                                    AttributeValue(attribute_a_name, attribute_a_value),
                                    AttributeValue(attribute_b_name, attribute_b_value)
                                ))

            if len(inferred_pairs) == 0:
                # we're not inferring anything anymore
                break

            for attribute_a_value, attribute_b_value in inferred_pairs:
                self.associate(attribute_a_value, attribute_b_value)

    def __is_association_possible(self, attribute_a_name, attribute_a_value, attribute_b_name, attribute_b_value):
        for attribute_name in self.__attribute_names():
            attribute_a_associated_value = self.__associations[attribute_a_name][attribute_a_value][attribute_name]
            attribute_b_associated_value = self.__associations[attribute_b_name][attribute_b_value][attribute_name]

            if all([
                attribute_a_associated_value is not None,
                attribute_b_associated_value is not None,
                attribute_a_associated_value != attribute_b_associated_value
            ]):
                return False

        return True

    def result(self, attribute_a_name, attribute_b_name):
        return {
            attribute_a_value: self.__associations[attribute_a_name][attribute_a_value][attribute_b_name]
            for attribute_a_value in self.__attribute_values(attribute_a_name)
        }


class Condition(object):
    class Association(object):
        def __init__(self, attribute_a_value, attribute_b_value):
            object.__init__(self)
            self.attribute_a_value = attribute_a_value
            self.attribute_b_value = attribute_b_value

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
                            association.attribute_a_value,
                            association.attribute_b_value
                        )

                    new_solution.infer()

                    new_solutions.append(new_solution)

                except AttributeValueAlreadyAssociated:
                    pass

        return new_solutions


def solve(attributes, conditions):
    solutions = [Solution(attributes)]

    for condition in conditions:
        solutions = condition.apply(solutions)

    return solutions


# -------------------------------------------------------------------------------------------------------------------- #
# Riddle-specific routines                                                                                             #
# -------------------------------------------------------------------------------------------------------------------- #

def is_same_person(attribute_a_value, attribute_b_value):
    return Condition([
        Condition.Alternative([
            Condition.Association(attribute_a_value, attribute_b_value)
        ])
    ])


def sit_left_right(attribute_value_left, attribute_value_right):
    seats_left_to_right = ['far left', 'center-left', 'center', 'center-right', 'far right']

    return Condition([
        Condition.Alternative([
            Condition.Association(attribute_value_left, AttributeValue('seat', seats_left_to_right[left_seat_index])),
            Condition.Association(attribute_value_right, AttributeValue('seat', seats_left_to_right[left_seat_index + 1]))
        ])
        for left_seat_index in xrange(0, len(seats_left_to_right) - 1)
    ])


def sit_next_to(attribute_a_value, attribute_b_value):
    left_right_alternatives = sit_left_right(attribute_a_value, attribute_b_value).alternatives
    right_left_alternatives = sit_left_right(attribute_b_value, attribute_a_value).alternatives

    return Condition(left_right_alternatives + right_left_alternatives)


def main():
    # riddle attributes and rules - could be easily adapted for file input

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
            ['far left', 'center-left', 'center', 'center-right', 'far right']
        )
    ]

    conditions = [
        # Madam Natsiou - purple
        is_same_person(
            AttributeValue('name', 'Madam Natsiou'),
            AttributeValue('color', 'purple')
        ),
        # Lady Winslow - far left
        is_same_person(
            AttributeValue('name', 'Lady Winslow'),
            AttributeValue('seat', 'far left')
        ),
        # Lady Winslow - next to red
        sit_next_to(
            AttributeValue('name', 'Lady Winslow'),
            AttributeValue('color', 'red')
        ),
        # green - left to white
        sit_left_right(
            AttributeValue('color', 'green'),
            AttributeValue('color', 'white')
        ),
        # green - beer
        is_same_person(
            AttributeValue('color', 'green'),
            AttributeValue('drink', 'beer')
        ),
        # Dunwall - blue
        is_same_person(
            AttributeValue('city', 'Dunwall'),
            AttributeValue('color', 'blue')
        ),
        # Ring - next to Dunwall
        sit_next_to(
            AttributeValue('heirloom', 'Ring'),
            AttributeValue('city', 'Dunwall')
        ),
        # Doctor Marcolla - Diamond
        is_same_person(
            AttributeValue('name', 'Doctor Marcolla'),
            AttributeValue('heirloom', 'Diamond')
        ),
        # Dabokva - War Medal
        is_same_person(
            AttributeValue('city', 'Dabokva'),
            AttributeValue('heirloom', 'War Medal')
        ),
        # Snuff Tin - next to Baleton
        sit_next_to(
            AttributeValue('heirloom', 'Snuff Tin'),
            AttributeValue('city', 'Baleton')
        ),
        # Baleton - next to rum
        sit_next_to(
            AttributeValue('city', 'Baleton'),
            AttributeValue('drink', 'rum')
        ),
        # unsure: Snuff Tin - rum
        is_same_person(
            AttributeValue('heirloom', 'Snuff Tin'),
            AttributeValue('drink', 'rum')
        ),
        # Countess Contee - wine
        is_same_person(
            AttributeValue('name', 'Countess Contee'),
            AttributeValue('drink', 'wine')
        ),
        # Fraeport - whiskey
        is_same_person(
            AttributeValue('city', 'Fraeport'),
            AttributeValue('drink', 'whiskey')
        ),
        # center - absinthe
        is_same_person(
            AttributeValue('seat', 'center'),
            AttributeValue('drink', 'absinthe')
        ),
        # Baroness Finch - Karnaca
        is_same_person(
            AttributeValue('name', 'Baroness Finch'),
            AttributeValue('city', 'Karnaca')
        )
    ]

    solutions = solve(attributes, conditions)

    print 'Found {} solution(s):'.format(len(solutions))
    print

    for solution_index, solution in enumerate(solutions, 1):
        print 'Solution {}:'.format(solution_index)
        print
        result = solution.result('name', 'heirloom')
        for attribute_a_value in sorted(result.keys()):
            print '{:16}: {:16}'.format(attribute_a_value, result[attribute_a_value])
        print


if __name__ == '__main__':
    sys.exit(main())
