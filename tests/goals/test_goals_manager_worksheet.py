from unittest.mock import Mock

import pytest

from goals.goals_manager import GoalsManager
from goals.goals_manager_worksheet import GoalsManagerWorksheet


@pytest.fixture
def setup_goals_manager_worksheet_with_values(request) -> GoalsManager:
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param
    return GoalsManagerWorksheet(worksheet_mock)


@pytest.mark.parametrize('setup_goals_manager_worksheet_with_values', [[[]]], indirect=True)
def test_get_goals_when_no_goals(setup_goals_manager_worksheet_with_values):
    assert len(setup_goals_manager_worksheet_with_values.get_goals()) == 0


@pytest.mark.parametrize('setup_goals_manager_worksheet_with_values',
                         [[["year", "2023"], ["quarter", "q1"], ["some-goal", "in_progress"]]], indirect=True)
def test_get_goals_when_one_year_has_goals(setup_goals_manager_worksheet_with_values):
    goals = setup_goals_manager_worksheet_with_values.get_goals()

    assert 1 == len(goals)
    assert "2023" in goals
    assert 1 == len(goals["2023"].q1)
    assert 0 == len(goals["2023"].q2)
    assert 0 == len(goals["2023"].q3)
    assert 0 == len(goals["2023"].q4)
