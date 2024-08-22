from dataclasses import dataclass
from enum import Enum

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


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


@dynamo_item("goals")
@dataclass
class PersistedGoal:
    year: str
    quarter: str
    id: str
    progress: GoalProgress


class GoalsManager(Repository[PersistedGoal]):

    def __init__(self):
        super().__init__(PersistedGoal)

    def get_goals(self) -> dict:
        items = self.get_all()

        goals = {}
        for item in items:
            year = item.year
            quarter = item.quarter
            name = item.id
            progress = item.progress

            if year not in goals:
                goals[year] = YearlyGoals()
            this_yearly_goals = goals[year]
            getattr(this_yearly_goals, quarter).append(Goal(name, progress))
        return goals
