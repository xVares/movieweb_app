import json
from abc import ABC
from uuid import uuid4
from .data_manager_interface import DataManagerInterface
from typing import Union


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename: str):
        self.filename = filename

    @staticmethod
    def write_json(filename, content):
        """
        Write JSON content to a file.

        :param filename: The path to the JSON file.
        :type filename: str
        :param content: The data to be written to the file.
        :type content: Any valid JSON-serializable object
        """
        with open(filename, "w") as file:
            json.dump(content, file, indent=4)

    def get_all_users(self) -> Union[dict, None]:
        """
        Return all the users from a JSON file as a dictionary.

        :return: A dictionary containing user data if successful, or None if an error occurs.
        :rtype: Union[dict, None]
        """
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except OSError:
            return None

    def add_user(self, new_user_name):
        """
        Adds a new user to the database.

        :param new_user_name: The name of the new user.
        """
        all_users = self.get_all_users()

        # Generate a new user ID and add the user to the database
        new_user_id = str(uuid4())
        all_users[new_user_id] = {
            "name": new_user_name,
            "movies": {}
        }

        # Update JSON file with new user
        self.write_json(self.filename, all_users)

    def delete_user(self, user_id) -> bool:
        """
        Delete a user from the database.

        :param user_id: The unique identifier of the user to be deleted.
        :type user_id: str
        :return: True if the user was successfully deleted, False if the user does not exist.
        :rtype: bool
        """
        all_users = self.get_all_users()

        # Is user in database? -> del & return True
        if user_id in all_users:
            del all_users[user_id]
            self.write_json(self.filename, all_users)
            return True
        return False

    def get_user_name_and_movies(self, user_id) -> Union[tuple, False]:
        """
        Get the name and movies of a user from the database.

        :param user_id: The unique identifier of the user.
        :type user_id: str
        :return: A tuple containing the user's name and movie collection if the user exists,
                 otherwise False.
        :rtype: Union[tuple, False]
        """
        all_users = self.get_all_users()
        user = all_users.get(user_id)

        # Is user in database? -> return False
        if not user:
            return False

        user_name = user.get("name")
        user_movies = user.get("movies")

        # Does user have any movies?
        if not user_movies:
            user_movies = None
        return user_name, user_movies

    def add_movie(self, is_fetch_successful, fetched_movie_data) -> bool:
        """
        Add a new movie to the user's collection.

        :param is_fetch_successful: A boolean indicating whether the movie data was successfully fetched.
        :type is_fetch_successful: bool
        :param fetched_movie_data: The data of the fetched movie.
        :type fetched_movie_data: dict
        :return: True if the movie was successfully added, False if the movie already exists in the collection.
        :rtype: bool
        """
        fetched_movie_title = fetched_movie_data["Title"]
        fetched_movie_director = fetched_movie_data["Director"]
        fetched_movie_year = fetched_movie_data["Year"]
        fetched_movie_rating = fetched_movie_data["imdbRating"]

        stored_movie_data = self.get_all_users()

        # Is movie already in users favorites? -> return False
        if fetched_movie_title in stored_movie_data:
            return False

        unique_id = str(uuid4())
        new_movie = {
            "name": fetched_movie_title,
            "director": fetched_movie_director,
            "rating": fetched_movie_rating,
            "year": fetched_movie_year
        }
        #  Add fetched movie to database & return True
        stored_movie_data["movies"][unique_id] = new_movie
        self.write_json(self.filename, stored_movie_data)
        return True

    def update_user_movies(self, user_id, movie_id, update_data) -> bool:
        """
        Update the specified movie data for a given user.

        :param user_id: The unique identifier of the user.
        :type user_id: str
        :param movie_id: The unique identifier of the movie to be updated.
        :type movie_id: str
        :param update_data: The updated data for the movie.
        :type update_data: dict
        :return: True if the movie data was successfully updated, False if the user or movie does not exist.
        :rtype: bool
        """
        all_users = self.get_all_users()
        user = all_users.get(user_id)
        has_movies = user.get("movies")

        # Is user in database or has user movies? -> return False
        if not user or not has_movies:
            return False

        # Update movie data for user
        user_movies = user["movies"]
        user_movies[movie_id].update(update_data)
        user["movies"] = user_movies
        all_users[user_id] = user

        # Write updated data back to JSON file
        self.write_json(self.filename, all_users)
        return True

    def delete_user_movie(self, user_id, movie_id) -> bool:
        """
        Delete the specified movie of a user.

        :param user_id: The unique identifier of the user.
        :type user_id: str
        :param movie_id: The unique identifier of the movie to be deleted.
        :type movie_id: str
        :return: True if the movie was successfully deleted, False if the user or movie does not exist.
        :rtype: bool
        """

        all_users = self.get_all_users()
        user = all_users.get(user_id)
        has_movies = user.get("movies")

        # Is user in database or has user movies? -> return False
        if not user or not has_movies:
            return False

        # Delete movie
        user_movies = user["movies"]
        del user_movies[movie_id]
        user["movies"] = user_movies
        all_users[user_id] = user

        # Write updated data back to JSON file
        self.write_json(self.filename, all_users)
        return True
