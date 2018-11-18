"""Different applications of pink noise, the intended application being
to make 'starter' melodic shapes"""

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
    for sample in range(1, 2**number_of_dice):
        for x in range(number_of_dice):
            if sample % (2**x) == 0:
                dice[x] = randint(1, size_of_die)
        array.append(sum(dice))
    # scale between 0 and array_max:
    array_min = min(array)
    for item in range(len(array)):
        array[item] = array[item] - array_min
    return array


def pink_noise_unity():
    dice = [random() / 6. for x in range(8)]
    for sample in range(1, 2**8):
        for x in range(8):
            if sample % (2**x) == 0:
                dice[x] = random()
    yield sum(dice)


def sspn(number_of_dice, size_of_die):  # self-similar pink noise
    """sspn(number_of_dice, size_of_die)
    "self-similar pink noise", or fractal noise. Returns an array,
    auto re-scaled so min=0"""
    array = []
    phrase = []
    pointers = []
    for x in range(number_of_dice):
        phrase.append(randint(1, size_of_die))
        pointers.append(0)
    for sample in range(2**number_of_dice):
        for x in range(number_of_dice):
            if sample % (2**x) == 0:
                pointers[x] = (pointers[x] + 1) % number_of_dice
        sum = 0
        for point in pointers:
            sum = sum + phrase[point]
        array.append(sum)
    # scaled between 0 and array_max:
    array_min = min(array)
    for item in range(len(array)):
        array[item] = array[item] - array_min
    return array


def sspn_linear(total_length, phrase_length, size_of_die):
    """sspn_linear(total_length, phrase_length, size_of_die)
    "self-similar pink noise", or fractal noise. This variation uses a 
    simple linear cycle instead of the power scaling of the normal 
    'sspn' function. Returns an array, auto re-scaled so min=0"""
    array = []
    phrase = []
    pointers = []
    for x in range(phrase_length):
        phrase.append(randint(1, size_of_die))
        pointers.append(0)
    for sample in range(total_length):
        for x in range(1, phrase_length + 1):
            if sample % x == 0:
                pointers[x - 1] = (pointers[x - 1] + 1) % phrase_length
        sum = 0
        for point in pointers:
            sum = sum + phrase[point]
        array.append(sum)
    # scaled between 0 and array_max:
    array_min = min(array)
    for item in range(len(array)):
        array[item] = array[item] - array_min
    return array


def sspn_linear_custom(total_length, input_phrase, layers=0):
    """sspn_linear_custom(total_length, input_phrase, layers=0)
    "self-similar pink noise", or fractal noise.  This variation uses a
    simple linear cycle instead of the power scaling of the normal 'sspn'
    function.  When 'layers' is supplied and is greater than 0, use that 
    number to determine the number of layers that contribute to the final 
    texture. Returns an array, auto re-scaled so min=0"""
    output_array = []
    pointers = []
    if layers <= 0:
        layers = len(input_phrase)
    for x in range(layers):
        pointers.append(0)
    for sample in range(total_length):
        for x in range(1, layers + 1):
            if sample % x == 0:
                pointers[x - 1] = (pointers[x - 1] + 1) % layers
        sum = 0
        for point in pointers:
            sum = sum + input_phrase[point]
        output_array.append(sum)
    # scaled between 0 and array_max:
    array_min = min(output_array)
    for item in range(len(output_array)):
        output_array[item] = output_array[item] - array_min
    return output_array
