from enum import Enum


class GoalProgress(Enum):
    not_started = 0
    in_progress = 1
    done = 2

    def to_json(self):
        return str(self.name)


class Goal:

    def __init__(self, name: str, progress: GoalProgress):
        self.name = name
        self.progress = progress


class YearlyGoals:

    def __init__(self):
        self.q1 = list()
        self.q2 = list()
        self.q3 = list()
        self.q4 = list()


class GoalsManager:

    def get_goals(self) -> dict:
        raise NotImplementedError
