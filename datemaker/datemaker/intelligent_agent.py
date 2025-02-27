import asyncio
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

    def __init__(self, custom_event_loop: AbstractEventLoop = None, postgres_connector=None):
        self.loop = custom_event_loop or asyncio.get_event_loop()

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
        :return: Dataframe with user IDs and groups.
        """
        users = self.prepare_data(users)
        target_users, additive_users = self._split_into_genders(users)
        # target_users = self._split_by_age(target_users)  # not implemented
        # target_users = self._split_by_city(target_users)  # not implemented
        # target_users = self._split_by_rating(target_users)  # rating not implemented
        embedding_data = self._calculate_matchmaking_embedding(target_users, additive_users)
        groups = self._split_into_groups(target_users, embedding_data, users_limit)
        # put the final dataframe into dating_event_groups
        for group_num, group in enumerate(groups):
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

    @staticmethod
    def _calculate_matchmaking_embedding(target: pd.DataFrame, additive: pd.DataFrame) -> pd.DataFrame:
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

        embedding['match'] = embedding[[str(x) for x in additive.user_id.values.tolist()]].idxmax(axis=1)
        return embedding

    @classmethod
    def _split_into_groups(
            cls,
            target_users: pd.DataFrame,
            embedding_data: pd.DataFrame,
            users_limit: int = DEFAULT_EVENT_IDEAL_USERS,
    ) -> List[pd.DataFrame]:
        """
        Generate groups.

        1. Order target by rating, age and registration date.
        2. Select the best possible pair for each target user (every additive used once)
        3. Split into groups.

        :param target_users:
        :param embedding_data:
        :return:
        """
        sorted_user_ids = target_users.sort_values(
            by=['rating', 'registered_on_dttm'],
            ascending=False
        ).user_id.tolist()
        target_users['match'] = -1
        for user in sorted_user_ids:
            target_users.loc[
                target_users.user_id == user, 'match'
            ] = embedding_data.loc[embedding_data.user_id == user].match.values[0]
        return cls._split_dataframe(target_users, users_limit)

    @staticmethod
    def _split_dataframe(df: pd.DataFrame, chunk_size: int = DEFAULT_EVENT_IDEAL_USERS) -> List[pd.DataFrame]:
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
