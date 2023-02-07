from hlifepoll import *
from util import life_fatal


class LifePoll(HLifePoll):
    def __init__(self):
        super(LifePoll, self).__init__()
        self.__interrupted: cint = cint(0)
        self.__calculating: cint = cint(0)
        self.__countdown: cint = POLL_INTERVAL

    def check_events(self) -> cint:
        return cint(0)

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
            life_fatal("Illegal operation while calculating.")

    def update_pop(self) -> None:
        pass


default_poller = LifePoll()
