import re


class TemplateProcessor:
    SLOT = r"{{([A-Za-z0-9,.: ]*)}}"

    def __init__(self, pattern_file, target_file, conserve_whitespace):
        with open(pattern_file, "r") as pf:
            self.pattern = pf.read()
            self.input_tokens = self._find_slots(self.pattern)

        self.pattern = re.sub(r"[\\\[(=/!|?\"\'.]", lambda m: f"\\{m.group(0)}", self.pattern)
        if not conserve_whitespace:
            self.pattern = re.sub(r"\n+", r"\s*", self.pattern)
            self.pattern = re.sub(r"\s{2,}", r"\s*", self.pattern)

        for t in self.input_tokens:
            self.pattern = re.sub("{{(%s)}}" % t, self._parse_input_slots(), self.pattern, count=1)

        # self.pattern = re.sub(self.SLOT, self._parse_input_slots(), self.pattern)
        # self.pattern = re.compile(self.pattern)

        if target_file is not None:
            with open(target_file, "r") as tf:
                self.target = tf.read()
                self.output_tokens = self._find_slots(self.target)

            for t in self.output_tokens:
                self.target = re.sub("{{(%s)}}" % t, self._prepare_target_slots(), self.target)

    @staticmethod
    def _find_slots(text):
        for i, c in enumerate(text):
            if i == 0:
                prev_char = c
                continue

            if c == "{" and prev_char == "{":
                token = ""
                i = i + 1
                c = text[i]
                while c != "}" or text[i + 1] != "}":
                    token += c
                    i = i + 1
                    c = text[i]

                yield token

            prev_char = c

    @staticmethod
    def _parse_input_slots():
        def inner(m):
            token = m.group(1)
            if token == ":":
                return r"(?:.*)"
            elif re.match(r":.+", token):
                subm = re.match(r":(.+)", token)
                return f"\\{subm.group(1)}*"
            elif re.match(r"[A-Za-z0-9\-_]+", token):
                if re.match(r"^\d|-", token):
                    return f"(?P<_{token}>.*)"
                return f"(?P<{token}>.*)"
            else:
                return r"(.*)"

        return inner

    @staticmethod
    def _prepare_target_slots():
        def inner(m):
            token = m.group(1)
            if re.match(r"^(?:\d+ )+\d$", token):
                pat = ""
                for i in token.split(" "):
                    pat += f"\\{i}"
                return pat
            elif re.match(r"\d+\.\.\d+", token):
                limits = token.split("..")
                pat = ""
                for i in range(int(limits[0]), int(limits[1]) + 1):
                    pat += f"\\{i}"
                return pat
            elif re.match(r"^\d+$", token):
                return f"\\{token}"
            elif re.match(r"(?:[\w\d\-_]+ )+[\w\d\-_]+", token):
                pat = ""
                for s in token.split(" "):
                    pat += f"\\g<{s}>"
                return pat
            elif re.match(r"[\w\d\-_]+", token):
                return f"\\g<{token}>"

        return inner

    def find(self, file):
        with open(file, "r") as input_text:
            return re.finditer(self.pattern, input_text.read())

    def find_and_replace(self, input_file, in_place):
        with open(input_file, "w+" if in_place else "r") as h:
            new_text = re.sub(self.pattern, self.target, h.read())
            if in_place:
                h.write(new_text)
            return new_text
