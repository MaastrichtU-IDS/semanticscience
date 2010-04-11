#
# Master-slave process manager for distributed computing
# based on Pyro
#
# Written by Konrad Hinsen <hinsen@cnrs-orleans.fr>
# last revision: 2007-8-28
#

"""
Distributed computing using a master-slave model

The classes in this module provide a simple way to parallelize independent
computations in a program. The communication is handled by the Pyro package,
which must be installed before this module can be used.
Pyro can be obtained from http://pyro.sourceforge.net/.
By default, the Pyro name server is used to initialize communication. Please
read the Pyro documentation for learning how to use the name server.

The principle of the master-slave model is that there is a single master
process that defines computational tasks and any number of slave processes
that execute these tasks. The master defines task requests and then waits
for the results to come in. The slaves wait for a task request, execute it,
return the result, and wait for the next task. There can be any number of
slave processes, which can be started and terminated independently, the
only condition being that no slave process can be started before its master
process. This setup makes it possible to perform a lengthy computation using
a variable number of processors.

Communication between the master and the slave processes passes through
a TaskManager object that is created automatically as part of the master
process. The task manager stores and hands out task requests and results.
The task manager also keeps track of the slave processes. When a slave process
disappears (because it was killed or because of a hardware failure), the
task manager re-schedules its active task(s) to another slave process. This
makes the master-slave system very fault tolerant.

Each task manager has a label that makes it possible to distinguish between
several master-slave groups running at the same time. It is by the label
that slave processes identify the master process for which they work.

The script "task_manager" prints statistics about a currently active task
manager; it takes the label as an argument. It shows the number of currently
active processes (master plus slaves), the number of waiting and running
tasks, and the number of results waiting to be picked up.

The script Examples/master_slave_demo.py illustrates the use of the
master-slave setup in a simple script. Both master and slave processes
are defined in the same script. The scripts Examples/master.py and
Examples/slave.py show a master-slave setup using two distinct scripts.
This is more flexible because task requests and result retrievals
can be made from anywhere in the master code.
"""

from Scientific.DistributedComputing.TaskManager import \
                      TaskManager, TaskManagerTermination, TaskRaisedException
import Pyro.core
import Pyro.naming
import Pyro.errors
import threading
import time
import copy

class MasterProcess(object):

    """
    Master process in a master-slave setup
    
    A master process in a program is implemented by subclassing
    this class and overriding the method "run", which calls the methods
    "requestTask" and "retrieveResult". The process is then
    launched by calling the method "start".
    """

    def __init__(self, label, use_name_server=True):
        """
        @param label: the label that identifies the task manager
        @type label: C{str}
        
        @param use_name_server: If C{True} (default), the task manager is
                                registered with the Pyro name server. If
                                C{False}, the name server is not used and
                                slave processes need to know the host
                                on which the master process is running.
        @type use_name_server: C{bool}
        """
        self.label = label
        self.task_manager = TaskManager()
        self.process_id = \
            self.task_manager.registerProcess(info = getMachineInfo())
        Pyro.core.initServer(banner=False)
        self.pyro_ns = None
        if use_name_server:
            self.pyro_ns=Pyro.naming.NameServerLocator().getNS()
        self.manager_thread = threading.Thread(target = self.taskManagerThread)
        self.manager_thread.start()

    def taskManagerThread(self):
        """
        This method represents the code that is executed in a background
        thread for remote access to the task manager.
        """
        self.pyro_daemon=Pyro.core.Daemon()
        if self.pyro_ns is not None:
            # Make another name server proxy for this thread
            pyro_ns=Pyro.naming.NameServerLocator().getNS()
            self.pyro_daemon.useNameServer(pyro_ns)
            try:
                pyro_ns.createGroup("TaskManager")
            except Pyro.errors.NamingError:
                pass
        uri = self.pyro_daemon.connect(self.task_manager,
                                       "TaskManager.%s" % self.label)
        try:
            self.pyro_daemon.requestLoop()
        finally:
            self.pyro_daemon.shutdown(True)
        if self.pyro_ns is not None:
            try:
                pyro_ns.unregister("TaskManager.%s" % self.label)
            except Pyro.errors.NamingError:
                pass

    def requestTask(self, tag, *parameters):
        """
        Launches a task request. The task will be executed by a slave
        process in a method called "do_"+tag that is called with the
        parameters given in the task request. Note that the order of
        task executions is not defined.

        @param tag: a tag identifying the computational task. It corresponds
                    to the name of a method in the slave process.
        @type tag: C{str}

        @param parameters: the parameters passed to the corresponding method
                           in the slave process. The only restriction on their
                           types is that all parameters must be picklable.

        @return: a unique task id
        @rtype: C{str}
        """
        return self.task_manager.addTaskRequest(tag, parameters)

    def retrieveResult(self, tag=None):
        """
        @param tag: a tag identifying the computational task from which a
                    return value is requested. If C{None}, results from
                    any task will be accepted.
        @type tag: C{str}

        @return: a tuple containing three values: the task id to which the
                 result corresponds, the tag of the computational task, 
                 and the result returned by the slave method that handled
                 the task
        @rtype: C{tuple}

        @raises TaskRaisedException: if the slave method raised an exception
        """
        try:
            if tag is None:
                return self.task_manager.getAnyResult()
            else:
                task_id, result = self.task_manager.getResultWithTag(tag)
                return task_id, tag, result
        except TaskManagerTermination:
            return None, None, None

    def start(self):
        """
        Starts the master process.
        """
        try:
            self.run()
        finally:
            self.shutdown()

    def shutdown(self):
        self.task_manager.terminate()
        while self.task_manager.numberOfActiveProcesses() > 1:
            time.sleep(0.1)
        self.pyro_daemon.shutdown()
        self.manager_thread.join()

    def run(self):
        """
        The main routine of the master process. This method must be
        overridden in subclasses.
        """
        raise NotImplementedError


