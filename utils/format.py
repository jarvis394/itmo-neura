from random import randint
from re import findall


def censor_sentence(result: str) -> str:
    blacklisted_tokens = [
        "сова никогда не спит",
        "#cинийкит",
        "#рaзбудименяв420",
        "all",
        "everyone",
    ]
    links = list(set(findall(r"[^ (){\}\[\]\'\";]+\.[^ (){\}\[\]\'\";]+", result)))

    for link in links:
        result = result.replace(link, "[ссылка удалена]")

    for token in blacklisted_tokens:
        result = result.replace(token, "*" * len(token))

    return result


def improve_sentence(result: str) -> str:
    rnd = randint(0, 10)
    if rnd == 0:
        return result.upper()
    elif rnd in range(1, 6):
        return result
    else:
        improved_result = ""

        for i in range(len(result)):
            if i == 0:
                improved_result += result[i].upper()
            elif i > 1:
                if result[i - 1] == " " and result[i - 2] in ["?", ".", "!"]:
                    improved_result += result[i].upper()
                else:
                    improved_result += result[i]
            else:
                improved_result += result[i]

        return improved_result


def escape_string(string: str) -> str:
    return string.replace(";", "\;")


def unescape_string(string: str) -> str:
    return string.replace("\;", ";")
