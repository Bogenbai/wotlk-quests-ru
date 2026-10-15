import re

_COLUMN = re.compile(r"^\s+`([^`]+)`", re.M)
_ESCAPES = {"0": "\0", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a", "b": "\b"}


def _columns(sql):
    create = sql[sql.index("CREATE TABLE"):]
    create = create[:create.index("\n)")]
    return _COLUMN.findall(create)


def _rows(sql):
    i = 0
    n = len(sql)
    while True:
        i = sql.find("VALUES", i)
        if i < 0:
            return
        i += len("VALUES")
        while i < n:
            while sql[i] in " \r\n\t,":
                i += 1
            if sql[i] != "(":
                break
            i += 1
            row = []
            while True:
                c = sql[i]
                if c == "'":
                    i += 1
                    parts = []
                    while True:
                        c = sql[i]
                        if c == "\\":
                            parts.append(_ESCAPES.get(sql[i + 1], sql[i + 1]))
                            i += 2
                        elif c == "'":
                            if sql[i + 1] == "'":
                                parts.append("'")
                                i += 2
                            else:
                                i += 1
                                break
                        else:
                            parts.append(c)
                            i += 1
                    row.append("".join(parts))
                else:
                    j = i
                    while sql[j] not in ",)":
                        j += 1
                    token = sql[i:j].strip()
                    row.append(None if token == "NULL" else token)
                    i = j
                if sql[i] == ",":
                    i += 1
                elif sql[i] == ")":
                    i += 1
                    yield row
                    break


def load(path):
    sql = open(path, encoding="utf-8").read()
    columns = _columns(sql)
    return [dict(zip(columns, row)) for row in _rows(sql)]
