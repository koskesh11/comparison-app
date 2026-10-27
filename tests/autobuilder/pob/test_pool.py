"""The session pool (ported from the unit half of tests/test_engine_pool.py): a lease returns the same session, a lease
that raises closes its session and a new one takes its place, and a closed pool refuses. Fakes, no PoB."""

import threading

import pytest

from autobuilder.pob.pool import SessionPool


class FakeSession:
    def __init__(self, slot: int) -> None:
        self.slot = slot
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Factory:
    def __init__(self, fail_on: tuple[int, ...] = ()) -> None:
        self.made: list[FakeSession] = []
        self.calls = 0
        self.fail_on = fail_on

    def __call__(self, slot: int) -> FakeSession:
        self.calls += 1
        if self.calls in self.fail_on:
            raise LookupError(f"factory failed {self.calls}")
        session = FakeSession(slot)
        self.made.append(session)
        return session


def test_a_lease_returns_the_same_session_after_success() -> None:
    factory = Factory()
    pool = SessionPool(1, factory)
    with pool.lease() as first:
        assert first.slot == 0
    with pool.lease() as second:
        assert second is first
    assert factory.made == [first]
    pool.close()


def test_a_body_that_raises_closes_and_replaces_its_session() -> None:
    pool = SessionPool(1, Factory())
    with pytest.raises(RuntimeError, match="body failed"), pool.lease() as old:
        raise RuntimeError("body failed")
    assert old.closed
    with pool.lease() as replacement:
        assert replacement is not old and not replacement.closed
    pool.close()


def test_a_failed_replacement_leaves_a_slot_the_next_lease_retries() -> None:
    factory = Factory(fail_on=(2, 3))
    pool = SessionPool(1, factory)
    with pytest.raises(RuntimeError, match="original"), pool.lease():
        raise RuntimeError("original")
    with pytest.raises(LookupError, match="factory failed 3"), pool.lease():
        pass
    with pool.lease() as recovered:
        assert not recovered.closed
    assert factory.calls == 4
    pool.close()


def test_closing_with_a_leased_session_closes_it_on_return() -> None:
    pool = SessionPool(1, FakeSession)
    with pool.lease() as session:
        pool.close()
        assert not session.closed
    assert session.closed
    pool.close()
    with pytest.raises(RuntimeError, match="the session pool is closed"), pool.lease():
        pass


def test_a_failure_after_close_makes_no_replacement() -> None:
    factory = Factory()
    pool = SessionPool(1, factory)
    with pytest.raises(RuntimeError, match="body failed"), pool.lease():
        pool.close()
        raise RuntimeError("body failed")
    assert len(factory.made) == 1 and factory.made[0].closed


def test_a_failing_first_start_closes_what_was_made() -> None:
    factory = Factory(fail_on=(2,))
    with pytest.raises(LookupError, match="factory failed 2"):
        SessionPool(2, factory)
    assert [session.closed for session in factory.made] == [True]
    with pytest.raises(ValueError, match="positive"):
        SessionPool(0, FakeSession)


def test_four_threads_share_two_sessions() -> None:
    pool = SessionPool(2, FakeSession)
    barrier, lock = threading.Barrier(4), threading.Lock()
    state = {"active": 0, "peak": 0}
    completed: list[int] = []

    def worker(index: int) -> None:
        barrier.wait()
        with pool.lease():
            with lock:
                state["active"] += 1
                state["peak"] = max(state["peak"], state["active"])
            threading.Event().wait(0.05)
            with lock:
                state["active"] -= 1
                completed.append(index)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert sorted(completed) == [0, 1, 2, 3] and state["peak"] == 2
    pool.close()
