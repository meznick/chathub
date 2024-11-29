from typing import List

import pandas as pd


class IntelligentAgent:
    """
    MVP class for matchmaker. Will be moved to a separate service.
    """

    def cluster_users_for_event(self, users: pd.DataFrame) -> pd.DataFrame:
        """
        For a given list of users need to cluster them in groups for
        the best experience.
        :param users: Dataframe with users and their features.
        :return: Dataframe with user IDs and groups.
        """
        target_users, additive_users = self._split_into_genders(users)
        target_users = self._split_by_age(target_users)
        target_users = self._split_by_city(target_users)  # optional: if there are enough users?
        target_users = self._split_by_rating(target_users)
        additive_users = self._calculate_matchmaking_embedding(target_users, additive_users)
        # target_users

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
    def _split_into_genders(users: pd.DataFrame) -> List[pd.DataFrame]:
        """
        Splitting users into groups by gender.
        Smaller group is target in the matchmaking process and returned first.
        Larger group is additive and returned last.
        :param users:
        :return:
        """
        ...

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

    @staticmethod
    def _split_by_city(users: pd.DataFrame) -> pd.DataFrame:
        ...

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

        :param target:
        :param additive:
        :return:
        """
        return additive

    # @staticmethod
    # def _make_groups
