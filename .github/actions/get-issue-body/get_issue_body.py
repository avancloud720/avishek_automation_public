import os, json, re, logging

FORMAT = "%(asctime)s:%(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=FORMAT, datefmt=DATE_FORMAT, level=logging.INFO)

LOGGER = logging.getLogger(__name__)

issue_id = os.getenv("INPUT_ISSUE_ID")
issue_body = os.getenv("INPUT_ISSUE_BODY")
separator = os.getenv("INPUT_SEPARATOR", "###")
label_marker_start = os.getenv("INPUT_LABEL_MARKER_START", "---")
label_marker_end = os.getenv("INPUT_LABEL_MARKER_END", "---")

NO_RESPONSE = "_No response_"


class Parser:
    def __init__(self) -> None:
        self._config = {
            "separator": separator,
            "tag": {"open": label_marker_start, "close": label_marker_end},
        }

    @property
    def separator(self):
        return self._config["separator"]

    def tag_regex(self):
        open = self._config["tag"]["open"]
        close = self._config["tag"]["close"]
        regex_match = f"{open}(.*){close}(?:\s)+(.*)"
        return re.compile(regex_match)

    def bullet_regex(self):
        open = self._config["tag"]["open"]
        close = self._config["tag"]["close"]
        regex_match = f"\* (.*) - (.*)"
        return re.compile(regex_match)

    def check_box_regex(self):
        open = self._config["tag"]["open"]
        close = self._config["tag"]["close"]
        regex_match = f"\\- \\[(\w|\s)\\]  {open}(.*){close}"
        return re.compile(regex_match)

    def parse(self, content):
        content = content.replace("\r", "")
        if content == "" or len(content.strip()) == 0:
            return None

        parts = content.split(self.separator)
        result = {}

        if parts:
            tag_regex = self.tag_regex()
            check_box_regex = self.check_box_regex()
            bullet_regex = self.bullet_regex()

            for part in parts:
                bullet_match = bullet_regex.findall(part)
                tag_match = tag_regex.findall(part)
                if tag_match:
                    if tag_match[0][1].strip() == NO_RESPONSE:
                        result.update({tag_match[1]: None})
                    else:
                        result.update({tag_match[0][0]: tag_match[0][1]})
                elif bullet_match:
                    for k, v in bullet_match:
                        result.update({k.replace(" ", "_").lower(): v})
                else:
                    check_box_match = check_box_regex.findall(part)
                    if check_box_match:
                        result.update({check_box_match[0][1]: check_box_match == "X"})

        return result


def run():
    try:
        LOGGER.info("Starting to parse the data.")
        parser = Parser()
        parsed = parser.parse(issue_body)
        LOGGER.info("Data was parsed successfully.")

        if parsed != None:
            with open(os.environ["GITHUB_OUTPUT"], "a") as gh_output:
                LOGGER.info(f"Payload = {parsed}.")
                print(f"payload={json.dumps(parsed)}", file=gh_output)
            with open(os.environ["GITHUB_OUTPUT"], "r") as gh_output:
                print(gh_output.read())
        else:
            LOGGER.error("Data couldn't be parsed.")
    except Exception as err:
        LOGGER.exception(f"There was an exception in the code.")
        raise SystemExit(err)


if __name__ == "__main__":
    run()
