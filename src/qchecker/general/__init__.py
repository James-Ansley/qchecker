"""
Allows for the programmatic execution of flake8 and pylint.

To use this module, qChecker must be installed with the general_checks extra.

e.g. :code:`pip install qchecker[general_checks]`
"""

try:
    from ._flake8_checks import get_flake8_matches
    from ._pylint_checks import get_pylint_matches
except ImportError as e:
    raise ImportError(
        "It seems like qchecker was installed without the optional general "
        "checks requirements. Reinstall qcheker with the optional "
        "general_checks or all extras."
        "(e.g. pip install qchecker[general_checks])"
    ) from e
