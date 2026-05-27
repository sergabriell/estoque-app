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


def _cpf_digit(numbers: str, length: int) -> int:
    weights = range(length + 1, 1, -1)
    total   = sum(int(d) * w for d, w in zip(numbers, weights))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def _cnpj_digit(numbers: str, length: int) -> int:
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    offset  = len(weights) - length
    total   = sum(int(d) * weights[offset + i] for i, d in enumerate(numbers[:length]))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(numbers: str) -> bool:
    if len(numbers) != 11 or len(set(numbers)) == 1:
        return False
    return (
        int(numbers[9])  == _cpf_digit(numbers, 9) and
        int(numbers[10]) == _cpf_digit(numbers, 10)
    )


def is_valid_cnpj(numbers: str) -> bool:
    if len(numbers) != 14 or len(set(numbers)) == 1:
        return False
    return (
        int(numbers[12]) == _cnpj_digit(numbers, 12) and
        int(numbers[13]) == _cnpj_digit(numbers, 13)
    )


def is_valid_cpf_cnpj(value: str) -> bool:
    numbers = only_numbers(value)
    if len(numbers) == 11:
        return is_valid_cpf(numbers)
    if len(numbers) == 14:
        return is_valid_cnpj(numbers)
    return False


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