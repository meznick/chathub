import pandas as pd


class IntelligentAgent:
    @staticmethod
    def cluster_users_for_event(users: pd.DataFrame) -> pd.DataFrame:
        """
        For a given list of users need to cluster them in groups for
        the best experience.
        :param users: Dataframe with users and their features.
        :return: Dataframe with user IDs and groups.
        """
        ...

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
