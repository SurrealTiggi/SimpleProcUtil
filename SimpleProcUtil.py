#!/usr/bin/env python

"""
Author: Tiago Baptista
Purpose: An alternate implementation of top to show info regarding processes running on a Linux system
Timer: 3:35
"""

# Imports
#####################
import sys
import os
import subprocess
import argparse
import time
import re
import random
from datetime import datetime as dt
import threading

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue

from numpy import mean

try:
    import psutil
except ImportError as e:
    pass

from SimpleConfig import SimpleConfigBuilder
#from SimpleProcPrinter import SimplePrinter

# Global Objects
#####################
myProcDict = {}
myRuns = None
myQueryInterval = 5 # Defaul 5
myOutputInterval = 30 # Default 30

# Classes
#####################

class Worker(threading.Thread):
    """ Execute tasks from given queue """
    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print("%s || [ERROR] || %s") % (now(), e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming from queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def map(self, func, arg_list):
        for args in arg_list:
            self.add_task(func, args)

    def wait_completion(self):
        self.tasks.join()


class ProcDict(object):

    def __init__(self):
        super(ProcDict, self).__init__()
        self.__dict = {}

    @property
    def dict(self):
        return self.__dict


class SimpleProcUtil(object):
    """ Stores pid information in an easily queriable object """

    def __init__(self):
        super(SimpleProcUtil, self).__init__()
        #self.__allpids = psutil.pids()
        self.pid = None
        self.name = None
        self.owner = None
        self.cpu = None
        self.mem = None

    # Getters + Setters p/pid

    @property
    def pid(self):
        return self._pid

    @property
    def name(self):
        return self._name

    @property
    def owner(self):
        return self._owner

    @property
    def cpu(self):
        return self._cpu

    @property
    def mem(self):
        return self._mem
    
    @pid.setter
    def pid(self, value):
        self._pid = value

    @name.setter
    def name(self, value):
        self._name = value

    @owner.setter
    def owner(self, value):
        self._owner = value

    @cpu.setter
    def cpu(self, value):
        self._cpu = value

    @mem.setter
    def mem(self, value):
        self._mem = value


# Methods
######################

def now():
    """ Returns current timestamp """
    now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    return now

def argBuilder(args):
    """ Store global variables for argument handling """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-r", "--regex", type=str,
                        help="process name(s) to look for, eg. mysql",
                        default=None)
    group.add_argument("-p", "--pid", type=int,
                        help="process id to monitor, eg. 123",
                        default=None)

    parser.add_argument("-e", "--run", type=int,
                        help="exit after x runs, eg. 5",
                        default=10)
    # Optionals
    #parser.add_argument("-i", "--interval", type=int,
    #                    nargs="+", help="run intervals, eg. 5 30",
    #                    default=[5, 30])
    #parser.add_argument(
    #    "-d", "--daemon", action="store_true", help="run as daemon",
    #    default=False)
    #parser.add_argument("-o", "--ouput", type=str,
    #                    help="set where results are sent, eg syslog",
    #                    default='console')

    return parser.parse_args()

def run(argv=None):
    """ Main runner for running things """
    args = argv
    runs = int(args.run)
    pids = []

    if not len(sys.argv) > 1:
        # Default run with no flags specified, only reads 10 random processes
        print("%s || [INFO] || Running with defaults for %s run/s") % (now(), runs)
        pids = random.sample(psutil.pids(), 10)
    elif args.regex is None:
        pids.append(args.pid)
    else:
        pids = getRegexPids(args.regex)

    for _ in range(runs):
        print("=" * 50)
        print("%s || [INFO] || Gathering data: %s/%s") % (now(), _ + 1, runs)
        runtime = myOutputInterval/myQueryInterval

        # Create thread per pid 
        pool = ThreadPool(len(pids))
        
        for pid in pids: # replace with psutils.pids when done testing
            procutil = psutil.Process(pid)
            procinfo = SimpleProcUtil()
            procinfo.pid = pid
            procinfo.name = str(procutil.name())
            procinfo.owner = str(procutil.username())

            # Now spawn a thread to go and gather info (output/query) and output when done
            pool.add_task(getProcInfo, procinfo, runtime)
            
        pool.wait_completion()
        
        # Show summary
        for pid in pids:
            currentPid = myProcDict[pid]
            print("%s || [INFO] || Process details for PID [%s]: ") % (now(), currentPid.pid),
            print("Name: %s, ") % currentPid.name,
            print("Owner: %s, ") % currentPid.owner,
            print("Memory: %s KB, ") % currentPid.mem,
            print("CPU: %s %%") % currentPid.cpu

def getRegexPids(regex):
    nameList = []
    for proc in psutil.process_iter():
        try:
            if re.search(regex, proc.name()):
                nameList.append(proc.pid)
        except Exception as e:
            print("%s || [ERROR] || %s : Unable to find reguested process...") % (now(), e)
    return nameList

def getProcInfo(procinfo, runtime):
    """ Threader to handle simultanous queries for cpu/mem stats"""
    infopool = ThreadPool(2)
    infopool.add_task(calcAvg, procinfo, runtime, 1)
    infopool.add_task(calcAvg, procinfo, runtime, 2)
    infopool.wait_completion()

    myProcDict[procinfo.pid] = procinfo

def calcAvg(procinfo, runtime, case):
    """ Calculate averages given a single process """
    myList = []
    currentProc = psutil.Process(procinfo.pid)

    if case == 1:
        for _ in range(runtime):
            myList.append(currentProc.cpu_percent())
            time.sleep(myQueryInterval)
        result = round(mean(myList), 2)
        procinfo.cpu = str(result)

    elif case == 2:
        for _ in range(runtime):
            myList.append(round(currentProc.memory_info()[0]/1000, 2))
            time.sleep(myQueryInterval)
        result = int(mean(myList))
        procinfo.mem = str(result)

def psAux():
    """ Use if psutil is unavailable """
    cmd = "ps aux | awk '{print $2}' | sort | uniq | sort -nu"
    #process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #output = process.communicate()
    #return output

# Main
####################

def main(argv=None):
    print("%s || [INFO] || Starting...") % now()
    #config = SimpleConfigBuilder()
    config = None

    # Create pid for safety
    pid = str(os.getpid())
    pidfile = "/tmp/simpleprocutil.pid" # Check from config file

    if os.path.isfile(pidfile):
        print("%s || [ERROR] || Found an existing pid file: %s") % (now(), pidfile)
        sys.exit()
    file(pidfile, 'w').write(pid)

    try:
        if config is not None:
            run(config)
        elif not len(sys.argv) > 1:
            raise Exception("No arguments given")
        else:
            args = argBuilder(argv)
            run(args)
    except:
        args = argBuilder(argv)
        run(args)
    finally:
        os.unlink(pidfile)


if __name__ == '__main__':
    sys.exit(main())
