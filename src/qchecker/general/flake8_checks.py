import json

from qchecker.descriptions import Description, Markup
from qchecker.match import Match, TextRange

from ._process import _run_subprocess


def _run_flake8(code: str) -> list[dict]:
    """
    Runs flake8 on the given code and returns a list of dictionaries
    containing the resulting errors or warnings.
    """
    stdout = _run_subprocess(
        [
            'flake8',
            '--format', 'json',
            '--stdin-display-name', '_flake8_code',
            '-',
        ],
        code,
    )
    return json.loads(stdout)['_flake8_code']


def get_flake8_matches(code: str) -> list[Match]:
    """Returns a list of matches detected by flake8"""
    return [
        Match(
            f"flake8-{f8_match['code']}",
            Description(Markup.plaintext, f8_match['text']),
            TextRange(
                f8_match['line_number'],
                f8_match['column_number'],
                f8_match['line_number'],
                f8_match['column_number'],
            ),
        ) for f8_match in _run_flake8(code)
    ]