class SlaveProcess(object):

    """
    Slave process in a master-slave setup
    
    A concrete slave process in a program is implemented by subclassing
    this class and adding the methods that handle the computational
    tasks. Such a method has the name "do_" followed by the tag of the
    computational task. The process is then launched by calling the
    method "start".
    """

    def __init__(self, label, master_host=None, watchdog_period=120.):
        """
        @param label: the label that identifies the task manager
        @type label: C{str}
        
        @param master_host: If C{None} (default), the task manager of the
                            master process is located using the Pyro name
                            server. If no name server is used, this parameter
                            must be the hostname of the machine on which the
                            master process runs, plus the port number if it
                            is different from the default (7766).
        @type master_host: C{str} or C{NoneType}

        @param watchdog_period: the interval (in seconds) at which the
                                slave process sends messages to the
                                manager to signal that it is still alive.
                                If None, no messages are sent at all. In that
                                case, the manager cannot recognize if the slave
                                job has crashed or been killed.
        @type watchdog_period: C{int} or C{NoneType}
        """
        Pyro.core.initClient(banner=False)
        if master_host is None:
            self.task_manager = \
                Pyro.core.getProxyForURI("PYRONAME://TaskManager.%s" % label)
        else:
            # URI defaults to "PYROLOC://localhost:7766/"
            uri = "PYROLOC://%s/TaskManager.%s" % (master_host, label)
            self.task_manager = Pyro.core.getProxyForURI(uri)
        self.watchdog_period = watchdog_period
        self.done = False
        # Compile a dictionary of methods that implement tasks
        import inspect
        self.task_methods = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if name[:3] == "do_":
                self.task_methods[name] = value

    def watchdogThread(self):
        """
        This method is run in a separate thread that pings the master process
        regularly to signal that it is still alive.
        """
        task_manager = copy.copy(self.task_manager)
        while True:
            task_manager.ping(self.process_id)
            if self.done:
                break
            time.sleep(self.watchdog_period)

    def start(self, namespace=None):
        """
        Starts the slave process.
        """
        if namespace is None:
            namespace = self.task_methods
        self.process_id = \
            self.task_manager.registerProcess(self.watchdog_period,
                                              info = getMachineInfo())
        if self.watchdog_period is not None:
            self.background_thread = \
                              threading.Thread(target=self.watchdogThread)
            self.background_thread.setDaemon(True)
            self.background_thread.start()
        while True:
            try:
                task_id, tag, parameters = \
                       self.task_manager.getAnyTask(self.process_id)
            except TaskManagerTermination:
                break
            try:
                method = namespace["do_%s" % tag]
            except KeyError:
                self.task_manager.returnTask(task_id)
                continue
            try:
                result = method(*parameters)
            except KeyboardInterrupt:
                self.task_manager.returnTask(task_id)
                self.task_manager.unregisterProcess(self.process_id)
                raise
            except Exception, e:
                import traceback, StringIO
                tb_text = StringIO.StringIO()
                traceback.print_exc(None, tb_text)
                tb_text = tb_text.getvalue()
                self.task_manager.storeException(task_id, e, tb_text)
            else:
                self.task_manager.storeResult(task_id, result)
        self.task_manager.unregisterProcess(self.process_id)
        self.done = True

