import json
import sys
from io import StringIO, TextIOWrapper, BytesIO

from pylint.lint import Run
from pylint.reporters import JSONReporter
from qchecker.descriptions import Markup, Description
from qchecker.match import Match, TextRange


def _run_pylint(code: str) -> list[dict]:
    """
    Runs pylint on the given code and returns a list of dictionaries
    containing the resulting errors or warnings.
    """
    # Stdin swapping is faster than running a subprocess. Although this
    # likely can't be used with multithreading.
    pylint_output = StringIO()
    # This is why you don't diddle with other people's IO without asking.
    sys.stdin = TextIOWrapper(BytesIO(code.encode()))
    Run(
        [
            '--disable',
            'C0115,'  # missing-class-docstring
            'C0116,'  # missing-function-docstring
            'C0114,'  # missing-module-docstring
            'C0103,'  # invalid-name – This matches any single char variable
            'C0301,'  # line-too-long
            'C1803,'  # use-implicit-booleaness-not-comparison
            'C0121,'  # singleton-comparison – students don't know this
            '',
            '--from-stdin', '_pylint_runner'
        ],
        reporter=JSONReporter(pylint_output),
        do_exit=False,
    )
    sys.stdin = sys.__stdin__
    result = pylint_output.getvalue()
    return json.loads(result)


def get_pylint_matches(code: str) -> list[Match]:
    """Returns a list of matches detected by pylint"""
    return [
        Match(
            f"pylint-{pl_match['message-id']}",
            Description(Markup.plaintext, pl_match['message']),
            TextRange(
                pl_match['line'],
                pl_match['column'],
                pl_match['endLine'],
                pl_match['endColumn']
            ),
        ) for pl_match in _run_pylint(code)
    ]
