"""The app's own errors. No HTTP in them: app/errors.py maps each class to a response (interfaces 4.9)."""


class AutobuilderError(Exception):
    """Base of every error the app expects and can explain."""


class PobNotInstalled(AutobuilderError):
    """Path of Building is not in the folder the settings name."""


class PobError(AutobuilderError):
    """A failure inside PoB or our Lua code: `message` is for the user, `traceback` for the log."""

    def __init__(self, message: str, traceback: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.traceback = traceback


class UnknownEndpoint(PobError):
    """Python asked for a Lua endpoint that no Lua file registered."""


class BuildLoadFailed(PobError):
    """PoB could not open the build; `message` is PoB's own error text."""


class NoBuildLoaded(PobError):
    """A read before any build was loaded, or after a load that failed."""
