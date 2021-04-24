"""
DoF - Deep Model Core Output Framework
======================================

Submodule: storage
"""


from abc import ABC, abstractmethod
import json
from os import listdir
from os.path import isfile, join
import pickle

from .error import DofError


class DofObjectHandler(ABC):
    """
    Abstract class (de facto interface) to provide storage management of data
    =========================================================================

    Attributes
    ----------
    handler_type : str (read-only)
        Get the type of the handler.
    is_closed : bool (abstract) (read-only)
        Get whether the handler is closed or not.
    is_open : bool (abstract) (read-only)
        Get whether the handler is open or not.
    """

    # These variables should be static class level constants but this out of the
    # capabilites of Python.
    LOCAL = 'local'
    ONLINE = 'online'


    @abstractmethod
    def __init__(self, handler_type : str, *args, **kwargs):
        """
        Semi-abstract method to initialize an instance of the object
        ============================================================

        Parameters
        ----------
        handler_type : str
            Type of the DofObjectHandler. Should be DofObjectHandler.LOCAL or
            DofObjectHandler.ONLINE.

        Raises
        ------
        DofError
            When the given handler type is not suppported.
        """

        if handler_type in [DofObjectHandler.LOCAL, DofObjectHandler.ONLINE]:
            self.__handler_type = handler_type
        else:
            raise DofError('DofObjectHandler.init(): unsupported handler type.')


    @abstractmethod
    def close(self):
        """
        Abstract method to close the connection with the storage
        ========================================================
        """


    @abstractmethod
    def exist(self, location : str, is_relative : bool = True) -> bool:
        """
        Abstract method to check the existence file
        ===========================================

        Parameters
        ----------
        location : str
            Location to check.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        bool
            True if file exists, False if not.
        """


    @abstractmethod
    def files(self, location : str, is_relative : bool = True) -> list:
        """
        Abstract method to get list of files in a directory
        ===================================================

        Parameters
        ----------
        location : str
            Location to check.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        list
            List of files, empty list if no files.
        """


    @property
    def handler_type(self) -> bool:
        """
        Get the type of the handler
        ===========================

        Returns
        -------
        bool
            Type of the handler.

        See Also:
            Handler types : DofObjectHandler.LOCAL, DofObjectHandler.ONLINE
        """

        return self.__handler_type


    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """
        Get whether the handler is closed or not
        ========================================

        Returns
        -------
        bool
            True if handler is closed, False if not.
        """


    @property
    @abstractmethod
    def is_open(self) -> bool:
        """
        Abstract method to get whether the handler is open or not
        =========================================================

        Returns
        -------
        bool
            True if handler is open, False if not.
        """

    @abstractmethod
    def load_as_binary(self, location : str,
                       is_relative : bool = True) -> bytearray:
        """
        Abstract method to load data as binary data
        ===========================================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        bytearray
            Load data as bytearray.
        """


    @abstractmethod
    def load_as_instance(self, location : str,
                         is_relative : bool = True) -> any:
        """
        Abstract method to load data as instance
        ========================================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        any
            Load data as any instances.
        """


    @abstractmethod
    def load_as_json(self, location : str,
                     is_relative : bool = True) -> any:
        """
        Abstract method to load data as JSON data
        =========================================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        any
            Load data as JSON.
        """


    @abstractmethod
    def load_as_text(self, location : str, is_relative : bool = True) -> str:
        """
        Abstract method to load data as text
        ====================================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        str
            Load data as a string.
        """


    @abstractmethod
    def open(self):
        """
        Abstract method to open the connection with the storage
        =======================================================
        """


    @abstractmethod
    def save_as_binary(self, data : any, location : str,
                       is_relative : bool = True):
        """
        Abstract method to save data as binary
        ======================================

        Parameters
        ----------
        data : any
            Data to save in the form true binary data.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Notes
        -----
            By implementing this function please keep in mind that data can be
            anything. It depends on the use case what how data should be
            processed to achieve a binary form to save. Saving data in pure
            binary form (not pickle) can be a good source of building platform
            (programming language) agnostic frameworks.
        """


    @abstractmethod
    def save_as_instance(self, data : any, location : str,
                         is_relative : bool = True):
        """
        Abstract method to save data as instance
        ========================================

        Parameters
        ----------
        data : any
            Data to save in the form a python instance.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Notes
        -----
            By implementing this function please keep in mind that data should
            be saved as an instance (in most cases python instance).
        """


    @abstractmethod
    def save_as_json(self, data : any, location : str,
                     is_relative : bool = True):
        """
        Abstract method to save data as JSON data
        =========================================

        Parameters
        ----------
        data : any
            Data to save in the form JSON.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Notes
        -----
            By implementing this function please keep in mind that data should
            be saved as JSON and not everything is serializable on its own.
        """


    @abstractmethod
    def save_as_text(self, data : any, location : str,
                     is_relative : bool = True):
        """
        Abstract method to save data as text
        ====================================

        Parameters
        ----------
        data : any
            Data to save as text.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Notes
        -----
            By implementing this function please keep in mind that data can be
            anything. It depends on the use case what how data should be
            processed to achieve a text to save.
        """


