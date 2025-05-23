from subprocess import PIPE, Popen


def pdftotext(filename: str) -> str:
    """Convert a PDF file to a text equivalent.

    Args:
      filename: A string path, the filename to convert.
    Returns:
      A string, the text contents of the filename.
    """

    executable = ["pdftotext", "-layout", filename, "-"]
    pipe = Popen(executable, stdout=PIPE, stderr=PIPE)
    stdout, stderr = pipe.communicate()
    return stdout.decode("iso-8859-1")
    if (
        stderr
        and all(
            ignore not in stderr
            for ignore in (
                "Can't get Fields array",
                "a line has more than",
            )
        )
        not in stderr
    ):
        raise ValueError(stderr.decode("utf-8"))
    else:
        return stdout.decode("iso-8859-1")
