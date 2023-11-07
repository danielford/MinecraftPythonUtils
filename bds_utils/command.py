import collections
import re
import logging
import time

MinecraftCommand = collections.namedtuple(
    'MinecraftCommand', ['command', 'pattern'])

ListCommand = MinecraftCommand('list', re.compile(
    'There are (\d+)\/(\d+) players online:'))
ShutdownCommand = MinecraftCommand(
      'stop', re.compile('Server stop requested'))

class CommandExecution:
    def __init__(self, command, pattern, handler, timeout_ms=10_000):
        self.command = command
        self.pattern = pattern
        self.handler = handler
        self.buffer = ''
        self.timeout_ms = timeout_ms
        self.logger = logging.getLogger(self.__class__.__name__)

    def send(self, pipe):
        self.started_ms = time.time() * 1000.0
        pipe.write(self.command + '\n')
        pipe.flush()

    def check(self, new_output):
        if not self.handler:
            return True
        
        if (time.time() * 1000.0) > self.started_ms + self.timeout_ms:
            self.logger.error('Timed out waiting for response to command: %s' % self.command)
            return True

        self.buffer += new_output
        match = self.pattern.search(self.buffer)

        if match:
            self.logger.debug('Found match: %s' % match)
            self.handler(*match.groups())
            return True
        else:
            return False