def getMachineInfo():
    import os
    sysname, nodename, release, version, machine = os.uname()
    return "%s (%s)" % (nodename, machine)

#
# Job handling utility
#
def runJob(label, master_class, slave_class, watchdog_period=120.):
    """
    Creates an instance of the master_class and runs it. A copy
    of the script and the current working directory are stored in the
    TaskManager object to enable the task_manager script to launch
    slave processes.

    @param label: the label that identifies the task manager
    @type label: C{str}

    @param master_class: the class implementing the master process
                         (a subclass of L{MasterProcess})

    @param slave_class: the class implementing the slave process
                        (a subclass of L{SlaveProcess})

    @param watchdog_period: the interval (in seconds) at which the
                            slave process sends messages to the
                            manager to signal that it is still alive.
                            If None, no messages are sent at all. In that
                            case, the manager cannot recognize if the slave
                            job has crashed or been killed.
    @type watchdog_period: C{int} or C{NoneType}
    """
    import inspect
    import os
    import sys
    main_module = sys.modules['__main__']
    try:
        slave_label = main_module.SLAVE_PROCESS_LABEL
        master = label != slave_label
#        master = not getattr(main_module,
#                             "RUN_%s_AS_SLAVE" % '_'.join(label.split()))
    except AttributeError:
        master = True
    if master:
        filename = inspect.getsourcefile(main_module)
        source = file(filename).read()
        process = master_class(label)
        process.task_manager.storeData(slave_code = source,
                                       cwd = os.getcwd())
        process.start()
    else:
        slave_class(label, watchdog_period=watchdog_period).start()

#
# Alternate interface for multi-module programs
#
def initializeMasterProcess(label, slave_script=None, use_name_server=True):
    """
    Initializes a master process.

    @param label: the label that identifies the task manager
    @type label: C{str}

    @param slave_script: the file name of the script that defines
                         the corresponding slave process
    @type slave_script: C{str}

    @param use_name_server: If C{True} (default), the task manager is
                            registered with the Pyro name server. If
                            C{False}, the name server is not used and
                            slave processes need to know the host
                            on which the master process is running.
    @type use_name_server: C{bool}

    @returns: a process object on which the methods requestTask()
              and retrieveResult() can be called.
    @rtype: L{MasterProcess}
    """
    import atexit
    import os
    process = MasterProcess(label, use_name_server)
    atexit.register(process.shutdown)
    if slave_script is not None:
        source = file(slave_script).read()
        process.task_manager.storeData(slave_code = source,
                                       cwd = os.getcwd())
    return process

def startSlaveProcess(label=None, master_host=None):
    """
    Starts a slave process. Must be called at the end of a script
    that defines or imports all task handlers.

    @param label: the label that identifies the task manager. May be
                  omitted if the slave process is started through
                  the task_manager script.
    @type label: C{str} or C{NoneType}

    @param master_host: If C{None} (default), the task manager of the
                        master process is located using the Pyro name
                        server. If no name server is used, this parameter
                        must be the hostname of the machine on which the
                        master process runs, plus the port number if it
                        is different from the default (7766).
    @type master_host: C{str} or C{NoneType}
    """
    import sys
    main_module = sys.modules['__main__']
    if label is None:
        label = main_module.SLAVE_PROCESS_LABEL
        namespace = main_module.SLAVE_NAMESPACE
    else:
        namespace = main_module.__dict__
    process = SlaveProcess(label, master_host=None)
    process.start(namespace)
