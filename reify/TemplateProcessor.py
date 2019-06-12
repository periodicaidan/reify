import re
from typing import *
from typing import Match


class TemplateProcessor:
    SLOT = r"{{([A-Za-z0-9,.: ]*)}}"

    def __init__(self, input_template: str, output_template: Optional[str], conserve_whitespace: bool):
        self.pattern = input_template
        self.target = output_template

        self.input_tokens = self._find_slots(self.pattern)

        self.pattern = re.sub(r"[\\\[(=/!|?\"\'.]", lambda m: f"\\{m.group(0)}", self.pattern)
        if not conserve_whitespace:
            self.pattern = re.sub(r"\n+", r"\s*", self.pattern)
            self.pattern = re.sub(r"\s{2,}", r"\s*", self.pattern)

        for t in self.input_tokens:
            self.pattern = re.sub("{{(%s)}}" % t, self._parse_input_slots(), self.pattern, count=1)

        if output_template is not None:
            self.output_tokens = self._find_slots(self.target)

            for t in self.output_tokens:
                self.target = re.sub("{{(%s)}}" % t, self._prepare_target_slots(), self.target)

    @classmethod
    def from_files(cls, input_file: str, output_file: str, conserve_whitespace: bool):
        with open(input_file, "r") as ih, open(output_file, "r") as oh:
            return cls(ih.read(), oh.read(), conserve_whitespace)

    @staticmethod
    def _find_slots(text: str) -> Iterator[str]:
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
    def _parse_input_slots() -> Callable[[Match], str]:
        def inner(m: Match) -> str:
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
    def _prepare_target_slots() -> Callable[[Match], str]:
        def inner(m: Match) -> str:
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

    def find(self, file: str) -> Iterator[Match]:
        with open(file, "r") as input_text:
            return re.finditer(self.pattern, input_text.read())

    def find_and_replace(self, input_file: str, in_place: bool) -> str:
        with open(input_file, "w+" if in_place else "r") as h:
            new_text = re.sub(self.pattern, self.target, h.read())
            if in_place:
                h.write(new_text)
            return new_text
