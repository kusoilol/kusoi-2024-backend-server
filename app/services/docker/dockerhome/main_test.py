from enum import Enum
import queue
import subprocess
import threading
import time


class Language(Enum):
    """
    Represents the language of the solution.
    The number of supported languages may increase.
    """
    PYTHON = ".py"
    # PYPY = ".pypy.py"
    CPP20GPP = ".gpp.cpp"
    # JAVA21 = ".java"


class FileInteractor:
    def __init__(self, path: str, language: Language):
        self.path = path
        self.language = language
        self.process = None
        self.message_queue = queue.Queue()
        self.output_thread = None
        self.lock = threading.Lock()

    def run_subprocess(self, user: str = "root") -> None:
        cmd = []
        match self.language:
            case Language.PYTHON:
                cmd = ['python3', '-u', self.path]
            case Language.CPP20GPP:
                pass

        self.process = subprocess.Popen(cmd,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        text=True,
                                        user=user)

        self.output_thread = threading.Thread(target=self._enqueue_output, daemon=True)
        self.output_thread.start()

    def _enqueue_output(self) -> None:
        while True:
            line = self.process.stdout.readline()
            if line:
                self.message_queue.put(line)
            else:
                break

    def _process_exist_checker(self) -> None:
        if self.process is None:
            raise IOError("The process doesn't exist yet or already terminated")

    def send_input(self, input_data: str) -> None:
        self._process_exist_checker()
        with self.lock:
            self.process.stdin.write(input_data + '\n')
            self.process.stdin.flush()

    def read_output(self, timeout=1) -> str | None:
        self._process_exist_checker()
        for _ in range(3):
            try:
                return self.message_queue.get(timeout=timeout).strip()
            except queue.Empty:
                time.sleep(0.1)
                continue
        return None

    def close(self) -> None:
        if self.process:
            self.process.terminate()
            self.output_thread.join()
            self.output_thread = None
            self.process = None


def _log(data: str):
    print(data)


class GameBroker:
    alice: FileInteractor
    bob: FileInteractor
    tester: FileInteractor
    turn: int

    def __init__(self, path_1: str, lang_1: Language, user_1: str,
                 path_2: str, lang_2: Language, user_2: str,
                 tester_path: str):
        self.alice = FileInteractor(path_1, lang_1)
        self.bob = FileInteractor(path_2, lang_2)
        self.tester = FileInteractor(tester_path, Language.PYTHON)
        self.alice.run_subprocess(user_1)
        self.bob.run_subprocess(user_2)
        self.tester.run_subprocess()
        self.turn = 0

    def _cleanup(self):
        self.alice.close()
        self.bob.close()
        self.tester.close()

    def make_move(self) -> int:
        """
        :return: 0 for alive game, -1 for draw, 1 or 2 - winner id
        """
        player = self.alice if self.turn % 2 == 0 else self.bob
        try:
            command, n = self.tester.read_output().split()
            _log("Tester")
            _log(command + " " + n)
            n = int(n)
        except (RuntimeError, TypeError, ValueError, IOError):
            self._cleanup()
            raise
        if command in ['win', 'lose', 'draw']:
            self._cleanup()
            return n
        try:
            data = []
            for _ in range(n):
                data.append(self.tester.read_output())
        except (RuntimeError, TypeError, ValueError, IOError):
            self._cleanup()
            raise
        try:
            _log('\n'.join(data))
            player.send_input('\n'.join(data))
        except (RuntimeError, TypeError, ValueError, IOError) as e:
            _log(f"Player {self.turn % 2 + 1} couldn't get input or something\n: {str(e)}")
            self._cleanup()
            return (self.turn + 1) % 2 + 1

        try:
            n = player.read_output()
            if n is None:
                _log(f"Player {self.turn % 2 + 1} didn't answer to tester's query")
                self._cleanup()
                return (self.turn + 1) % 2 + 1
            _log(f"Player {self.turn % 2 + 1}")
            _log(n)
            data = [n]
        except (RuntimeError, TypeError, ValueError, IOError) as e:
            _log(f"Player {self.turn % 2 + 1} incorrect answer to tester's query\n: {str(e)}")
            self._cleanup()
            return (self.turn + 1) % 2 + 1

        try:
            _log('\n'.join(data))
            self.tester.send_input('\n'.join(data))
        except (RuntimeError, TypeError, ValueError, IOError):
            self._cleanup()
            raise
        self.turn += 1
        return 0


PATH_1 = "../test/alice.py"
PATH_2 = "../test/bob.py"
PATH_3 = "tester.py"

game_broker = GameBroker(PATH_1, Language.PYTHON, "alice",
                         PATH_2, Language.PYTHON, "bob",
                         PATH_3)
while True:
    if x := game_broker.make_move():
        print(x)
        break