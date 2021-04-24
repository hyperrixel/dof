"""
DoF - Deep Model Core Output Framework
======================================

Submodule: services
"""


from abc import ABC, abstractmethod

from .file import DofFile
from .information import ContainerInfo


class DofSearch(ABC):
    """
    Abstract class for DoF's search functionality
    =============================================

    Attributes
    ----------
    queue : list (abstract) (read-only)
        Get a copy of the queue
    queue_queries : bool (abstract)
        Wheter or not to collect queries.
    """


    @abstractmethod
    def __init__(self):
        """
        Abstract method to initialize an instance of the object
        =======================================================
        """


    @abstractmethod
    def apply(self):
        """
        Abstract method to apply all queries in the queue
        =================================================

        Notes
        -----
            Since it is useful when there is at least one query in the queue,
            the implemented apply function may have to check the state of
            queue_queries before you call apply(). It might be useful to throw
            an error if the apply() is called when the queue_queries is False.
        """


    @property
    @abstractmethod
    def queue(self) -> list:
        """
        Abstract method to get a copy of the queue
        ==========================================

        Returns
        -------
        list
            A copy of the queue.

        Notes
        -----
            This function should return a copy of the queue only. This is useful
            to avoid external modification of the queue because modifications
            on the copy has no effect to the original queue.
        """


    @property
    @abstractmethod
    def queue_queries(self) -> bool:
        """
        Abstract method to get query optimization state
        ===============================================

        Returns
        -------
        bool
            True if queries collected into queue, False if queries are made
            inmediately.
        """


    @queue_queries.setter
    @abstractmethod
    def queue_queries(self, newstate : bool):
        """
        Abstract method to get query optimization state
        ===============================================

        Parameters
        ----------
        newstate : bool
            Wheter or not to collect queries. If True, all queries get collected
            and they are made on a .apply() call. If False all queries is
            made inmediately.

        Notes
        -----
            Example implementation of this function is as follows:

            @queue_queries.setter
            def queue_queries(self, newstate : bool):

                if not newstate:
                    self.apply()
                self.__queue_queries = newstate
        """


    @abstractmethod
    def search(self):
        """
        Abstract method to search in the stored data
        ============================================
        """


    @abstractmethod
    def store(self):
        """
        Abstract method to store the data
        =================================
        """


class DofFileServer(ABC):
    """
    Provide server to manage DoF files for the world
    ================================================
    """


    @abstractmethod
    def __init__(self):
        """
        Abstract method to initialize an instance of the object
        =======================================================
        """


    @abstractmethod
    def add_file(self, filename : str, file_data : DofFile):
        """
        Create a new file from DofFile data
        ===================================

        Parameters
        ----------
        filename : str
            Name and path of the file.
        file_data : DofFile
            Well structured and filled DofFile.
        """


    @abstractmethod
    def add_user(self, userid : str, user_data : dict):
        """
        Add new user
        ============

        Parameters
        ----------
        userid : str
            ID for the user.
        user_data : dict
            Data for the user.

        Notes
        -----
            It is advised to add userid as an unique value to avoid collision.
        """


    @abstractmethod
    def clear_log(self):
        """
        Clear the log
        =============
        """


    @abstractmethod
    def get_file(self, filename : str) -> DofFile:
        """
        Get a file
        ==========

        Parameters
        ----------
        filename : str
            Name and path of the file.

        Returns
        -------
        DofFile
            The file.
        """


    @abstractmethod
    def get_file_info(self, filename : str) -> ContainerInfo:
        """
        Get information of a file
        =========================

        Parameters
        ----------
        filename : str
            Name and path of the file.

        Returns
        -------
        ContainerInfo
            The dataset level information of the file.
        """


    @abstractmethod
    def get_log(self) -> list:
        """
        Get log information
        ===================

        Returns
        -------
        list[str]
            List of log entries.
        """


    @abstractmethod
    def get_server_state(self) -> dict:
        """
        Get server state information
        ============================

        Returns
        -------
        dict
            Server state information in key, value form.
        """


    @abstractmethod
    def get_user(self, userid : str) -> dict:
        """
        Get user data
        =============

        Parameters
        ----------
        userid : str
            The identifier of the user.

        Returns
        -------
        dict
            User information in key, value form.
        """


    @abstractmethod
    def list_files(self, query : str = '') -> list:
        """
        List files
        ==========

        Parameters
        ----------
        query : str, optional (empty string if omitted)
            Query to select files. If the parameter is empty, all files are
            returned.

        Returns
        -------
        list
            List of file identifiers or file information or files.
        """


    @abstractmethod
    def list_users(self, query : str = '') -> list:
        """
        List users
        ==========

        Parameters
        ----------
        query : str, optional (empty string if omitted)
            Query to select users. If the parameter is empty, all users are
            returned.

        Returns
        -------
        list
            List of user identifiers or user information.
        """


    @abstractmethod
    def modify_user(self, userid : str, new_data : dict):
        """
        Modification for an already existed user
        ========================================

        Parameters
        ----------
        userid : str
            ID for the user.
        new_data : dict
            New data for the user.
        """


    @abstractmethod
    def remove_file(self, filename : str):
        """
        Delete a file
        =============

        Parameters
        ----------
        filename : str
            Name and path of the file to remove.
        """


    @abstractmethod
    def remove_user(self, userid : str) -> dict:
        """
        Delete a user
        =============

        Parameters
        ----------
        userid : str
            The identifier of the user to remove.
        """


    @abstractmethod
    def start(self):
        """
        Start services
        ==============
        """


    @abstractmethod
    def stop(self):
        """
        Start services
        ==============
        """


if __name__ == '__main__':
    pass
