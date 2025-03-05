import re


class PhoneNumberValidator:
    def __init__(self, re_exp):
        self.re_exp = re_exp

    def __call__(self, phone):
        phone_valid = re.match(self.re_exp, phone)
        return phone_valid is not None
