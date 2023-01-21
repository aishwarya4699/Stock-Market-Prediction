import os
import sys
from abc import abstractmethod
from atexit import register
from signal import SIGTERM
from time import sleep


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            # exit first parent
            if pid > 0: sys.exit(0)

        except OSError as e:
            sys.stderr.write(f"fork #1 failed: {e.errno} ({e.strerror})\n")
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            # exit from second parent
            if pid > 0: sys.exit(0)

        except OSError as e:
            sys.stderr.write(f"fork #2 failed: {e.errno} ({e.strerror})\n")
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, "r")
        so = open(self.stdout, "a+")
        se = open(self.stderr, "a+", 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write register
        register(self.delpid)
        with open(self.pidfile, "w+") as f:
            f.write(f"{os.getpid()}\n")

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            sys.stderr.write(f"pidfile {self.pidfile} already exist. Daemon already running?\n")
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, "r")
            pid = int(pf.read().strip())
            pf.close()

        except IOError:
            pid = None

        if not pid:
            sys.stderr.write(f"pidfile {self.pidfile} does not exist. Daemon not running?\n")
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                sleep(0.1)

        except OSError as err:
            if (err := str(err)).find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)

            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    @abstractmethod
    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by start() or restart().
        """
        raise NotImplementedError
