def sum(number_one, number_two):
    number_one_init = convert_integer(number_one)
    number_two_init = convert_integer(number_two)

    result = number_one_init + number_two_init
    return result

def convert_integer(number):
    converted_integer = int(number)
    return converted_integer

answer = sum("34", "12")