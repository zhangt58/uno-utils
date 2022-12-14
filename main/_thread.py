#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from typing import Callable


def execute_task(fn: Callable):
    """Execute the task on a new thread.
    """
    t = threading.Thread(target=fn)
    t.daemon = True
    t.start()


class BaseThreadWorker(threading.Thread):
    def __init__(self, name=None):
        super().__init__()
        self.daemon = True
        self.paused = True
        self.stopped = False
        self.state = threading.Condition()
        #
        self.pre_run()
        self.name = name

    def pre_run(self):
        """Initialization before run.
        """
        raise NotImplementedError

    def is_started(self):
        return self._started.is_set()

    def is_stopped(self):
        return self._is_stopped

    def is_daemon(self):
        return self._daemonic

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, s):
        self.set_name(s)

    def set_name(self, s):
        if s is None:
            self._name = threading._newname()
        else:
            self._name = s

    def status(self):
        if not self.is_stopped():
            if self.paused:
                status = "Paused"
            else:
                status = "Running"
        else:
            status = "Stopped"
        return status

    def run(self):
        raise NotImplementedError

    def stop(self):
        with self.state:
            self.stopped = True
        self._wait_for_tstate_lock()
        self._stop()

    def pause(self):
        with self.state:
            self.paused = True

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()

    def __repr__(self):
        status = self.status()
        if self.is_daemon():
            status += " (daemon)"
        return f"[{self.__class__.__name__}]({self.name}@{self.ident}): {status}"
