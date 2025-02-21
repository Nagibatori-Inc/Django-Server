

def make_phone_uniform(phone: str) -> str:
    if phone.startswith("+7"):
        return "8" + phone[2:]
    elif phone.startswith("7"):
        return "8" + phone[1:]
    elif phone.startswith("+8"):
        return phone[1:]
    return phone
