"""Model representing an nhl skater"""
import datetime
from typing import List


class Skater:
    def __init__(
            self,
            assists: int,
            assists_pp: int,
            assists_sh: int,
            blocks: int,
            faceoff_pct: float,
            faceoffs: int,
            faceoffs_won: int,
            game_dates: List,
            giveaways: int,
            goals: int,
            goals_pp: int,
            goals_sh: int,
            hits: int,
            name: str,
            pim: int,
            plus_minus: int,
            position: str,
            shots: int,
            takeaways: int,
            team: str,
            toi: datetime.datetime,
            toi_ev: datetime.datetime,
            toi_pp: datetime.datetime,
            toi_sh: datetime.datetime,
            games: int = 1
    ):
        self.assists = assists
        self.assists_pp = assists_pp
        self.assists_sh = assists_sh
        self.blocks = blocks
        self.faceoff_pct = faceoff_pct
        self.faceoffs = faceoffs
        self.faceoffs_won = faceoffs_won
        self.games = games
        self.game_dates = game_dates
        self.giveaways = giveaways
        self.goals = goals
        self.goals_pp = goals_pp
        self.goals_sh = goals_sh
        self.hits = hits
        self.name = name
        self.pim = pim
        self.plus_minus = plus_minus
        self.position = position
        self.shots = shots
        self.takeaways = takeaways
        self.team = team
        self.toi = toi
        self.toi_ev = toi_ev
        self.toi_pp = toi_pp
        self.toi_sh = toi_sh

    @property
    def shooting_percentage(self):
        return round(self.goals/self.shots, 2)

