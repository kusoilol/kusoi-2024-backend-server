import queue
import subprocess
import threading
import time

from app.schemas import Language


class FileInteractor:
    def __init__(self, path: str, language: Language):
        self.path = path
        self.language = language
        self.process = None
        self.message_queue = queue.Queue()
        self.output_thread = None
        self.lock = threading.Lock()

    def run_subprocess(self) -> None:
        cmd = []
        match self.language:
            case Language.PYTHON:
                cmd = ['python3', '-u', self.path]
            case Language.CPP20GPP:
                pass

        self.process = subprocess.Popen(cmd,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        text=True)

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
