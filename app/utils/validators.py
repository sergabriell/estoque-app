import re


def only_numbers(value: str) -> str:
    return "".join(filter(str.isdigit, value))


def format_cpf_cnpj(value: str) -> str:
    numbers = only_numbers(value)

    if len(numbers) <= 11:
        numbers = numbers[:11]

        if len(numbers) > 9:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
        if len(numbers) > 6:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:]}"
        if len(numbers) > 3:
            return f"{numbers[:3]}.{numbers[3:]}"
        return numbers

    numbers = numbers[:14]

    if len(numbers) > 12:
        return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:]}"
    if len(numbers) > 8:
        return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:]}"
    if len(numbers) > 5:
        return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:]}"
    if len(numbers) > 2:
        return f"{numbers[:2]}.{numbers[2:]}"
    return numbers


def format_phone(value: str) -> str:
    numbers = only_numbers(value)[:11]

    if len(numbers) > 10:
        return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
    if len(numbers) > 6:
        return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
    if len(numbers) > 2:
        return f"({numbers[:2]}) {numbers[2:]}"
    return numbers


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def is_valid_cpf_cnpj(value: str) -> bool:
    numbers = only_numbers(value)
    return len(numbers) in [11, 14]


def is_valid_phone(value: str) -> bool:
    numbers = only_numbers(value)
    return len(numbers) in [10, 11]

def parse_money(value: str) -> float:
    value = value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    return float(value)


def format_money(value: str) -> str:
    numbers = only_numbers(value)

    if not numbers:
        return ""

    amount = int(numbers) / 100
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_int(value: str) -> int:
    value = value.strip()

    if not value:
        raise ValueError("Campo numérico vazio.")

    return int(value)


def is_positive_or_zero(value: float | int) -> bool:
    return value >= 0