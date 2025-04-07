from authentication.exceptions import InvalidPhoneError


# TODO сделать так, чтобы телефон приводился к ЗАДАННОМУ стандарту, а не захардкоженному
def make_phone_uniform(phone: str) -> str:
    """ Унификатор телефонного номера, приводит его к формату 71234567890"""
    if phone.startswith("+7"):
        return phone[1:]
    elif phone.startswith("+8"):
        return f"7{phone[2:]}"
    elif phone.startswith("8"):
        return f"7{phone[1:]}"
    elif phone.startswith("7"):
        return phone
    else:
        raise InvalidPhoneError("Phone starts with invalid code")

