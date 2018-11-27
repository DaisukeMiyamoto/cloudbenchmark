# -*- coding: utf-8 -*-
import random
import string

def get_random_str(n):
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
    return random_str

