#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unohelper
from com.sun.star.sheet import (
    XVolatileResult,
    ResultEvent,
    XResultListener
)
import aioca
import asyncio
import re
import sys
from functools import partial
from datetime import datetime
from uno_utils import BaseThreadWorker

SUB_STS_MAP = {0: 'OPENING', 1: 'OPEN', 2: 'CLOSED'}

SUB_DICT = {} # pvname: Subscription
MDEL_DICT = {} # pvname: mdel
RESULT_POOL = {} # pvname: PVResult
class PVDataThread(BaseThreadWorker):

    # add_pv: subscribe a pv
    # del_pv: remove a subscribed pv
    # show_all_pv: show all subscribed pv state

    def pre_run(self):
        self.t = None
        self.daemon = True
        # self.fp = open("/tmp/pvdatathread.log", "a")
        self.fp = sys.stdout
        printlog(f"Get thread ({self.name}) ready", file=self.fp)
        self.loop = asyncio.new_event_loop()
        self.lock = asyncio.Lock()
        self.sem = asyncio.Semaphore(1)
        asyncio.set_event_loop(self.loop)

    def set_mdel(self, pvname: str, mdel: float):
        """Set MDEL for the valid monitor signal.
        """
        MDEL_DICT[pvname] = mdel

    def add_pv(self, pvname: str, mdel: float = 0.0):
        """Subscribe *pvname*
        """
        if not is_valid_pv(pvname):
            printlog(f"Not to add an invalid PV: {pvname}", file=self.fp)
            return
        if pvname in SUB_DICT:
            printlog(f"Already added {pvname}", file=self.fp)
            self.set_mdel(pvname, mdel)
            return
        printlog(f"Add {pvname}", file=self.fp)
        future = asyncio.run_coroutine_threadsafe(self.camonitor_coro(pvname), self.loop)
        SUB_DICT[pvname] = future.result()
        self.set_mdel(pvname, mdel)
        RESULT_POOL[pvname] = PVResult(pvname)

    def del_pv(self, pvname: str):
        # close subscription, delete from dict.
        if pvname not in SUB_DICT:
            printlog(f"{pvname} is not found.", file=self.fp)
            return
        printlog(f"Remove {pvname}", file=self.fp)
        _sub = SUB_DICT.pop(pvname)
        _sub.close()
        RESULT_POOL.pop(pvname)

    def get_result(self, pvname: str):
        return RESULT_POOL.get(pvname)

    def show_all_pvs(self):
        for i, o in SUB_DICT.items():
            print(f"{i} is {SUB_STS_MAP[o.state]}")

    async def _main(self):
        async with self.sem:
            asyncio.ensure_future(self._main(), loop=self.loop)
            await asyncio.sleep(10) # serves as a live beat
            printlog("Asyncio loop is running ...", file=self.fp)

    def run(self):
        self.t = asyncio.ensure_future(self._main(), loop=self.loop)
        self.loop.run_forever()

    def __stop_close_loop(self):
        async def _stop_loop():
            if self.t:
                self.t.cancel()
            self.loop.stop()
            self.loop.close()
        asyncio.run_coroutine_threadsafe(_stop_loop(), self.loop)

    def stop(self):
        printlog("Stop and close loop.", file=self.fp)
        self.__stop_close_loop()
        #
        BaseThreadWorker.stop(self)
        printlog(f"Thread ({self.name}) is stopped? {self.stopped}", file=self.fp)

    async def mcb(self, pvname: str, value):
        # printlog(f"{pvname} has a new value {value}", file=self.fp)
        async with self.lock:
            mdel = MDEL_DICT[pvname]
            RESULT_POOL[pvname].updateValue(value, mdel)

    async def camonitor_coro(self, pvname: str):
        return aioca.camonitor(pvname, partial(self.mcb, pvname))


class PVResult(unohelper.Base, XVolatileResult):
    def __init__(self, pvname: str):
        self.pvname = pvname
        self.pvvalue = "#N/A"
        self.listeners = []

    def __str__(self):
        return f"{self.pvname} ({self.pvvalue}) with {len(self.listeners)} listeners"

    def getResult(self): # -> com.sun.star.sheet.ResultEvent
        _event = ResultEvent()
        _event.Value = self.pvvalue
        _event.Source = self
        return _event

    def addResultListener(self, listener: XResultListener):
        self.listeners.append(listener)
        listener.modified(self.getResult())

    def removeResultListener(self, listener: XResultListener):
        self.listeners.remove(listener)

    def updateValue(self, value, mdel: float):
        def _test_emit(x0, x1, mdel):
            try:
                v0 = float(x0)
                v1 = float(x1)
            except:
                _emit = True
            else:
                _emit = abs(x0 - x1) > mdel
            finally:
                return _emit

        if not _test_emit(self.pvvalue, value, mdel):
            return False

        self.pvvalue = value
        event = self.getResult()
        for ilistener in self.listeners:
            ilistener.modified(event)

        return True


def printlog(s: str, file):
    ts = datetime.now().isoformat()[:-3]
    print(f"[{ts}] {s}", file=file, flush=True)


_PATTERN = re.compile(r"^[a-zA-Z0-9\{\}\.\:\-\_]{1,40}$")
def is_valid_pv(pvname: str):
    """Test if *pvname* is a valid PV name.
    """
    if _PATTERN.match(pvname):
        return True
    else:
        return False


def main():
    import time

    # 2 PVs
    pvlist = ["PHY:DATETIME_NOW", "FE_ISRC2:BEAM:A_BOOK", "x", "PHY:DATETIME_NOW", ""]

    th = PVDataThread()
    th.start()

    for i in pvlist:
        th.add_pv(i)

    time.sleep(5)
    for i in pvlist:
        th.del_pv(i)

    # time.sleep(5)
    # th.add_pv(pv1)

    time.sleep(5)
    th.stop()


if __name__ == "__main__":
    main()

