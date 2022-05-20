try:
    from .flake8_checks import get_flake8_matches
    from .pylint_checks import get_pylint_matches
except ImportError as e:
    raise ImportError(
        "It seems like qchecker was installed without the optional general "
        "checks requirements. Reinstall qcheker with the optional "
        "general_checks or all extras."
        "(e.g. pip install qchecker[general_checks])"
    ) from e
