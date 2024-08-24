from uuid import UUID
import os
from os.path import join as path_join
from typing import IO

from .config import TEAMS_PATH, HISTORY_NAME
from app.schemas import Language


class TeamManager:
    """
    stateless helper class to manage operation with teams

    """

    max_id: int

    @staticmethod
    def _get_files_in_dir(directory):
        return [f for f in os.listdir(directory) if os.path.isfile(path_join(directory, f))]

    def get_main_filename(self) -> list[str]:
        return TeamManager._get_files_in_dir(self._team_path)

    def has_solutions(self) -> bool:
        return self.max_id == 0

    def get_main_solution(self):
        if self.max_id == 0:
            raise FileNotFoundError(f"Team {self.team_id} doesn't have any solutions yet")
        return path_join(self._team_path, TeamManager._get_files_in_dir(self._team_path)[0])

    def get_language_of_main(self) -> Language:
        data = self.get_main_filename()[0].split('.')
        extension = '.' + '.'.join(data[1:])
        return Language(extension)

    def _get_history_sols(self):
        return TeamManager._get_files_in_dir(path_join(self._team_path, HISTORY_NAME))

    @staticmethod
    def _get_id_from_filename(filename) -> int:
        return int(filename.split('.')[0])

    def _get_all_files(self):
        return self.get_main_filename(), self._get_history_sols()

    def __init__(self, team_id: UUID):
        self.team_id = team_id
        self._team_path = path_join(TEAMS_PATH, str(self.team_id))
        os.makedirs(path_join(self._team_path, HISTORY_NAME), exist_ok=True)
        self.max_id = 0
        main_sol, history_sols = self._get_all_files()
        self.max_id = max(
            TeamManager._get_id_from_filename(filename) for filename in (main_sol + history_sols + ["0."]))

    def create_solution(self, file: IO[bytes], language: Language):
        current_main = self.get_main_filename()
        filename = str(self.max_id + 1)
        extension = language.value
        filepath = path_join(self._team_path, filename + extension)
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
            os.rename(path_join(self._team_path, current_main[0]),
                      path_join(self._team_path, HISTORY_NAME, current_main[0]))
        self.max_id += 1
        return self.max_id

    def get_solution(self, solution_id: int):
        """
        :return: filepath to solution with given id
        :raise: FileNotFoundError if such solution doesn't exist
        """
        main_sol, history_sols = self._get_all_files()
        if main_sol and TeamManager._get_id_from_filename(main_sol[0]) == solution_id:
            return path_join(self._team_path, main_sol[0])
        for filename in history_sols:
            if int(filename.split('.')[0]) == solution_id:
                return path_join(self._team_path, HISTORY_NAME, filename)
        raise FileNotFoundError(f"Team {self.team_id} doesn't have solution with id {solution_id}")

    def select_main(self, solution_id: int):
        try:
            solution_path = self.get_solution(solution_id)
            current_main = self.get_main_filename()[0]
            if TeamManager._get_id_from_filename(current_main) == solution_id:
                return
            filename = os.path.basename(solution_path)
            os.rename(solution_path, path_join(self._team_path, filename))
            os.rename(path_join(self._team_path, current_main),
                      path_join(self._team_path, HISTORY_NAME, current_main))
        except FileNotFoundError:
            raise
        except IOError:
            raise
