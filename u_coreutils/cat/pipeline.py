LINE_NUMBER_WIDTH = 6


class LineFilter:
    def run(self, line: str, index: int = -1):
        raise NotImplementedError


class ShowEnds(LineFilter):
    def run(self, line: str, index: int = -1):
        return line.replace("\n", "$\n")


class ShowTabs(LineFilter):
    def run(self, line: str, index: int = -1):
        return line.replace("\t", "^I")


class ShowLineNumbers(LineFilter):
    def run(self, line: str, index: int = -1):
        return f"{index+1:{LINE_NUMBER_WIDTH}}  {line}"


class ShowNotBlankLineNumbers(LineFilter):
    lineIndex = 0

    def run(self, line: str, index: int = -1):
        if line != "\n":
            self.lineIndex += 1
            return f"{self.lineIndex:{LINE_NUMBER_WIDTH}}  {line}"
        else:
            return line


class SqueezeBlankLines(LineFilter):
    lastLine = ""

    def run(self, line: str, index: int = -1):

        if index == 0:
            self.lastLine = line

        if not self.lastLine and not line:
            return ""

        ret = self.lastLine
        self.lastLine = line
        return ret


COMBINE_OPTIONS = dict(showAllFlag=["showTabsFlag", "showEndFlag"])

PIPLINES = dict(
    showLineNumberFlag={1: ShowLineNumbers, 2: ShowNotBlankLineNumbers},
    showEndFlag={1: ShowEnds},
    showTabsFlag={1: ShowTabs},
    squeezeBlankFlag={1: SqueezeBlankLines},
)

PRIORITY = [
    ShowLineNumbers,
    ShowNotBlankLineNumbers,
    ShowTabs,
    SqueezeBlankLines,
    ShowEnds,
]


class Pipeline:
    def __init__(self, **kwargs):
        self.linePipeline = []

        for option in COMBINE_OPTIONS:
            if kwargs.get(option, None):
                kwargs.update({item: True for item in COMBINE_OPTIONS[option]})

        for k, v in kwargs.items():
            if v and issubclass(
                filterType := PIPLINES.get(k, {}).get(v, object), LineFilter
            ):
                self.linePipeline.append(filterType())

        self.linePipeline.sort(key=lambda x: PRIORITY.index(type(x)))

        def lineProcessor(line: str, index: int = -1):
            for filter in self.linePipeline:
                # click.secho(f"{filter=} {line=} {index=}", fg="green")
                line = filter.run(line, index)
            return line

        self.lineProcessor = lineProcessor

    def execute(self, line: str, index: int = -1):
        return self.lineProcessor(line, index)