import re


class Bsr:
    def __init__(self):
        pass

    @staticmethod
    def interpret(bsrstring):
        raw_bsrlist = bsrstring.split(",")
        pattern = r"(!bsr)? *([A-Fa-f0-9]+)"
        bsrlist = []
        for bsr in raw_bsrlist:
            match = re.match(pattern, bsr)
            if match:
                bsrlist.append(match.group(2))
        return bsrlist
