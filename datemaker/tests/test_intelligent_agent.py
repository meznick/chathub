import pandas as pd

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
