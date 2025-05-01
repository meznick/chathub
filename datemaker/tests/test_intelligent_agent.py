import pandas as pd
import pytest

from datemaker.intelligent_agent import IntelligentAgent


def test__split_into_genders():
    users = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "sex": ["M", "F", "F", "M", "M", "F"],
            "age": [25, 30, 33, 28, 35, 42],
            "city": ["NY", "LA", "NY", "LA", "SF", "NY"],
        }
    )

    target, additive = IntelligentAgent._split_into_genders(users)

    # Testing when female users are less than male users
    assert isinstance(target, pd.DataFrame)
    assert isinstance(additive, pd.DataFrame)
    assert target["sex"].eq("M").all()
    assert additive["sex"].eq("F").all()

    # Testing when female users are less than female users
    users.loc[users["id"] == 6, "sex"] = "M"
    target, additive = IntelligentAgent._split_into_genders(users)

    assert target["sex"].eq("F").all()
    assert additive["sex"].eq("M").all()

    # Testing when users dataframe is empty
    empty_users = pd.DataFrame(columns=["id", "sex", "age", "city"])
    target, additive = IntelligentAgent._split_into_genders(empty_users)

    assert target.empty
    assert additive.empty


def test_calculate_matchmaking_embedding_no_manual_scoring():
    target_dataframe = pd.DataFrame({
        'user_id': [1, 2, 3],
        'age': [24, 29, 34],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'manual_score': [0, 0, 0],
    })

    additive_dataframe = pd.DataFrame({
        'user_id': [4, 5, 6],
        'age': [28, 30, 31],
        'city': ['Los Angeles', 'Chicago', 'New York'],
        'manual_score': [0, 0, 0],
    })

    agent = IntelligentAgent()
    result = agent._calculate_matchmaking_embedding(target_dataframe, additive_dataframe)

    assert isinstance(result, pd.DataFrame)
    assert 'match' in result.columns
    assert set(result['user_id'].values) == {1, 2, 3}

    expected_scores = {"4": [6, 11, 4], "5": [4, 9, 8], "6": [5, 8, 7]}
    for key, values in expected_scores.items():
        calculated_scores = result[key].tolist()
        assert calculated_scores == values

    assert result['match'].tolist() == ["4", "4", "5"]
