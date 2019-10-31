import threading, time, signal

from datetime import timedelta
from task import TaskQueue

# Extracted from https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679

WAIT_TIME_SECONDS = 1

class ProgramKilled(Exception):
    pass

def _pull_new_task(task_queue):
    task_queue.pullTask()
    
def signal_handler(signum, frame):
    raise ProgramKilled
    
class Scheduler(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        
    def stop(self):
                self.stopped.set()
                self.join()
    def run(self):
            while not self.stopped.wait(self.interval.total_seconds()):
                self.execute(*self.args, **self.kwargs)
            
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    task_queue=TaskQueue()

    scheduler = Scheduler(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=_pull_new_task, task_queue=task_queue)
    scheduler.start()

    while True:
          try:
              pass
          except ProgramKilled:
              print("Program killed: running cleanup code")
              scheduler.stop()
              task_queue.endQueue()
              break