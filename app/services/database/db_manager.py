import os
import uuid
import sqlite3

ABS_PATH = "C:\\Programming\\KUSOI\\server"


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
                                result TEXT
                            )
                        """)

    def add_game(self, team1: uuid.UUID, team2: uuid.UUID, result: str) -> uuid.UUID:
        game_id = uuid.uuid4()
        data = (str(game_id), str(team1), str(team2), result)
        self.cursor.execute("INSERT INTO game (game_id, team1, team2, result) VALUES(?, ?, ?, ?)", data)
        self._conn.commit()
        return game_id

    def game_id_by_team_id(self, team_id: uuid.UUID) -> list[tuple]:
        data = []
        team_id = str(team_id)
        for row in self.cursor.execute("SELECT timestamp, game_id FROM game WHERE team1 = ?", (team_id,)):
            data.append(row)
        for row in self.cursor.execute("SELECT timestamp, game_id FROM game WHERE team2 = ?", (team_id,)):
            data.append(row)
        return data

    def result_by_game_id(self, game_id: uuid.UUID) -> str:
        data = []
        for row in self.cursor.execute("SELECT result FROM game WHERE game_id = ?", (str(game_id),)):
            data.append(row[0])
        return data[0]

    def close(self) -> None:
        self._conn.close()