class DofSerializable:
    """
    Provide serializability functions
    =================================
    """


    @abstractmethod
    def from_json(self, json_string : str, **kwargs) -> any:
        """
        Abstract methot to build object from JSON string
        ================================================

        Parameters
        ----------
        json_string : str
            The JSON formatted string that contains all the needed data.
        keyword arguments
            Arguments to forward to json.loads() funtion.

        Returns
        -------
        any
            The object that is created.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """


    def to_json(self, describe_only : bool = True, **kwargs) -> str:
        """
        Create JSON from an instance
        ============================

        Parameters
        ----------
        describe_only : bool, optional (True if omitted)
            Whether the JSON output should be a whole instance or not. If the
            value is False, the function returns all data of the instance that
            is needed to restore exactly the same instance. If the value is
            True, only those data should be included which are essential to
            describe the data.
        keyword arguments
            Arguments to forward to json.dunps() funtion.

        Returns
        -------
        str
            JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        data = self.to_json_dict(describe_only=describe_only)
        return json.dumps(data, **kwargs)


    @abstractmethod
    def to_json_dict(self, describe_only : bool = True) -> dict:
        """
        Abstract method to create a dict that is compatible to JSON from
        ================================================================

        Parameters
        ----------
        describe_only : bool, optional (True if omitted)
            Whether the JSON output should be a whole instance or not. If the
            value is False, the function returns all data of the instance that
            is needed to restore exactly the same instance. If the value is
            True, only those data should be included which are essential to
            describe the data.

        Returns
        -------
        dict
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """


class LocalHandler(DofObjectHandler):
    """
    Local storage handler
    =====================

    Attributes
    ----------
    encoding : str
        Encoding type for files with textual content (text, JSON).
    handler_type : str (inherited) (read-only)
        Get the type of the handler.
    is_closed : bool (read-only)
        Get whether the handler is closed or not.
    is_open : bool (read-only)
        Get whether the handler is open or not.
    """


    def __init__(self, base_path : str = './', encoding : str = 'uf8'):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        base_path : str, optional (./ if ommited)
            Base path to be used on loading or saving files.
        encoding : str, optional (utf8 if omitted)
            Encoding type of textual files like text and JSON files.
        """

        super().__init__(DofObjectHandler.LOCAL)
        self.__base_path = base_path
        self.__is_open = False
        self.__encoding = encoding


    def close(self):
        """
        Close the connection with the storage
        =====================================
        """

        self.__is_open = False


    @property
    def encoding(self) -> str:
        """
        Get encoding for textual files
        ==============================

        Returns
        -------
        str
            The identifier of the actual encoding method.
        """

        return self.__encoding


    @encoding.setter
    def encoding(self, newvalue : str):
        """
        Set encoding for textual files
        ==============================

        Parameters
        ----------
        newvalue : str
            The identifier of the new encoding method.
        """

        self.__encoding = newvalue


    @property
    def is_closed(self) -> bool:
        """
        Get whether the handler is closed or not
        ========================================

        Returns
        -------
        bool
            True if handler is closed, False if not.
        """

        return not self.__is_open


    @property
    def is_open(self) -> bool:
        """
        Get whether the handler is open or not
        ======================================

        Returns
        -------
        bool
            True if handler is open, False if not.
        """

        return self.__is_open


    def exist(self, location : str, is_relative : bool = True) -> bool:
        """
        Abstract method to check the existence file
        ===========================================

        Parameters
        ----------
        location : str
            Location to check.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        bool
            True if file exists, False if not.
        """
        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        return isfile(_location)


    def files(self, location : str, is_relative : bool = True) -> list:
        """
        Abstract method to get list of files in a directory
        ===================================================

        Parameters
        ----------
        location : str
            Location to check.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        list
            List of files, empty list if no files.
        """

        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        return [f for f in listdir(_location) if isfile(f)]


    def load_as_binary(self, location : str,
                       is_relative : bool = True) -> bytearray:
        """
        Load data as binary data
        ========================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        bytearray
            Load data as bytearray.

        Raises
        ------
        DofError
            If the hanlder is not yet or no mor open.
        DofError
            If the target file doesn't exist.
        """

        if not self.__is_open:
            raise DofError('LocalHandler.load_as_binary(): handler is not ' +
                           'open.')
        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        if not isfile(_location):
            raise DofError('LocalHandler.load_as_binary(): tried to ' +
                           'load binary from non-existing file "{}".'
                           .format(_location))
        with open(_location, 'rb') as instream:
            result = instream.read()
        return result


    def load_as_instance(self, location : str,
                         is_relative : bool = True) -> any:
        """
        Load data as instance
        =====================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        any
            Load data as any instances.

        Raises
        ------
        DofError
            If the hanlder is not yet or no mor open.
        DofError
            If the target file doesn't exist.
        """

        if not self.__is_open:
            raise DofError('LocalHandler.load_as_instance(): handler is not ' +
                           'open.')
        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        if not isfile(_location):
            raise DofError('LocalHandler.load_as_instance(): tried to ' +
                           'load instance from non-existing file "{}".'
                           .format(_location))
        with open(_location, 'rb') as instream:
            result = pickle.load(instream)
        return result


    def load_as_json(self, location : str, is_relative : bool = True) -> any:
        """
        Abstract method to load data as JSON data
        =========================================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        any
            Load data as JSON.

        Raises
        ------
        DofError
            If the hanlder is not yet or no mor open.
        DofError
            If the target file doesn't exist.
        """

        if not self.__is_open:
            raise DofError('LocalHandler.load_as_json(): handler is not open.')
        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        if not isfile(_location):
            raise DofError('LocalHandler.load_as_json(): tried to load JSON ' +
                           'from non-existing file "{}".'.format(_location))
        with open(_location, 'r', encoding=self.__encoding) as instream:
            result = json.load(instream)
        return result


    def load_as_text(self, location : str, is_relative : bool = True) -> list:
        """
        Load data as text
        =================

        Parameters
        ----------
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Returns
        -------
        list[str]
            Load data as a list of lines.

        Raises
        ------
        DofError
            If the hanlder is not yet or no mor open.
        DofError
            If the target file doesn't exist.
        """

        if not self.__is_open:
            raise DofError('LocalHandler.load_as_text(): handler is not open.')
        if is_relative:
            _location = join(self.__base_path, location)
        else:
            _location = location
        if not isfile(_location):
            raise DofError('LocalHandler.load_as_text(): tried to load text ' +
                           'from non-existing file "{}".'.format(_location))
        with open(_location, 'r', encoding=self.__encoding) as instream:
            result = instream.readlines()
        return result


    def open(self):
        """
        Abstract method to open the connection with the storage
        =======================================================
        """

        self.__is_open = True


    def save_as_binary(self, data : any, location : str,
                       is_relative : bool = True):
        """
        Save data as binary
        ===================

        Parameters
        ----------
        data : any
            Data to save in the form true binary data.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Raises
        ------
        DofError
            When the handler is not open.
        """

        if self.__is_open:
            if is_relative:
                _location = join(self.__base_path, location)
            else:
                _location = location
            if hasattr(data, 'to_binary') or isinstance(data, bytearray):
                if hasattr(data, 'to_binary'):
                    to_write = data.to_binary()
                else:
                    to_write = data
                with open(_location, 'wb') as outstream:
                    outstream.write(to_write)
            else:
                with open(_location, 'wb') as outstream:
                    pickle.dump(data, outstream)
        else:
            raise DofError('LocalHandler.save_as_binary(): handler is not ' +
                           'open.')


    def save_as_instance(self, data : any, location : str,
                         is_relative : bool = True):
        """
        Save data as instance
        =====================

        Parameters
        ----------
        data : any
            Data to save in the form a python instance.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Raises
        ------
        DofError
            When the handler is not open.
        """

        if self.__is_open:
            if is_relative:
                _location = join(self.__base_path, location)
            else:
                _location = location
            with open(_location, 'wb') as outstream:
                pickle.dump(data, outstream)
        else:
            raise DofError('LocalHandler.save_as_instance(): handler is not ' +
                           'open.')


    def save_as_json(self, data : any, location : str,
                     is_relative : bool = True):
        """
        Abstract method to save data as JSON data
        =========================================

        Parameters
        ----------
        data : any
            Data to save in the form JSON.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Raises
        ------
        DofError
            When the handler is not open.
        """

        if self.__is_open:
            if is_relative:
                _location = join(self.__base_path, location)
            else:
                _location = location
            with open(_location, 'w', encoding=self.__encoding) as outstream:
                json.dump(data, outstream)
        else:
            raise DofError('LocalHandler.save_as_instance(): handler is not ' +
                           'open.')


    def save_as_text(self, data : any, location : str,
                     is_relative : bool = True):
        """
        Save data as text
        =================

        Parameters
        ----------
        data : str | list
            Data to save as text. If list is given, elements of list is
            considered is lines of text.
        location : str
            Location to save to.
        is_relative : bool, optional (True if omitted)
            Whether to treat location string as relative or absolute location.
            Relative location means that the value will be added to a base path
            or base url or something like those.

        Raises
        ------
        DofError
            When the handler is not open.
        """

        if self.__is_open:
            if isinstance(data, list):
                _output = '\n'.join([str(row) for row in list])
            else:
                _output = data
            if is_relative:
                _location = join(self.__base_path, location)
            else:
                _location = location
            with open(_location, 'w', encoding=self.__encoding) as outstream:
                outstream.write(_output)
        else:
            raise DofError('LocalHandler.save_as_text(): handler is not open.')


if __name__ == '__main__':
    pass
