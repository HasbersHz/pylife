import abc
from ctypes import c_int as cint
import base.util

POLL_INTERVAL = cint(1000)


class LifePoll:
    __interrupted: cint = cint()
    __calculating: cint = cint()
    __countdown: cint = cint()

    def __init__(self):
        super(LifePoll, self).__init__()
        self.__interrupted: cint = cint(0)
        self.__calculating: cint = cint(0)
        self.__countdown: cint = POLL_INTERVAL

    @abc.abstractmethod
    def check_events(self) -> cint:
        """This is what should be overridden; it should check events,
           and return 0 if all is okay or 1 if the existing calculation
           should be interrupted."""
        return cint(0)

    def is_interrupted(self) -> cint:
        """Was an interrupt requested?"""
        return self.__interrupted

    def set_interrupted(self) -> None:
        """Call this to stop the current calculation."""
        self.__interrupted: cint = cint(1)

    def reset_interrupted(self) -> None:
        """Before a calculation begins, call this to reset the interrupted flag."""
        self.__interrupted: cint = cint(0)

    def poll(self) -> cint:
        """This is the routine called by the life algorithms at various
           points.  It calls check_events() and stashes the result.

           This routine may happen to go in the inner loop where it
           could be called a million times a second or more.  Checking
           for events might be a moderately heavyweight operation that
           could take microseconds, significantly slowing down the
           calculation.  To solve this, we use a countdown variable
           and only actually check when the countdown gets low
           enough (and we put it inline).  We assume a derating of
           1000 is sufficient to alleviate the slowdown without
           significantly impacting event response time.  Even so, the
           poll positions should be carefully selected to be *not*
           millions of times a second."""
        self.__countdown -= cint(1)
        return self.__interrupted if self.__countdown > cint(0) else self.inner_poll()

    def inner_poll(self) -> cint:
        self.bail_if_calculating()
        self.__countdown = POLL_INTERVAL
        self.__calculating += cint(1)
        if not self.__interrupted:
            self.__interrupted = self.check_events()
        self.__calculating -= cint(1)
        return self.__interrupted

    def bail_if_calculating(self) -> None:
        if self.is_calculating():
            util.life_fatal("Illegal operation while calculating.")

    def reset_countdown(self) -> None:
        """Sometimes we do a lengthy operation that we *don't* poll
           during.  After such operations, this function resets the
           poll countdown back to zero, so we get very quick response."""
        self.__countdown: cint = cint(0)

    def is_calculating(self) -> cint:
        """Some routines should not be called during a poll() such as ones
           that would modify the state of the algorithm process.  Some
           can be safely called but should be deferred.  This routine lets
           us know if we are called from the callback or not."""
        return self.__calculating

    @abc.abstractmethod
    def update_pop(self) -> None:
        """Sometimes get_population is called when hashlife is in a state
           where we just can't calculate it at that point in time.  So
           hashlife remembers that the population was requested, and
           when the GC is finished, calcs the pop and executes this
           callback to update the status window."""
        pass


default_poller = LifePoll()
