# Command script for managing trajectory files in a networked environment.
# Requires that a TrajectoryServer is running on each participating machine.
#
# Written by Konrad Hinsen
# last revision: 2000-2-24
#

import Pyro.core, Pyro.naming, Pyro.errors
from TrajectoryManager import TrajectoryManager
import os, socket, string, sys

manager = TrajectoryManager()

def show_usage():
    sys.stderr.write('Usage: tmanager command [arguments]\n')
    sys.stderr.write('  Commands:\n')
    sys.stderr.write('     list\n')
    sys.stderr.write('     status\n')
    sys.stderr.write('     publish filename\n')
    sys.stderr.write('     unpublish filename\n')
    sys.stderr.write('     servers\n')
    sys.stderr.write('     shutdown\n')
    sys.exit(1)

def list_trajectories():
    files = manager.trajectoryList()
    for file in files:
        sys.stdout.write(file+'\n')
        sys.stdout.flush()

def trajectory_status():
    files = manager.trajectoryList()
    for file in files:
        inspector = manager.trajectoryInspector(file)
        inspector.reopen()
        sys.stdout.write('%s\n    %d steps\n' %
                         (file, inspector.numberOfSteps()))
        sys.stdout.flush()

def list_servers():
    servers = manager.serverList()
    for server in servers:
        sys.stdout.write(server+'\n')
        sys.stdout.flush()

def quit():
    manager = find_manager()
    if manager is None:
        return
    manager.stop()

commands = {'list': list_trajectories,
            'status': trajectory_status,
            'publish': manager.publish,
            'unpublish': manager.unpublish,
            'servers': list_servers,
            'shutdown': manager.stopServer}

if len(sys.argv) < 2:
    show_usage()

try:
    function = commands[sys.argv[1]]
except KeyError:
    show_usage()

try:
    apply(function, tuple(sys.argv[2:]))
except TypeError:
    show_usage()
