# -*- coding: utf-8 -*-


conv_dict = {
    'A': ('\xc3\x80', '\xc3\x81', '\xc3\x82', '\xc3\x83', '\xc3\x84', '\xc3\x85'),
    'E': ('\xc3\x88', '\xc3\x89', '\xc3\x8a', '\xc3\x8b', '\xe2\x82\xac\xc3'),
    'I': ('\xc3\x8c', '\xc3\x8d', '\xc3\x8e', '\xc3\x8f'),
    'O': ('\xc3\x92', '\xc3\x93', '\xc3\x94', '\xc3\x95', '\xc3\x96'),
    'U': ('\xc3\x99', '\xc3\x9a', '\xc3\x9b', '\xc3\x9c'),
    'a': ('\xc3\xa0', '\xc3\xa1', '\xc3\xa2', '\xc3\xa3', '\xc3\xa4', '\xc3\xa5'),
    'c': ('\xc3\x87', '\xc3\xa7'),
    'e': ('\xc3\xa8', '\xc3\xa9', '\xc3\xaa', '\xc3\xab'),
    'i': ('\xc3\xac', '\xc3\xad', '\xc3\xae', '\xc3\xaf'),
    'o': ('\xc3\xb2', '\xc3\xb3', '\xc3\xb4', '\xc3\xb5', '\xc3\xb6', '\xc2\xb0'),
    'u': ('\xc3\xb9', '\xc3\xba', '\xc3\xbb', '\xc3\xbc'),
    'y': ('\xc3\xbf',),
}

def purify(my_str):
    """
    Retourne la chaine épurée, pratique pour faire des comparaisons.
    """
    for i in range(len(my_str)):
        for k, v in conv_dict.items():
            if my_str[i].encode("utf-8") in v:
                my_str = my_str.replace(my_str[i], k)
    # LC: Just in case, force encode
    return my_str.encode('utf-8')