"""Different applications of pink noise, the intended application being
to make 'starter' melodic shapes"""

from itertools import product
from random import randint


def pink_noise(number_of_dice, size_of_die):
    """pink_noise(number_of_dice,size_of_die)
    Return an array of pink noise base on the parameters, automatically
    re-scaled so that min=0
    """
    array = []
    dice = []
    for x in range(number_of_dice):
        dice.append(randint(1, size_of_die))
    array.append(sum(dice))
    for sample in range(1, 2 ** number_of_dice):
        for x in range(number_of_dice):
            if sample % (2 ** x) == 0:
                dice[x] = randint(1, size_of_die)
        array.append(sum(dice))
    # scale between 0 and array_max:
    array_min = min(array)
    for item in range(len(array)):
        array[item] = array[item] - array_min
    return array


def fractal_melody(input_phrase, layers, total_length, shift):
    """Return a list of numbers representing pitches in an abstract scale.

    Composed by adding a seed array to itself odometer style. A simple fractal!

    :param input_phrase: A `list` of integers that represents a seed melody.
    :param layers: An `int` representing how many repetitions
                   (places in the odometer) there will be.
    :param total_length: The total number of notes returned. Type: `int`.
    :param shift: An `int` for how much to displace the entire melody
                  up or down. Can be though of as a transposition.
    """
    # place to put output
    output_array = []
    # use the `product` object to get us our combinations:
    i = product(input_phrase, repeat=layers)
    # start producing:
    count = 0
    while count <= total_length:
        try:
            output_array.append(sum(next(i)))
        except StopIteration:
            i = product(input_phrase, repeat=layers)
            output_array.append(sum(next(i)))
        count += 1
    # We scale between 0 and array_max, but also shift (transpose)
    # The signed naturally should get reversed, so that a positive
    # shift becomes a subtraction here, and then the difference
    # re-accounts for the natural sign/direction.
    array_min = min(output_array) - shift
    output_array = [x - array_min for x in output_array]
    return output_array
