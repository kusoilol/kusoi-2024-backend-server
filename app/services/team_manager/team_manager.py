import os
from os.path import join as path_join
from tempfile import SpooledTemporaryFile

from .config import TEAMS_PATH, HISTORY_NAME
from app.schemas import Language


class TeamManager:
    """
    stateless helper class to manage operation with teams

    """

    @staticmethod
    def _get_files_in_dir(directory):
        return [f for f in os.listdir(directory) if os.path.isfile(path_join(directory, f))]

    def _get_main_sol(self):
        return TeamManager._get_files_in_dir(self.team_path)

    def _get_history_sols(self):
        return TeamManager._get_files_in_dir(self.team_path)

    def _get_all_files(self):
        return self._get_main_sol(), self._get_history_sols()

    def __init__(self, team_id: int):
        self.team_id = team_id
        self.team_path = path_join(TEAMS_PATH, str(self.team_id))
        os.makedirs(path_join(self.team_path, HISTORY_NAME), exist_ok=True)
        self.max_id = 0
        main_sol, history_sols = self._get_all_files()
        self.max_id = max(int(filename.split('.')[0]) for filename in (main_sol + history_sols + ["0."]))

    def create_solution(self, file: SpooledTemporaryFile, language: Language):
        current_main = self._get_main_sol()
        filename = str(self.max_id + 1)
        extension = language.value
        filepath = path_join(self.team_path, filename + extension)
        try:
            with open(filepath, 'wb') as save:
                save.write(file.read())
        except IOError:
            if os.path.isfile(filepath):
                os.remove(filepath)
            raise
        finally:
            if not file.closed:
                file.close()
        if current_main:
            os.rename(path_join(self.team_path, current_main[0]),
                      path_join(self.team_path, HISTORY_NAME, current_main[0]))
        self.max_id += 1
