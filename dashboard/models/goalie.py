"""Model representing an nhl goalie"""
from __future__ import annotations

from typing import List


class Goalie:

    def __init__(
            self,
            game_dates: List,
            name: str,
            saves: int,
            saves_ev: int,
            saves_pp: int,
            saves_sh: int,
            shots: int,
            shots_ev: int,
            shots_pp: int,
            shots_sh: int,
            team: str,
            decision: str = 'NA',
            games: int = 1,
            losses: int = None,
            wins: int = None
    ):
        if wins:
            self.wins = wins
        else:
            self.wins = 1 if decision.upper() == 'W' else 0

        if losses:
            self.losses = losses
        else:
            self.losses = 1 if decision.upper() == 'L' else 0

        self.games = games
        self.game_dates = game_dates
        self.losses = losses
        self.name = name
        self.position = 'G'
        self.saves = saves
        self.saves_ev = saves_ev
        self.saves_pp = saves_pp
        self.saves_sh = saves_sh
        self.shots = shots
        self.shots_ev = shots_ev
        self.shots_pp = shots_pp
        self.shots_sh = shots_sh
        self.save_percentage = round(saves/shots, 3) if shots else None
        self.save_percentage_ev = round(saves_ev/shots_ev, 3) if shots_ev else None
        self.save_percentage_pp = round(saves_pp/shots_pp, 3) if shots_pp else None
        self.save_percentage_sh = round(saves_sh/shots_sh, 3) if shots_sh else None
        self.team = team
        self.wins = wins

    def __add__(self, other: Goalie) -> Goalie:
        team = self.team if max(self.game_dates) > max(other.game_dates) else other.team
        return Goalie(
            games=self.games + other.games,
            game_dates=self.game_dates + other.game_dates,
            losses=self.losses + other.losses,
            name=self.name,
            saves=self.saves + other.saves,
            saves_ev=self.saves_ev + other.saves_ev,
            saves_pp=self.saves_pp + other.saves_pp,
            saves_sh=self.saves_sh + other.saves_sh,
            shots=self.shots + other.shots,
            shots_ev=self.shots_ev + other.shots_ev,
            shots_pp=self.shots_pp + other.shots_pp,
            shots_sh=self.shots_sh + other.shots_sh,
            team=team,
            wins=self.wins + other.wins
        )

