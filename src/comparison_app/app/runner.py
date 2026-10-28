"""Runs one comparison job: your build from the Builds folder, the target from a link, a code or a saved import, the
comparison on the app's PoB session, the report into the job (or its error, with the kind the page switches on).

Every log record of the job carries its id and build through app/logging_setup.job_context. An unexpected error is
logged with its traceback and the reference id the page shows (app/errors.py); nothing is swallowed.
"""

import logging
from pathlib import PurePosixPath

from comparison_app.app.errors import reply_for
from comparison_app.app.inputs import CompareRequest
from comparison_app.app.jobs import JobError, Stage
from comparison_app.app.logging_setup import job_context
from comparison_app.app.present.report import report
from comparison_app.app.state import AppState
from comparison_app.compare.service import compare
from comparison_app.errors import InvalidInput
from comparison_app.intake.library import Library
from comparison_app.intake.store import ImportedBuild, ImportStore, import_target

logger = logging.getLogger(__name__)


def _target(state: AppState, request: CompareRequest) -> ImportedBuild:
    store = ImportStore(state.settings.imports_dir)
    if request.target_import is not None:
        saved = store.saved(request.target_import)
        if saved is None:
            raise InvalidInput("That saved target is no longer there; paste its link or code again.")
        return saved
    return import_target(request.target or "", store)


def run_compare(state: AppState, job_id: str, request: CompareRequest) -> None:
    context = job_context.set((job_id, request.build))
    try:
        state.jobs.progress(job_id, Stage.LOADING)
        yours = Library(state.settings.builds_dir).read(request.build)
        target = _target(state, request)
        state.jobs.progress(job_id, Stage.READING)
        with state.lock:
            comparison = compare(
                state.session(),
                (yours, PurePosixPath(request.build).stem),
                (target.xml, target.import_id),
                request.scenario,
                stages=(request.your_stage, request.target_stage),
            )
        state.jobs.progress(job_id, Stage.COMPARING)
        state.jobs.finish(job_id, report(comparison))
        logger.info("comparison done", extra={"event": "job_done"})
    except Exception as error:
        reply = reply_for(error)
        if reply.reference_id is None:
            logger.info("comparison refused: %s", reply.message, extra={"event": "job_refused"})
        else:
            logger.exception("comparison failed, reference %s", reply.reference_id, extra={"event": "job_failed"})
        state.jobs.fail(job_id, JobError(reply.kind, reply.message, reply.reference_id))
    finally:
        job_context.reset(context)
