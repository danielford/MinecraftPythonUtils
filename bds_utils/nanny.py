import argparse
import sys
import logging
import collections
import xmlrpc.server
import time
import fcntl
import signal
import threading
import subprocess
import os

from .command import CommandExecution, ListCommand, ShutdownCommand

class BedrockServerNanny:

    RPC_PORT = 11542
    METRICS_INTERVAL_SECONDS = 10

    LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'

    def __init__(self, bds_dir, log_dir=None):
        if log_dir:
            server_log = os.path.join(log_dir, 'server.log')
            metrics_log = os.path.join(log_dir, 'metrics.log')

            logging.basicConfig(
                filename=server_log,
                format=self.LOG_FORMAT,
                level=logging.INFO)

            metrics_handler = logging.FileHandler(metrics_log)
            metrics_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))

            self.metrics_logger = logging.getLogger('metrics')
            self.metrics_logger.setLevel(logging.INFO)
            self.metrics_logger.addHandler(metrics_handler)
            #self.metrics_logger.propagate = False

            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            logging.basicConfig(format=self.LOG_FORMAT, level=logging.INFO)
            self.logger = logging.getLogger(self.__class__.__name__)
            self.metrics_logger = self.logger

        self.bds_dir = bds_dir
        self.command_queue = collections.deque()
        self.running_command = None

    def __log(self, line):
        self.logger.info(line)

    def __start_rpc_server(self):
        with xmlrpc.server.SimpleXMLRPCServer(('localhost', self.RPC_PORT), allow_none=True) as server:
            server.register_introspection_functions()
            server.register_function(self.__enqueue_command_str, 'send_command')
            server.serve_forever()

    def __start_metrics_emitter(self):
        def log_metrics(num_players, max_players):
            self.__log('in metrics logger')
            self.metrics_logger.info('NUM_PLAYERS %d' % int(num_players))
            self.metrics_logger.info('MAX_PLAYERS %d' % int(max_players))

        while self.running:
            self.__enqueue_command(ListCommand, log_metrics)
            time.sleep(self.METRICS_INTERVAL_SECONDS)

    def __nb_read(self, pipe):
        fd = pipe.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        try:
            return pipe.read()
        except:
            return ''

    def __consume_stdout(self):
        output = self.__nb_read(self.proc.stdout).strip()
        for line in output.split('\n'):
            if line:
                self.__log(line)

        if self.running_command:
            if output and self.running_command.check(output):
                self.running_command = None
        else:
            if self.command_queue:
                self.running_command = self.command_queue.popleft()
                self.running_command.send(self.proc.stdin)

        if output:
            return True
        else:
            return False

    def __enqueue_command_str(self, command_str):
        self.command_queue.append(CommandExecution(command_str, None, None))

    def __enqueue_command(self, command, handler=None):
        self.command_queue.append(CommandExecution(command.command, command.pattern, handler))

    def run(self):
        def shutdown(signum, frame):
            self.__enqueue_command(ShutdownCommand)

        def ignore_signals():
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)


        self.proc = subprocess.Popen([os.path.join(self.bds_dir, 'bedrock_server')], 
            cwd=self.bds_dir, bufsize=1, universal_newlines=True,
            env={ 'LD_LIBRARY_PATH': self.bds_dir }, preexec_fn=ignore_signals,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.running = True

        threading.Thread(target=self.__start_rpc_server, daemon=True).start()
        threading.Thread(target=self.__start_metrics_emitter, daemon=True).start()

        while self.running:
            # check if process has terminated
            if self.proc.poll() is not None:
                self.running = False
            
            if not self.__consume_stdout():
                time.sleep(0.1)

        self.__log('bedrock server exited with status: %d' % self.proc.returncode)

def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument('bds_dir', help='path to directory containing bedrock dedicated server')
    parser.add_argument('-l', '--log_dir', help='write logs to <log_dir>/server.log instead of stdout')
    args = parser.parse_args()

    BedrockServerNanny(args.bds_dir, log_dir=args.log_dir).run()
