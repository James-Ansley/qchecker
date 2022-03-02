import json

from qchecker.match import Match, TextRange

from ._process import _run_subprocess


def _run_pylint(code: str) -> list[dict]:
    """
    Runs pylint on the given code and returns a list of dictionaries
    containing the resulting errors or warnings.
    """
    stdout = _run_subprocess(
        ['pylint', '-f', 'json', '--from-stdin', '_pylint_code'],
        code,
    )
    return json.loads(stdout)


def get_pylint_matches(code: str) -> list[Match]:
    """Returns a list of matches detected by pylint"""
    return [
        Match(
            pl_match['message-id'],
            pl_match['message'],
            TextRange(
                pl_match['line'],
                pl_match['column'],
                pl_match['endLine'],
                pl_match['endColumn']
            ),
        ) for pl_match in _run_pylint(code)
    ]
