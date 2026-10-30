import re

from num2words import num2words

PLAYER_FORMS = {
    "m": {"n": "путник", "c": "искатель приключений", "r": "странник"},
    "f": {"n": "путница", "c": "искательница приключений", "r": "странница"},
}

DECLENSIONS = {
    "m": {
        "c": ["искатель приключений", "искателя приключений", "искателю приключений", "искателя приключений",
              "искателем приключений", "искателе приключений", "искатель приключений", "искатели приключений",
              "искателей приключений"],
        "r": ["странник", "странника", "страннику", "странника", "странником", "страннике", "странник",
              "странники", "странников"],
    },
    "f": {
        "c": ["искательница приключений", "искательницы приключений", "искательнице приключений",
              "искательницу приключений", "искательницей приключений", "искательнице приключений",
              "искательница приключений", "искательницы приключений", "искательниц приключений"],
        "r": ["странница", "странницы", "страннице", "странницу", "странницей", "страннице", "странница",
              "странницы", "странниц"],
    },
}

LATIN_PHRASES = {
    "World of Warcraft": "Ворлд оф Варкрафт",
    "Worldwide Invitational": "Ворлдвайд Инвитейшнл",
    "P.S.": "Постскриптум.",
}

HOMOGLYPHS = str.maketrans("aceopxykACEHKMOPTXYB", "асеорхукАСЕНКМОРТХУВ")

LETTER_NAMES = {
    "A": "а", "B": "бэ", "C": "цэ", "D": "дэ", "E": "е", "F": "эф", "G": "гэ", "H": "аш", "I": "и",
    "J": "жи", "K": "ка", "L": "эл", "M": "эм", "N": "эн", "O": "о", "P": "пэ", "Q": "ку", "R": "эр",
    "S": "эс", "T": "тэ", "U": "у", "V": "вэ", "W": "дубль-вэ", "X": "икс", "Y": "игрек", "Z": "зэт",
}

ROMAN = {"I": 1, "V": 5, "X": 10}

STRESS = {
    "Североземь": "Североз+емь",
    "Штормград": "Штормгр+ад",
    "бандан": "банд+ан",
    "Элвин": "Элв+ин",
    "Макбрайд": "Макбр+айд",
}


def is_gendered(text):
    return re.search(r"\$[gGnNcCrR]", text) is not None


def variants(text):
    return [("m-", "m"), ("f-", "f")] if is_gendered(text) else [("", "m")]


def decline(gender, token, case):
    forms = DECLENSIONS[gender][token.lower()]
    return forms[case] if case < len(forms) else forms[0]


def plural(number, forms):
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return forms[1]
    return forms[2]


def roman_value(token):
    values = [ROMAN[letter] for letter in token]
    total = sum(-v if i + 1 < len(values) and v < values[i + 1] else v for i, v in enumerate(values))
    return total if (len(token) > 1 or token in "IV") and to_roman(total) == token else None


def to_roman(number):
    result = ""
    for value, letters in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while number >= value:
            result += letters
            number -= value
    return result


def russify_word(match):
    word = match.group()
    if not re.search(r"[A-Za-z]", word):
        return word
    after_hyphen = match.start() > 0 and match.string[match.start() - 1] == "-"
    if len(word) == 1 and word in "AaCcOoKkYy" and not after_hyphen:
        return word.translate(HOMOGLYPHS)
    if re.search(r"[А-Яа-яЁё]", word) or re.search(r"[a-z]", word):
        word = word.translate(HOMOGLYPHS)
        return re.sub(r"[A-Za-z]", "", word) if re.search(r"[А-Яа-яЁё]", word) else word
    if re.fullmatch(r"[IVX]+", word) and roman_value(word):
        return str(roman_value(word))
    return "-".join(LETTER_NAMES[letter] for letter in word)


def russify_latin(text):
    for latin, russian in LATIN_PHRASES.items():
        text = text.replace(latin, russian)
    return re.sub(r"[A-Za-zА-Яа-яЁё]+", russify_word, text)


