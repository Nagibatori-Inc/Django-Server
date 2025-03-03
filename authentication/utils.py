

def make_phone_uniform(phone: str) -> str:
    if phone.startswith("+7"):
        return phone[1:]
    elif phone.startswith("+8"):
        return f"7{phone[2:]}"
    elif phone.startswith("8"):
        return f"7{phone[1:]}"
    return phone
