import logging
from datetime import datetime
from typing import Generator

import pandas as pd
import pytest

from datemaker.intelligent_agent import IntelligentAgent

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

AGENT = IntelligentAgent()


def test__split_into_genders():
    users = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "sex": ["M", "F", "F", "M", "M", "F"],
            "age": [25, 30, 33, 28, 35, 42],
            "city": ["NY", "LA", "NY", "LA", "SF", "NY"],
        }
    )

    target, additive = AGENT._split_into_genders(users)

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

    result = AGENT._calculate_matchmaking_embedding(target_dataframe, additive_dataframe)

    assert isinstance(result, pd.DataFrame)
    assert 'match' in result.columns
    assert set(result['user_id'].values) == {1, 2, 3}

    expected_scores = {"4": [6, 11, 4], "5": [4, 9, 8], "6": [5, 8, 7]}
    for key, values in expected_scores.items():
        calculated_scores = result[key].tolist()
        assert calculated_scores == values

    assert result['match'].tolist() == ["4", "4", "5"]


users_demo_case = pd.DataFrame({
    'user_id': [1, 2, 3],
    'rating': [0, 0, 0],
    'age': [24, 29, 34],
    'city': ['New York', 'Los Angeles', 'Chicago'],
    'manual_score': [0, 0, 0],
    'registered_on_dttm': [datetime.now(), datetime.now(), datetime.now()],
})
embedding_data_demo_case = pd.DataFrame({
    'user_id': [1, 2, 3],
    "4": [6, 11, 4],
    "5": [4, 9, 8],
    "6": [5, 8, 7],
    "match": ["4", "4", "5"]
})
@pytest.mark.parametrize("target_users, embedding_data, users_limit", [
    (users_demo_case, embedding_data_demo_case, 20),
])
def test_split_into_groups(target_users, embedding_data, users_limit):
    result = AGENT._split_into_groups(target_users, embedding_data, users_limit)
    logging.debug(f'\n{result}')
    assert isinstance(result, list)
    assert len(result[0].match.unique().tolist()) == result[0].index.size


def test__split_dataframe():
    # Test case 1: Normal case with DataFrame size > chunk_size
    df = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'value': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    })

    # Using the AGENT instance
    result = AGENT._split_dataframe(df, chunk_size=3)

    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 3, "Should split into 3 chunks"
    assert len(result[0]) == 3, "First chunk should have 3 rows"
    assert len(result[1]) == 3, "Second chunk should have 3 rows"
    assert len(result[2]) == 2, "Third chunk should have 2 rows"

    # Verify content of chunks
    assert result[0]['user_id'].tolist() == [1, 2, 3], "First chunk should contain user_ids 1, 2, 3"
    assert result[1]['user_id'].tolist() == [4, 5, 6], "Second chunk should contain user_ids 4, 5, 6"
    assert result[2]['user_id'].tolist() == [7, 8], "Third chunk should contain user_ids 7, 8"

    # Test case 2: Edge case with DataFrame size < chunk_size
    small_df = pd.DataFrame({
        'user_id': [1, 2],
        'value': ['a', 'b']
    })

    # Using the class method
    result = IntelligentAgent._split_dataframe(small_df, chunk_size=5)

    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 1, "Should have only one chunk"
    assert len(result[0]) == 2, "Chunk should have 2 rows"
    assert result[0]['user_id'].tolist() == [1, 2], "Chunk should contain all user_ids"

    # Test case 3: Edge case with empty DataFrame
    empty_df = pd.DataFrame(columns=['user_id', 'value'])

    result = IntelligentAgent._split_dataframe(empty_df, chunk_size=3)

    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 0, "Should have no chunks for empty DataFrame"

    # Test case 4: Edge case with chunk_size = 1
    result = IntelligentAgent._split_dataframe(df, chunk_size=1)

    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 8, "Should split into 8 chunks"
    for i, chunk in enumerate(result):
        assert len(chunk) == 1, f"Chunk {i} should have 1 row"
        assert chunk['user_id'].tolist() == [i+1], f"Chunk {i} should contain user_id {i+1}"


def test__generate_pairs():
    def dataframe_generator():
        yield pd.DataFrame({
            'user_id': [1, 2, 3],
            'match': [4, 5, 6]
        })

    group = next(dataframe_generator())
    pairs = AGENT._generate_pairs(group)

    assert isinstance(pairs, Generator), "Output should be a generator"

    expected_pairs = [
        (0, 1, 4), (0, 2, 5), (0, 3, 6),
        (1, 1, 5), (1, 2, 6), (1, 3, 4),
        (2, 1, 6), (2, 2, 4), (2, 3, 5),
    ]

    generated_pairs = list(pairs)

    assert len(generated_pairs) == len(expected_pairs), "Generated incorrect number of pairs"

    for pair in generated_pairs:
        assert pair in expected_pairs, f"Unexpected pair generated: {pair}"

    for pair in expected_pairs:
        assert pair in generated_pairs, f"Expected pair missing: {pair}"
