# Thread manager for long-running threads (MD etc.)
#
# Written by Konrad Hinsen
# last revision: 2000-2-29
#

_undocumented = 1

_threads = []

def registerThread(thread):
    _threads.append(thread)
    _cleanup()

def activeThreads():
    _cleanup()
    return _threads

def waitForThreads():
    while _threads:
        _threads[0].join()
        _cleanup()

def _cleanup():
    i = 0
    while i < len(_threads):
        if _threads[i].isAlive():
            i = i + 1
        else:
            del _threads[i]
