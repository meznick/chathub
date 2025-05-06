import asyncio
import os
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import List, Tuple, Generator

import pandas as pd

from chathub_connectors.postgres_connector import AsyncPgConnector
from datemaker import (
    setup_logger,
    DEFAULT_EVENT_IDEAL_USERS,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

LOGGER = setup_logger(__name__)


class IntelligentAgent:
    """
    MVP class for matchmaker. Will be moved to a separate service.
    """

    def __init__(
            self,
            custom_event_loop: AbstractEventLoop = None,
            postgres_connector=None,
            debug: bool = False
    ):
        self.loop = custom_event_loop or asyncio.get_event_loop()
        self.debug = debug

        if not postgres_connector:
            self.postgres_connector = AsyncPgConnector(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                db=POSTGRES_DB,
                username=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
            connect = self.loop.create_task(
                self.postgres_connector.connect(custom_loop=self.loop)
            )
            asyncio.gather(connect)
        else:
            self.postgres_connector = postgres_connector

    def cluster_users_for_event(
            self,
            users: pd.DataFrame,
            event_id: int,
            users_limit: int = DEFAULT_EVENT_IDEAL_USERS
    ):
        """
        For a given list of users need to cluster them in groups for
        the best experience.
        :param users: Dataframe with users and their features.
        :param event_id: ID of the event.
        :param users_limit: Maximum number of users per group.
        :return: Dataframe with user IDs and groups.
        """
        # Store event_id as an instance variable for use in _calculate_matchmaking_embedding
        self._current_event_id = event_id

        users = self.prepare_data(users)
        target_users, additive_users = self._split_into_genders(users)
        # target_users = self._split_by_age(target_users)  # not implemented
        # target_users = self._split_by_city(target_users)  # not implemented
        # target_users = self._split_by_rating(target_users)  # rating not implemented
        embedding_data = self._calculate_matchmaking_embedding(target_users, additive_users)
        groups = self._split_into_groups(target_users, embedding_data, users_limit)
        # put the final dataframe into dating_event_groups
        for group_num, group in enumerate(groups):
            LOGGER.debug(f'Putting group {group_num} into bd. Group size: {len(group)}')
            self.put_event_data_into_bd(
                event_id,
                group_num,
                self._generate_pairs(group)
            )

    @staticmethod
    def prepare_data(users: pd.DataFrame) -> pd.DataFrame:
        today = datetime.now().date()
        users['age'] = users['birthday'].apply(
            lambda x: today.year - x.year - (
                (today.month, today.day) < (x.month, x.day)
            )
        )
        return users

    @staticmethod
    def update_user_ratings(user_actions: pd.DataFrame) -> pd.DataFrame:
        """
        For a given dataframe with user actions update user ratings.
        Each user can choose or be chosen by another user.
        Each user can be reported.
        :param user_actions: Dataframe with user_id, rating and actions.
        :return: Dataframe with user_ids and updated ratings.
        """
        return user_actions[['user_id', 'rating']]

    @staticmethod
    def _split_into_genders(users: pd.DataFrame) -> Tuple:
        """
        Splitting users into groups by gender.
        Smaller group is target in the matchmaking process and returned first.
        Larger group is additive and returned last.
        :param users:
        :return:
        """
        LOGGER.debug('Splitting into genders')
        f_size = users.loc[users.sex == 'F'].shape[0]
        m_size = users.loc[users.sex == 'M'].shape[0]
        target_sex = 'F' if f_size < m_size else 'M'
        return (
            users.loc[users.sex == target_sex],
            users.loc[users.sex != target_sex],
        )

    @staticmethod
    def _split_by_age(users: pd.DataFrame) -> pd.DataFrame:
        """
        Split users into groups by age.
        Users in each group should have the smallest age difference to median age in group.

        Algorithm:
        - looking at age distribution for peaks
        - splitting users into groups for each peak

        :param users:
        :return:
        """
        return users

    @classmethod
    def _split_by_city(cls, users: pd.DataFrame) -> pd.DataFrame:
        """
        We want to split users into groups by city.
        The problem is in small cities.
        Since we do not have geo data now, we just randomly combine small cities in
        one.
        Sum of users should be multiple of "ideal size of group".
        :param users:
        :return:
        """
        return users

    @staticmethod
    def partition_integers(numbers: List[int], target: int) -> List[List[int]]:
        """
        AI generated, can be shit.
        The function takes a list of integers and a target integer,
        then tries to partition the list into groups with sums close to the target.
        """
        # Sort numbers in decreasing order
        numbers.sort(reverse=True)

        # To hold the groups of numbers
        partitions = []

        for number in numbers:
            # Try to find an existing partition to add this number to
            added_to_partition = False
            for group in partitions:
                if sum(group) + number <= target:
                    group.append(number)
                    added_to_partition = True
                    break

            # If no existing partition can hold the number, create a new partition
            if not added_to_partition:
                partitions.append([number])

        return partitions

    @staticmethod
    def _split_by_rating(users: pd.DataFrame) -> pd.DataFrame:
        """
        Make the best possible grouping by rating.

        :param users:
        :return:
        """
        return users

    def _calculate_matchmaking_embedding(self, target: pd.DataFrame, additive: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate matrix of compatibility coefficients for each M-F pair.

        Age scoring:
            - if target and additive users age is +-1 year (max diff 2) than score is 2
            - score decreases by 1 for each year away

        City scoring:
            - if city matches than score equals 2 else 0

        Manual scoring:
            - possible values for manual rating: 1, 2, 3
            - if target and additive users have same manual rating than score equals 6
            - score decreases by 2 for each 1 point difference

        Rating scoring: in progress.

        :param target:
        :param additive:
        :return:
        """
        LOGGER.debug('Calculating matchmaking embedding')
        embedding: pd.DataFrame = target[['user_id']].copy(deep=True)
        for additive_user in additive.user_id.values:
            embedding[str(additive_user)] = 0
            for target_user in target.user_id.values:
                # scoring age
                age_diff = abs(
                    target.loc[target.user_id == target_user].age.values[0] -
                    additive.loc[additive.user_id == additive_user].age.values[0]
                )
                score = 2 + 2 - age_diff

                # scoring city
                same_city = (
                    target.loc[target.user_id == target_user].city.values[0] ==
                    additive.loc[additive.user_id == additive_user].city.values[0]
                )
                score += 2 if same_city else 0

                # including manual tune
                manual_diff = abs(
                    target.loc[target.user_id == target_user].manual_score.values[0] -
                    additive.loc[additive.user_id == additive_user].manual_score.values[0]
                )
                score += 6 - 2 * manual_diff

                # assigning score
                embedding.loc[embedding.user_id == target_user, str(additive_user)] = score

        embedding['match'] = embedding[
            [str(x) for x in additive.user_id.values.tolist()]
        ].idxmax(axis=1)

        if self.debug:
            self.save_df_artifact(embedding, self._current_event_id, 'match_matrix')

        return embedding

    def _split_into_groups(
            self,
            target_users: pd.DataFrame,
            match_scoring_matrix: pd.DataFrame,
            users_limit: int = DEFAULT_EVENT_IDEAL_USERS,
    ) -> List[pd.DataFrame]:
        """
        Generate groups.

        1. Order target by rating, age, registration date.
        2. Select the best possible pair for each target user (every additive used once)
        3. Split into groups.

        :param target_users:
        :param match_scoring_matrix:
        :return:
        """
        sorted_user_ids = target_users.sort_values(
            by=['rating', 'registered_on_dttm'],
            ascending=False
        ).user_id.tolist()
        target_users['match'] = -1

        # Keep track of already assigned matches
        assigned_matches = set()

        match_columns = [
            col for col in match_scoring_matrix.columns
            if col != 'user_id' and col != 'match' and col.isdigit()
        ]

        for user_id in sorted_user_ids:
            # Get the user's embedding row
            user_scores = match_scoring_matrix.loc[match_scoring_matrix.user_id == user_id]
            # Sort matches by score (descending)
            matches_sorted = user_scores[match_columns].iloc[0].sort_values(ascending=False)
            # Find the first match that hasn't been assigned yet
            for match_id in matches_sorted.index:
                if match_id not in assigned_matches:
                    assigned_matches.add(match_id)
                    target_users.loc[target_users.user_id == user_id, 'match'] = match_id
                    break
            else:
                # If all potential matches are taken, delete the target user from the event
                target_users = target_users.drop(
                    target_users[target_users['user_id'] == user_id].index
                )

        if self.debug:
            self.save_df_artifact(target_users, self._current_event_id, 'matching_result')

        return self._split_dataframe(target_users, users_limit)

    @staticmethod
    def _split_dataframe(
            df: pd.DataFrame,
            chunk_size: int = DEFAULT_EVENT_IDEAL_USERS
    ) -> List[pd.DataFrame]:
        return [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

    @staticmethod
    def _generate_pairs(group: pd.DataFrame) -> Generator[Tuple[int, int, int], None, None]:
        pair_count = len(group.user_id.values.tolist())
        for turn in range(pair_count):
            for i in range(pair_count):
                first_user = group.user_id.values.tolist()[i]
                second_user_index = turn + i if turn + i < pair_count else turn + i - pair_count
                second_user = int(group.match.values.tolist()[second_user_index])
                yield turn, first_user, second_user

    @staticmethod
    def add_event_group_ids_to_pairs(event_id: int, group_id: int, data: Generator) -> Generator:
        for row in data:
            yield event_id, group_id, row[0], row[1], row[2]

    def put_event_data_into_bd(
            self,
            event_id: int,
            group_id: int,
            group_data,
    ):
        if self.loop.is_running():
            task = self.loop.create_task(
                self.postgres_connector.put_event_data(
                    data=self.add_event_group_ids_to_pairs(event_id, group_id, group_data)
                )
            )
            asyncio.gather(task)

    @staticmethod
    def save_df_artifact(embedding: pd.DataFrame, event_id: int, artifact_type: str):
        """
        Saves an embedding DataFrame as a CSV file artifact associated with a specific
        event ID and artifact type. The artifact is stored in a pre-defined directory
        structure, ensuring proper organization of event data. If the directory does
        not exist, it is created. The saved file is named according to the given
        artifact type and event ID.

        :param embedding: The DataFrame to be saved as a CSV file.
        :type embedding: pd.DataFrame
        :param event_id: The unique identifier for the event associated with the artifact.
        :type event_id: int
        :param artifact_type: A string representing the category or type of the artifact.
        :type artifact_type: str
        :return: None
        """
        artifacts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'datemaker',
            'artifacts'
        )
        os.makedirs(artifacts_dir, exist_ok=True)

        filename = f'{artifact_type}_event#{event_id}.csv'
        filepath = os.path.join(artifacts_dir, filename)

        embedding.to_csv(filepath, index=False)
        LOGGER.debug(f'Saved {artifact_type} dataframe saved to {filepath}')
