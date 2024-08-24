import os
import time
import uuid
import sqlite3

ABS_PATH = "C:\\Programming\\KUSOI\\server\\data"


class DBManager:
    def __init__(self):
        self._conn = sqlite3.connect(os.path.join(ABS_PATH, 'db.sqlite'))
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

    def add_game(self, team1: uuid.UUID, team2: uuid.UUID, winner: uuid.UUID, log: str) -> uuid.UUID:
        game_id = uuid.uuid4()
        data = (str(game_id), str(team1), str(team2), str(winner), log)
        self.cursor.execute("INSERT INTO game (game_id, team1, team2, winner, log) VALUES(?, ?, ?, ?, ?)", data)
        for i in range(3):
            try:
                self._conn.commit()
                break
            except sqlite3.DatabaseError as e:
                time.sleep(0.1)
                if i == 2:
                    print(str(e))
                continue
        return game_id

    def games_by_team_id(self, team_id: uuid.UUID) -> list[tuple] | None:
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

    def log_by_game_id(self, game_id: uuid.UUID) -> str | None:
        data = []
        for row in self.cursor.execute("SELECT log FROM game WHERE game_id = ?", (str(game_id),)):
            data.append(row[0])
        if not data:
            return None
        return data[0]

    def score_by_team_id(self, team_id: uuid.UUID) -> int:
        return self.cursor.execute("SELECT COUNT(*) FROM game WHERE winner = ?",
                                   (str(team_id),)).fetchone()[0]

    def close(self) -> None:
        self._conn.close()
