from app.services.broker import FileInteractor
from app.schemas import Language


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
        if command in ['WIN', 'LOSE', 'DRAW']:
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
            for _ in range(int(n)):
                data.append(player.read_output())
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
