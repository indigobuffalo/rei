"""Model representing an nhl skater"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List

from dashboard.util.misc import duration_to_min_and_sec


class Skater:
    def __init__(
            self,
            assists: int,
            assists_pp: int,
            assists_sh: int,
            blocks: int,
            faceoffs: int,
            faceoffs_won: int,
            game_dates: List[datetime],
            giveaways: int,
            goals: int,
            goals_pp: int,
            goals_sh: int,
            hits: int,
            name: str,
            pim: int,
            plus_minus: int,
            positions: List[str],
            shots: int,
            takeaways: int,
            team: str,
            toi: List[timedelta],
            toi_ev: List[timedelta],
            toi_pp: List[timedelta],
            toi_sh: List[timedelta],
            games: int = 1
    ):
        self.assists = assists
        self.assists_pp = assists_pp
        self.assists_sh = assists_sh
        self.blocks = blocks
        self.faceoff_pct = round((faceoffs_won/faceoffs), 2) if faceoffs else None
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
        self.positions = positions
        self.shots = shots
        self.shooting_percentage = round(self.goals/self.shots, 2) if self.shots else 'NA'
        self.takeaways = takeaways
        self.team = team
        self.toi = toi
        self.toi_ev = toi_ev
        self.toi_pp = toi_pp
        self.toi_sh = toi_sh

    def __add__(self, other: Skater) -> Skater:
        team = self.team if max(self.game_dates) > max(other.game_dates) else other.team
        if self.name != other.name:
            raise ValueError(f'Cannot aggregate stats for two different players: {self.name}')
        return Skater(
            assists=self.assists + other.assists,
            assists_pp=self.assists_pp + other.assists_pp,
            assists_sh=self.assists_sh + other.assists_sh,
            blocks=self.blocks + other.blocks,
            faceoffs=self.faceoffs + other.faceoffs,
            faceoffs_won=self.faceoffs_won + other.faceoffs_won,
            games=self.games + other.games,
            game_dates=self.game_dates + other.game_dates,
            giveaways=self.giveaways + other.giveaways,
            goals=self.goals + other.goals,
            goals_pp=self.goals_pp + other.goals_pp,
            goals_sh=self.goals_sh + other.goals_sh,
            hits=self.hits + other.hits,
            name=self.name,
            pim=self.pim + other.pim,
            plus_minus=self.plus_minus + other.plus_minus,
            positions=list(set(self.positions + other.positions)),
            shots=self.shots + other.shots,
            takeaways=self.takeaways + other.takeaways,
            team=team,
            toi=self.toi + other.toi,
            toi_ev=self.toi_ev + other.toi_ev,
            toi_pp=self.toi_pp + other.toi_pp,
            toi_sh=self.toi_sh + other.toi_sh
        )

    def json_normalized(self):
        normalized = self.__dict__
        normalized['game_dates'] = [datetime.strftime(d, '%m/%d') for d in self.game_dates]
        normalized['toi'] = [duration_to_min_and_sec(toi) for toi in self.toi]
        normalized['toi_ev'] = [duration_to_min_and_sec(toi) for toi in self.toi_ev]
        normalized['toi_pp'] = [duration_to_min_and_sec(toi) for toi in self.toi_pp]
        normalized['toi_sh'] = [duration_to_min_and_sec(toi) for toi in self.toi_sh]
        return normalized
