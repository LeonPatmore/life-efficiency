from gspread import Worksheet

from goals.goals_manager import GoalsManager, GoalProgress, YearlyGoals, Goal


class GoalsManagerWorksheet(GoalsManager):

    def __init__(self, worksheet: Worksheet):
        self.worksheet = worksheet

    def get_goals(self) -> dict:
        final_goals = dict()
        worksheet_values = self.worksheet.get_all_values()
        current_year_goals = None
        current_quarter_list = None
        for row in worksheet_values:
            if len(row) < 1:
                continue
            if row[0] == "year":
                current_year = row[1]
                current_year_goals = YearlyGoals()
                final_goals[current_year] = current_year_goals
            elif row[0] == "quarter":
                current_quarter = row[1]
                current_quarter_list = list()
                setattr(current_year_goals, current_quarter, current_quarter_list)
            else:
                goal_name = row[0]
                goal_progress = getattr(GoalProgress, row[1])
                current_quarter_list.append(Goal(goal_name, goal_progress))
        return final_goals
