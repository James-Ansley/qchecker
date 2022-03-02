import subprocess


def _run_subprocess(args: list[str], stdin: str) -> bytes:
    """
    Runs a subprocess with the given args. stdin is then communicated to
    the subprocess and the resulting stdout is returned. stderr is ignored.
    """
    with subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
    ) as process:
        stdout, _ = process.communicate(stdin.encode(), timeout=3)
    return stdout
