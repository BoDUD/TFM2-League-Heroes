"""Load / dump a hand-written kit or text file exactly as the repo stores it (CRLF, indent 2, UTF-8, the trailing
newline and BOM as they were). `python -I jsonio.py <file>...` checks that an unchanged load / dump gives the same bytes."""
import json
import sys
from collections import OrderedDict


def load(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    return json.loads(text, object_pairs_hook=OrderedDict), {"bom": bom, "crlf": "\r\n" in text,
                                                              "tail": text[len(text.rstrip("\r\n")):], "raw": raw}


def dumps(data, meta):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if meta["crlf"]:
        text = text.replace("\n", "\r\n")
    text += meta["tail"]
    return (b"\xef\xbb\xbf" if meta["bom"] else b"") + text.encode("utf-8")


def save(path, data, meta):
    open(path, "wb").write(dumps(data, meta))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        d, m = load(p)
        print(p, "same bytes" if dumps(d, m) == m["raw"] else "DIFFERENT")
