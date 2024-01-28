from goals.goals_manager import GoalsManager, GoalProgress, YearlyGoals, Goal


class GoalsManagerDynamo(GoalsManager):

    def __init__(self, table):
        self.table = table

    def get_goals(self) -> dict:

        items = self.table.scan()["Items"]

        goals = {}
        for item in items:
            year = item["Year"]
            quarter = item["Quarter"]
            name = item["id"]
            progress = item["Progress"]

            if year not in goals:
                goals[year] = YearlyGoals()
            this_yearly_goals = goals[year]
            getattr(this_yearly_goals, quarter).append(Goal(name, getattr(GoalProgress, progress)))
        return goals
