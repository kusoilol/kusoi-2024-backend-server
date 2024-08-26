import os
import time
import uuid
import sqlite3

from .config import DATA_PATH


class DBManager:
    def __init__(self):
        self._conn = sqlite3.connect(os.path.join(DATA_PATH, 'db.sqlite'))
        self.cursor = self._conn.cursor()
        res = self.cursor.execute("SELECT name FROM sqlite_master WHERE name='game'")
        if res.fetchone() is None:
            self.cursor.execute("""
                            CREATE TABLE game(
                                game_id TEXT PRIMARY KEY,
                                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                                team1 TEXT,
                                team2 TEXT,
                                winner TEXT,
                                log TEXT
                            )
                        """)
        res = self.cursor.execute("SELECT name FROM sqlite_master WHERE name='scoreboard'")
        if res.fetchone() is None:
            self.cursor.execute("""
            CREATE TABLE scoreboard(
            team_id TEXT PRIMARY KEY,
            score INTEGER
            )
            """)
            self._conn.commit()

    def add_game(self, team1: uuid.UUID, team2: uuid.UUID, winner: str, log: str) -> uuid.UUID:
        game_id = uuid.uuid4()
        data = (str(game_id), str(team1), str(team2), str(winner), log)
        for i in range(3):
            try:
                self.cursor.execute("INSERT INTO game (game_id, team1, team2, winner, log) VALUES(?, ?, ?, ?, ?)", data)
                self._conn.commit()
                break
            except sqlite3.DatabaseError as e:
                time.sleep(0.1)
                if i == 2:
                    print(str(e))
                    raise
                continue
        return game_id

    def inc_score(self, team_id: uuid.UUID, add: int):
        if self.cursor.execute("SELECT * FROM scoreboard WHERE team_id = ?",
                               (str(team_id),)).fetchone() is None:
            self.cursor.execute("INSERT INTO scoreboard VALUES (?, ?)", (str(team_id), 0))

        self.cursor.execute("UPDATE scoreboard SET score = score + ? WHERE team_id = ?",
                            (add, str(team_id),))
        self._conn.commit()

    def get_games(self, team_id: uuid.UUID) -> list[tuple] | None:
        data = []
        team_id = str(team_id)
        for row in self.cursor.execute("SELECT timestamp, game_id, winner, team2 FROM game WHERE team1 = ?",
                                       (team_id,)):
            data.append(row)
        for row in self.cursor.execute("SELECT timestamp, game_id, winner, team1 FROM game WHERE team2 = ?",
                                       (team_id,)):
            data.append(row)
        if not data:
            return None
        return data

    def get_log(self, game_id: uuid.UUID) -> str | None:
        data = []
        for row in self.cursor.execute("SELECT log FROM game WHERE game_id = ?", (str(game_id),)):
            data.append(row[0])
        if not data:
            return None
        return data[0]

    def get_score(self, team_id: uuid.UUID) -> int:
        res = self.cursor.execute("SELECT score FROM scoreboard WHERE team_id = ?",
                                  (str(team_id),)).fetchone()
        if res is None:
            return 0
        return res[0]

    def dump_scoreboard(self, teams: list[uuid.UUID] = None) -> dict:
        """
        :param teams: list of teams which result will be returned
        :return: scoreboard dump
        """
        if teams is not None:
            teams = set(teams)
        data = dict()
        for team_id, score in self.cursor.execute("SELECT * from scoreboard").fetchall():
            if teams is None or uuid.UUID(team_id) in teams:
                data[team_id] = score
        return data

    def close(self) -> None:
        self._conn.close()