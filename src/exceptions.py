# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

class MemeoffError(Exception):
    """Top-level Memeoff error."""


class MinorMemeoffError(MemeoffError):
    """A minor error to communicate back to the end user."""


class MajorMemeoffError(MemeoffError):
    """A major error from which the program cannot continue."""
