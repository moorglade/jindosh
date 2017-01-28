#!/usr/bin/env python

import copy
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

    def __repr__(self):
        lines = []

        for attribute_name in self.__associations:
            attribute_lines = []

            for attribute_value in self.__associations[attribute_name]:
                associated_attribute_values = [
                    associated_attribute_value
                    for associated_attribute_value in self.__associations[attribute_name][attribute_value].itervalues()
                    if associated_attribute_value is not None and associated_attribute_value != attribute_value
                ]

                if len(associated_attribute_values) > 0:
                    attribute_lines.append(' '.join([attribute_value, '\t|'] + associated_attribute_values))

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
         while True:
            inferred_pairs = []
            # attribute_names_checked = []
            # TODO: optimize?
            # attribute_names_checked.append(attribute_name_a)

            for attribute_name_a in self.__attribute_names():
                print 'att a', attribute_name_a

                for attribute_value_a in self.__attribute_values(attribute_name_a):
                    for attribute_name_b in self.__attribute_names():

                        print 'att b', attribute_name_b


                        if all([
                            attribute_name_a != attribute_name_b,
                            self.__associations[attribute_name_a][attribute_value_a][attribute_name_b] is None
                        ]):
                            attribute_possible_values = [
                                attribute_value_b
                                for attribute_value_b in self.__attribute_values(attribute_name_b)
                                if self.__is_association_possible(
                                    attribute_name_a, attribute_value_a,
                                    attribute_name_b, attribute_value_b
                                )
                            ]

                            # single leftover value - let's associate it!
                            if len(attribute_possible_values) == 1:
                                attribute_value_b = attribute_possible_values[0]

                                inferred_pairs.append((
                                    AttributeValue(attribute_name_a, attribute_value_a),
                                    AttributeValue(attribute_name_b, attribute_value_b)
                                ))

            if len(inferred_pairs) == 0:
                break

            for attribute_value_a, attribute_value_b in inferred_pairs:
                self.associate(attribute_value_a, attribute_value_b)

    def __is_association_possible(self, attribute_name_a, attribute_value_a, attribute_name_b, attribute_value_b):
        if all([
            attribute_value_a == 'Lady Winslow',
            attribute_value_b == 'purple',
            self.__associations['color']['purple']['name'] == 'Madam Natsiou'
        ]):
            print 'hehe'

        for attribute_name in self.__attribute_names():
            attribute_value_associated_with_a = self.__associations[attribute_name_a][attribute_value_a][attribute_name]
            attribute_value_associated_with_b = self.__associations[attribute_name_b][attribute_value_b][attribute_name]

            if all([
                attribute_value_associated_with_a is not None,
                attribute_value_associated_with_b is not None,
                attribute_value_associated_with_a != attribute_value_associated_with_b
            ]):
                return False

        return True


class Condition(object):
    class Association(object):
        def __init__(self, attribute_value_a, attribute_value_b):
            object.__init__(self)
            self.attribute_value_a = attribute_value_a
            self.attribute_value_b = attribute_value_b

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
                            association.attribute_value_a,
                            association.attribute_value_b
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


# ==================================================================================================================== #


def is_same_person(attribute_value_a, attribute_value_b):
    return Condition([
        Condition.Alternative([
            Condition.Association(attribute_value_a, attribute_value_b)
        ])
    ])


def sit_left_right(attribute_value_left, attribute_value_right):
    seats_left_to_right = ['leftmost', 'center-left', 'center', 'center-right', 'rightmost']

    return Condition([
        Condition.Alternative([
            Condition.Association(attribute_value_left, AttributeValue('seat', seats_left_to_right[left_seat_index])),
            Condition.Association(attribute_value_right, AttributeValue('seat', seats_left_to_right[left_seat_index + 1]))
        ])
        for left_seat_index in xrange(0, len(seats_left_to_right) - 1)
    ])


def sit_next_to(attribute_value_a, attribute_value_b):
    left_right_alternatives = sit_left_right(attribute_value_a, attribute_value_b).alternatives
    right_left_alternatives = sit_left_right(attribute_value_b, attribute_value_a).alternatives

    return Condition(left_right_alternatives + right_left_alternatives)


def main():
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
        # Madam Natsiou - purple
        is_same_person(
            AttributeValue('name', 'Madam Natsiou'),
            AttributeValue('color', 'purple')
        ),
        # Lady Winslow - far left
        is_same_person(
            AttributeValue('name', 'Lady Winslow'),
            AttributeValue('seat', 'leftmost')
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
        # unsure: Snuff Tin - Rum
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

    for solution_index, solution in enumerate(solutions, 1):
        print 'Solution {}:'.format(solution_index)
        print solution

if __name__ == '__main__':
    sys.exit(main())
