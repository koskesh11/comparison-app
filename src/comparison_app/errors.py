"""The app's own errors. No HTTP in them: app/errors.py maps each class to a response (interfaces 4.9)."""


class AutobuilderError(Exception):
    """Base of every error the app expects and can explain."""


class InvalidInput(AutobuilderError):
    """Something the owner typed or picked cannot be used; `str(error)` says what, for the page."""


class BadLink(InvalidInput):
    """Not a pobb.in build link."""


class Unreadable(InvalidInput):
    """The pasted code or the file is not a Path of Building build."""


class TooLarge(InvalidInput):
    """The code or the build inside it is over the size limit."""


class FetchFailed(AutobuilderError):
    """pobb.in was unreachable, too slow, or answered with an error."""


class SetupProblem(AutobuilderError):
    """The app's folders are not set up (a missing Builds folder, a relative path); `str(error)` says what to fix."""


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


class TargetLoadFailed(PobError):
    """PoB could not open the target build."""


class NoTargetLoaded(PobError):
    """A read of the target before one was loaded, after a load that failed, or after it was released."""


class MixedStages(InvalidInput):
    """A build saved with its tree, items, skills and config from different stages (decision 026): fix it in PoB, or
    pick a stage; `str(error)` names the parts."""


class NoMainSkill(PobError):
    """The build's sidebar has no main skill, so there is no damage chain to read."""


class BuildNotRestored(PobError):
    """PoB could not undo a temporary change; no build counts as loaded until it is loaded again."""