def render(text, gender):
    forms = PLAYER_FORMS[gender]
    text = re.sub(r"\|3-(\d+)\(\$([cCrR])\)", lambda m: decline(gender, m.group(2), int(m.group(1))), text)
    text = re.sub(r"\|3-\d+\(([^)]*)\)", r"\1", text)
    text = re.sub(r"(\d+)\s*\|4([^:;]*):([^:;]*):([^;]*);", lambda m: m.group(1) + " " + plural(int(m.group(1)), m.group(2, 3, 4)), text)
    text = re.sub(r"\|4([^:;]*):([^:;]*):([^;]*);", r"\3", text)
    text = re.sub(r"(?<![A-Za-z$])[gG]\$?(?=[А-Яа-яЁё][^:;$\s]*:)", "$G", text)
    text = re.sub(r"\$[gG]\s*([^:;]*):([^:;]*)(:[^;]*)?;", lambda m: m.group(1 if gender == "m" else 2), text)
    text = re.sub(r"\$[gG]\s*([^:;$]*);([^\s,.!?;:$]+);?", lambda m: m.group(1 if gender == "m" else 2), text)
    text = re.sub(r"\$[gG]\s*([^:;$\s]+):([^\s,.!?;:$]+)", lambda m: m.group(1 if gender == "m" else 2), text)
    text = re.sub(r"\$([nNcCrR])", lambda m: forms[m.group(1).lower()], text)
    text = re.sub(r"\$\d+[wW]", "немало", text)
    text = re.sub(r"\$\d+[kK]", "несколько минут", text)
    text = re.sub(r"\$[gG]\b", "", text)
    text = re.sub(r"(?<=[.!?])[bB](?=\$[bB])", "\n", text)
    text = re.sub(r"\$[bB]|/[bB](?![A-Za-z])", "\n", text)
    text = re.sub(r"(?<![A-Za-zА-Яа-яЁё])[bB](?=[А-ЯЁ])", "\n", text)
    text = re.sub(r"[$|]", "", text)
    text = re.sub(r"\[PH\]\s*", "", text).replace("(NAME)", "кто-то")
    text = re.sub(r"<([^>]*)>", r"\1", text)
    text = russify_latin(text)
    text = re.sub(r"(?:\b[01]{8}\b[^\S\n]*){2,}", "", text)
    text = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang="ru"), text)
    text = text.replace("–", ",").replace("—", ",").replace("…", "...")
    text = re.sub(r"(?<=\w)[\"«»„“”](?=\w)", " ", text)
    text = re.sub(r"[\"«»„“”]", "", text)
    text = re.sub(r"\s*,(\s*,)+", ",", text)
    return text


def add_stress(text):
    for plain, stressed in STRESS.items():
        text = text.replace(plain, stressed)
    return text


def strip_stress(text):
    return text.replace("+", "")


def paragraphs(text):
    return [p.strip() for p in text.split("\n") if re.search(r"[^\W\d_]", p)]


def sentences(paragraph):
    return [s for s in re.split(r"(?<=[.!?…])\s+", paragraph) if s]


def _split_long(sentence, limit):
    parts = re.split(r"(?<=[,;:])\s+", sentence)
    current = ""
    for part in parts:
        while len(part) > limit:
            cut = part.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                yield current
                current = ""
            yield part[:cut]
            part = part[cut:].strip()
        if current and len(current) + 1 + len(part) > limit:
            yield current
            current = part
        else:
            current = f"{current} {part}".strip()
    if current:
        yield current


def chunks(paragraph, limit):
    current = ""
    for sentence in sentences(paragraph):
        pieces = [sentence] if len(sentence) <= limit else list(_split_long(sentence, limit))
        for piece in pieces:
            if current and len(current) + 1 + len(piece) > limit:
                yield current
                current = piece
            else:
                current = f"{current} {piece}".strip()
    if current:
        yield current


def lines(quests):
    for quest in quests:
        for event, npc_field in (("accept", "starters"), ("complete", "enders")):
            text = quest[event]
            if not text:
                continue
            for prefix, gender in variants(text):
                yield f"{prefix}{quest['id']}-{event}", quest[npc_field], render(text, gender)
