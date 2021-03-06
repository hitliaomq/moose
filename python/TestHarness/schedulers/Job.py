import re
from timeit import default_timer as clock


class Timer(object):
    """
    A helper class for testers to track the time it takes to run.

    Every call to the start method must be followed by a call to stop.
    """
    def __init__(self):
        self.starts = []
        self.ends = []
    def start(self):
        """ starts the timer clock """
        self.starts.append(clock())
    def stop(self):
        """ stop/pauses the timer clock """
        self.ends.append(clock())
    def cumulativeDur(self):
        """ returns the total/cumulative time taken by the timer """
        diffs = [end - start for start, end in zip(self.starts, self.ends)]
        return sum(diffs)
    def avgerageDur(self):
        return self.cumulativeDur() / len(self.starts)
    def nRuns(self):
        return len(self.starts)
    def reset(self):
        self.starts = []
        self.ends = []

class Job(object):
    """
    The Job class is a simple container for the tester and its associated output file object, the DAG,
    the process object, the exit codes, and the start and end times.
    """
    def __init__(self, tester, tester_dag, options):
        self.options = options
        self.__tester = tester
        self.timer = Timer()
        self.__dag = tester_dag
        self.__dag_clone = None
        self.__outfile = None
        self.__start_time = clock()
        self.__end_time = None
        self.__std_out = ''
        self.report_timer = None

    def getTester(self):
        """ Return the tester object """
        return self.__tester

    def getDAG(self):
        """ Return the DAG object """
        return self.__dag

    def getOriginalDAG(self):
        """
        Retreive the DAG object from the state it was when setOriginalDAG was called or the current
        state it is in now, if setOriginalDAG was never called.
        """

        return self.setOriginalDAG()

    def setOriginalDAG(self):
        """
        Create a soft clone of the working DAG for what ever state it is currently in. This method
        should only be called once, and once the working DAG is properly set up.

        This is to protect the DAG from further tampering.
        """

        if self.__dag_clone == None:
            self.__dag_clone = self.__dag.clone()
        return self.__dag_clone

    def getTestName(self):
        """ Wrapper method to return the testers test name """
        return self.__tester.getTestName()


    def run(self):
        """
        A blocking method to handle the exit status of the process object while keeping track of the
        time the process was active. When the process exits, read the output and close the file.
        """
        self.__tester.prepare(self.options)

        if self.options.dry_run or not self.__tester.shouldExecute():
            self.__tester.setStatus(self.__tester.getSuccessMessage(), self.__tester.bucket_success)
            return

        self.timer.reset()
        self.__tester.run(self.timer, self.options)
        self.__start_time = self.timer.starts[0]
        self.__end_time = self.timer.ends[-1]
        self.__std_out = self.__tester.std_out

    def killProcess(self):
        """ Kill remaining process that may be running """
        self.__tester.killCommand()

    def getStartTime(self):
        """ Return the time the process started """
        return self.__start_time

    def getEndTime(self):
        """ Return the time the process exited """
        return self.__end_time

    def getOutput(self):
        """ Return the contents of output """
        return self.__std_out

    def setOutput(self, output):
        """ Method to allow testers to overwrite the output if certain conditions are met """
        if self.__tester.outfile is not None and not self.__tester.outfile.closed:
            return
        self.__std_out = output

    def getActiveTime(self):
        """ Return active time """
        m = re.search(r"Active time=(\S+)", self.__std_out)
        if m != None:
            return m.group(1)

    def getSolveTime(self):
        """ Return solve time """
        m = re.search(r"solve().*", self.__std_out)
        if m != None:
            return m.group().split()[5]

    def getTiming(self):
        """ Return active time if available, if not return a comparison of start and end time """
        if self.getActiveTime():
            return self.getActiveTime()
        elif self.getEndTime() and self.getStartTime():
            return self.timer.cumulativeDur()
        elif self.getStartTime() and self.__tester.isPending():
            # If the test is still running, return current run time instead
            return max(0.0, clock() - self.getStartTime())
        else:
            return 0.0
