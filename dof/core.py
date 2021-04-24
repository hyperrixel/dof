"""
DoF - Deep Model Core Output Framework
======================================

Submodule: core

Notes
-----
    We tried to minimize the number of imports to the neccessary ones. That's
    why we used `from json import loads` instead of `import json` and
    `from pickle import dumps, loads` instead of `import pickle`. Due to the
    readability of code we named some imports. Users usually see for example
    `json.loads` or `pickle.loads` in code, so we use `json_loads`,
    `pickle_dumps` and `pickle_loads` expressions to provide both readability of
    code and optimization at the same time.
"""

# pylint: disable=too-many-lines
#           I.  Docstring and code together consumes a lot of lines of code.
#          II.  We try to keep similar or related classes in the same file.
#         III.  The working code may be under the 1000 lines limit, but we
#               think, docstring with notations is useful to anybody to
#               understand our code and the way of our thinking.


from json import loads as json_loads
from pickle import dumps as pickle_dumps, loads as pickle_loads

from .datamodel import ContentForm, JSONDescription, JSONRoot
from .datamodel import create_json_dict, get_content
from .error import DofError
from .storage import DofObjectHandler, DofSerializable


class DofObject(DofSerializable):
    """
    Wrap data in DoF
    ================

    Attributes
    ----------
    data : any
        Data from memory.

    is_binary : bool
        Whether the DofObject is a wrapper of a real binary data (eg. document)
    is_in_memory : bool (read-only)
        Whether data is in the memory or not.
    is_relative_local : bool (read-only)
        Local path's relativity state.
    is_relative_online : bool (read-only)
        Online link's relativity state.
    local_handler_id : int
        Id of local handler.
    local_path : str (read-only)
        Local path of the data.
    online_handler_id : int
        Id of online handler.
    online_link : str (read-only)
        Online link of the data.
    """


    # pylint: disable=too-many-public-methods
    #         The amount of public methods is needed due to the functionality.


    # pylint: disable=too-many-instance-attributes
    #         The amount of attributes is needed because of the functionality.


    __local_handlers = {}
    __online_handlers = {}
    __local_default = -1
    __online_default = -1


    def __init__(self, data : any = None, local_path : str = '',
                 is_relative_local : bool = True, local_handler_id : int = -1,
                 online_link : str = '', is_relative_online : bool = True,
                 online_handler_id : int = -1, is_binary : bool = False):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        data : any, optional (None if omitted)
            Data to store in memory.
        local_path : str, optional (empty string if omitted)
            Local unique location of the data.
        is_relative_local : bool, optional (True if omitted)
            Whether the given local location is relative or not.
        local_handler_id : int, optional (-1 if omitted)
            Id of local handler.
        online_link : str, optional (empty string if omitted)
            Online unique link of the data.
        is_relative_online : bool, optional (True if omitted)
            Whether the given online link is relative or not.
        online_handler_id : int, optional (-1 if omitted)
            Id of online handler.
        is_binary : bool, optinal (False if omitted)
            Whether the DofObject is a wrapper of a real binary data.

        Notes
        -----
            The is_binary flag is True when the DofObject contains real binary
            data, for example any document. In all other cases the state is
            False.
        """

        # pylint: disable=too-many-arguments
        #         We consider a better practice having long list of named
        #         arguments then having **kwargs only.

        self.__data = data
        self.__local_path = local_path
        self.__is_relative_local = is_relative_local
        self.__local_handler_id = local_handler_id
        self.__online_link = online_link
        self.__is_relative_online = is_relative_online
        self.__online_handler_id = online_handler_id
        self.__is_binary = is_binary


    @classmethod
    def add_handler(cls, handler : DofObjectHandler,
                    as_default : bool = False) -> int:
        """
        Add handler to DofObject
        ========================

        Parameters
        ----------
        handler : DofObjectHandler
            Handler to add.
        as_default : bool, optional (False if omitted)
            Whether or not to set handler as default.

        Raises
        ------
        DofError
            If tha handler_type parameter of the handler is unknown.

        Returns
        -------
        int
            The id of the new handler.
        """

        if handler.handler_type == DofObjectHandler.LOCAL:
            next_id = len(cls.__local_handlers)
            cls.__local_handlers[next_id] = handler
            if as_default or next_id == 0:
                cls.__local_default = next_id
        elif handler.handler_type == DofObjectHandler.ONLINE:
            next_id = len(cls.__online_handlers)
            cls.__online_handlers[next_id] = handler
            if as_default or next_id == 0:
                cls.__online_default = next_id
        else:
            raise DofError('DofObject.add_handler(): Unsupported handler type.')


    @classmethod
    def available_handlers(cls, handler_type : str) -> list:
        """
        Get all available handlers
        ==========================

        Parameters
        ----------
        handler_type : str
            Which type of handler is listed.

        Result
        ------
        list
            List of all available handler within the given handler type.

        Raises
        ------
        DofError
            When the handler type is not supported.

        See Also
        --------
            Possible type of handlers : storage.DofObjectHandler
        """

        result = []
        if handler_type == DofObjectHandler.LOCAL:
            for key in sorted(cls.__local_handlers.keys()):
                if cls.__local_handlers[key] is not None:
                    result.append(key)
        elif handler_type == DofObjectHandler.ONLINE:
            for key in sorted(cls.__online_handlers.keys()):
                if cls.__online_handlers[key] is not None:
                    result.append(key)
        else:
            raise DofError('DofObject.available_handlers(): Unsupported ' +
                           'handler type.')
        return result


    @property
    def data(self) -> any:
        """
        Get data from memory
        ====================
        """

        return self.__data


    @data.setter
    def data(self, new_value : any):
        """
        Set the data
        ============

        Parameters
        ----------
        new_value : any
            New value to set as data.
        """

        self.__data = new_value


    @classmethod
    def delete_handler(cls, handler_type : str, handler_id : int):
        """
        Delete handler
        ==============

        Parameters
        ----------
        handler_type : str
            Type of the handler to delete. Must be DofObjectHandler.LOCAL or
            DofObjectHandler.ONLINE.
        handler_id : int
            The id of the handler to delete.

        Raises
        ------
        DofError
            If the given local handler does not exist.
        DofError
            If the local handler is already deleted.
        DofError
            If the given online handler does not exist.
        DofError
            If the online handler is already deleted.
        DofError
            If the handler_type parameter is unknown.

        See Also
        --------
            Possible type of handlers : storage.DofObjectHandler
        """

        if handler_type == DofObjectHandler.LOCAL:
            if not handler_id in cls.__local_handlers.keys():
                raise DofError('DofObject.delete_handler(): handler id {} '
                               .format(handler_id) + 'doesn\'t exist in LOCAL' +
                               ' handlers.')
            if cls.__local_handlers[handler_id] is None:
                raise DofError('DofObject.delete_handler(): handler id {} '
                               .format(handler_id) + 'in LOCAL is already ' +
                               'deleted.')
            cls.__local_handlers[handler_id] = None
        elif handler_type == DofObjectHandler.ONLINE:
            if not handler_id in cls.__online_handlers.keys():
                raise DofError('DofObject.delete_handler(): handler id {} '
                               .format(handler_id) + 'doesn\'t exist in ' +
                               'ONLINE handlers.')
            if cls.__online_handlers[handler_id] is None:
                raise DofError('DofObject.delete_handler(): handler id {} '
                               .format(handler_id) + 'in ONLINE is already ' +
                               'deleted.')
            cls.__online_handlers[handler_id] = None
        else:
            raise DofError('DofObject.delete_handler(): Unsupported handler ' +
                           'type.')


    def force_load_to_memory(self) -> bool:
        """
        Load data to memory if possible
        ===============================

        Returns
        -------
        bool
            True if data get loaded into the memory, False if not.

        Notes
        -----
            This function contains try-except formula to provide smooth run.
            Since it load data into memory if it is possible, we handle the most
            problems within a try method where only DofErrors are caught by
            except.
        """
        if not self.is_in_memory:
            try:
                self.__load_local()
            except DofError:
                pass
        if not self.is_in_memory:
            try:
                self.__load_online()
            except DofError:
                pass
        return self.is_in_memory


    @classmethod
    def from_json(cls, json_string : str, **kwargs) -> any:
        """
        Build object from JSON string
        =============================

        Parameters
        ----------
        json_string : str
            The JSON formatted string that contains all the needed data.
        keyword arguments
            Arguments to forward to json.loads() funtion.

        Returns
        -------
        DofObject
            The object that is created.

        Raises
        ------
        DofError
            If the content of the JSON string is not valid to create the
            instance.
        DofError
            If the JSON string seems to bu valid but the stored instance is
            not a DofObject.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = json_loads(json_string, **kwargs)
        data = get_content(json_dict, 'DofObject', 'dof.core',
                           describe_only=False)
        if data is None:
            raise DofError('DofObject.from_json(): JSON string is not valid ' +
                           'to create an instance.')
        _object = pickle_loads(bytes.fromhex(data[JSONRoot.CONTENT.value]))
        if not isinstance(_object, DofObject):
            raise DofError('DofObject.from_json(): JSON string contained ' +
                           'invalid instance, it should be type of DofObject' +
                           'but is type "{}"'.format(type(_object)))
        return _object


    @classmethod
    def get_handler(cls, handler_type : str,
                    handler_id : int) -> DofObjectHandler:
        """
        Get the specific object handler
        ===============================

        Parameters
        ----------
        handler_type : str
            Type of a handler to check.
        handler_id : id
            Id of handler to check.

        Returns
        -------
        DofObjectHandler
            Instance of the specified object handler.

        Raises
        ------
        DofError
            When the given local handler is never existed.
        DofError
            When the given local handler is already deleted.
        DofError
            When the given online handler is never existed.
        DofError
            When the given online handler is already deleted.
        DofError
            Whether the given handler_type is not supported.

        See Also
        --------
            Possible type of handlers : storage.DofObjectHandler
        """
        result = None
        if handler_type == DofObjectHandler.LOCAL:
            if handler_id == -1:
                result = cls.__local_handlers[cls.__local_default]
            elif handler_id not in cls.__local_handlers.keys():
                raise DofError('DofObject.get_handler(): tried to get a LOCAL' +
                               ' handler that never existed.')
            elif  cls.__local_handlers[handler_id] is None:
                raise DofError('DofObject.get_handler(): tried to get a LOCAL' +
                               ' handler that is already deleted.')
            else:
                result = cls.__local_handlers[handler_id]
        elif handler_type == DofObjectHandler.ONLINE:
            if handler_id == -1:
                result = cls.__online_handlers[cls.__online_default]
            elif handler_id not in cls.__online_handlers.keys():
                raise DofError('DofObject.get_handler(): tried to get an ' +
                               'ONLINE handler that never existed.')
            elif cls.__online_handlers[handler_id] is None:
                raise DofError('DofObject.get_handler(): tried to get an ' +
                               'ONLINE handler that is already deleted.')
            else:
                result = cls.__online_handlers[handler_id]
        else:
            raise DofError('DofObject.get_handler(): Unsupported handler ' +
                           'type.')
        return result


    @classmethod
    def handler_exists(cls, handler_type : str, handler_id : int) -> bool:
        """
        Checking the existence of a specific handler
        ============================================

        Parameters
        ----------
        handler_type : str
            Type of a handler to check.
        handler_id : id
            Id of handler to check.

        Returns
        -------
        bool
            Whether the specific handler exists or not.

        Raises
        ------
        DofError
            Whether the given handler_type is not supported.

        See Also
        --------
            Possible type of handlers : storage.DofObjectHandler
        """

        result = False
        if handler_type == DofObjectHandler.LOCAL:
            if handler_id == -1:
                result = True
            elif handler_id not in cls.__local_handlers.keys():
                result = False
            else:
                result = cls.__local_handlers[handler_id] is not None
        elif handler_type == DofObjectHandler.ONLINE:
            if handler_id == -1:
                result = True
            elif handler_id not in cls.__online_handlers.keys():
                result = False
            else:
                result = cls.__online_handlers[handler_id] is not None
        else:
            raise DofError('DofObject.handler_exists(): Unsupported handler ' +
                           'type.')
        return result


    @property
    def is_binary(self) -> bool:
        """
        Get the state of is_binary flag
        ===============================

        Returns
        -------
        bool
            State of is_binary flag.

        See Also
        --------
            Meaning the state of is_binary flag : DofObject
        """

        return self.__is_binary


    @is_binary.setter
    def is_binary(self, new_value : bool):
        """
        Set the state of is_binary flag
        ===============================

        Parameters
        ----------
        new_value : bool
            The new state of is_binary flag.

        See Also
        --------
            Meaning the state of is_binary flag : DofObject
        """

        self.__is_binary = new_value


    @property
    def is_in_memory(self) -> bool:
        """
        Get whether data is in the memory or not
        ========================================

        Returns
        -------
        bool
            True if data is in the memory, False if not.
        """

        return self.__data is not None


    @property
    def is_relative_local(self) -> bool:
        """
        Get local path's relativity state
        =================================

        Returns
        -------
        bool
            True if the local path is relative, False if not.
        """

        return self.__is_relative_local


    @property
    def is_relative_online(self) -> bool:
        """
        Get the online link's relativity state
        ======================================

        Returns
        -------
        bool
            True if the online link is relative, False if not.
        """

        return self.__is_relative_online


    def load(self, source_type : str = DofObjectHandler.LOCAL):
        """
        Load data from the source
        =========================

        Parameters
        ----------
        source_type : str, optional (DofObjectHandler.LOCAL if omitted)
            Source of data.

        Raises
        ------
        DofError
            When the type of handler is not supported.

        See Also
        --------
            Constants for selecting the source : storage.DofObjectHandler
            Possible type of handlers : storage.DofObjectHandler

        Notes
        -----
            Type of source can be local or online.
        """
        if source_type == DofObjectHandler.LOCAL:
            self.__load_local()
        elif source_type == DofObjectHandler.ONLINE:
            self.__load_online()
        else:
            raise DofError('DofObject.load(): Unsupported handler type.')


    def load_from(self, handler_id : int, location : str, is_relative : bool):
        """
        Load internal data from local storage
        =====================================

        Parameters
        ----------
        handler_id : int
            The id of the handler.
        location : str
            Location to load from.
        is_relative : bool
            Whether the path is relative or not.

        Raises
        ------
        DofError
            If the given handler id points to a local handler that doesn't
            exist.
        DofError
            When the local handler has been deleted.
        """

        if not handler_id in self.__local_handlers:
            raise DofError('DofObject.save_to(): local handler doesn\'t exist.')
        if self.__local_handlers[handler_id] is None:
            raise DofError('DofObject.save_to(): local handler is deleted.')
        self.__data = self.__local_handlers[handler_id].load_as_instance(
                                                        location, is_relative)


    @property
    def local_handler_id(self) -> int:
        """
        Get the Id of local handler
        ===========================

        Returns
        -------
        int
            The Id of the local handler.
        """

        return self.__local_handler_id


    @local_handler_id.setter
    def local_handler_id(self, new_id : int):
        """
        Set the Id of local handler
        ===========================

        Parameters
        ----------
        new_id : int
            The new Id of the local handler.

        Raises
        ------
        DofError
            When the given id does not connect to a valid handler.

        See Also
        --------
            check all available handlers : DofObject.available_handlers()
        """

        if not DofObject.handler_exists(DofObjectHandler.LOCAL, new_id):
            raise DofError('DofFile.local_handler_id : tried to set LOCAL ' +
                           'handler id to a non existing handler.')
        self.__local_handler_id = new_id


    @property
    def local_path(self) -> str:
        """
        Get the local path of the data
        ==============================

        Returns
        -------
        str
            The local path. Empty string means no local path is added.
        """

        return self.__local_path


    @property
    def online_handler_id(self) -> int:
        """
        Get the Id of online handler
        ============================

        Returns
        -------
        int
            The Id of the online handler.
        """

        return self.__local_handler_id


    @online_handler_id.setter
    def online_handler_id(self, new_id : int):
        """
        Set the Id of online handler
        ============================

        Parameters
        ----------
        new_id : int
            The new Id of the online handler.

        Raises
        ------
        DofError
            When the given id does not connect to a valid handler.

        See Also
        --------
            check all available handlers : DofObject.available_handlers()
        """

        if not DofObject.handler_exists(DofObjectHandler.ONLINE, new_id):
            raise DofError('DofFile.online_handler_id : tried to set ONLINE ' +
                           'handler id to a non existing handler.')
        self.__online_handler_id = new_id


    @property
    def online_link(self) -> str:
        """
        Get online link of the data
        ===========================

        Returns
        -------
        str
            The online_link. Empty string means no online link is added.
        """

        return self.__online_link


    def save(self, destination_type : str = DofObjectHandler.LOCAL):
        """
        Save data to the destination
        ============================

        Parameters
        ----------
        destination_type : str, optional (DofObjectHandler.LOCAL if omitted)
            Destinaton of data.

        Raises
        ------
        DofError
            When the type of handler is not supported.

        See Also
        --------
            Constants for selecting the destination : storage.DofObjectHandler

        Notes
        -----
            Type of destination can be local or online.
        """

        if destination_type == DofObjectHandler.LOCAL:
            self.__save_local()
        elif destination_type == DofObjectHandler.ONLINE:
            self.__save_online()
        else:
            raise DofError('DofObject.save(): Unsupported handler type.')


    def save_to(self, handler_id : int, location : str, is_relative : bool):
        """
        Save internal data to local storage
        ===================================

        Parameters
        ----------
        handler_id : int
            The id of the handler.
        location : str
            Location to save to.
        is_relative : bool
            Whether the path is relative or not.

        Raises
        ------
        DofError
            If the given handler id points to a local handler that doesn't
            exist.
        DofError
            When the local handler has been deleted.
        """

        if not handler_id in self.__local_handlers:
            raise DofError('DofObject.save_to(): local handler doesn\'t exist.')
        if self.__local_handlers[handler_id] is None:
            raise DofError('DofObject.save_to(): local handler is deleted.')
        self.__local_handlers[handler_id].save_as_instance(self.__data,
                                                           location,
                                                           is_relative)


    @classmethod
    def set_default_handler(cls, handler_type : str, handler_id : int):
        """
        Set default handler id
        ======================

        Parameters
        ----------
        handler_type : str
            Type of the handler to set. Must be DofObjectHandler.LOCAL or
            DofObjectHandler.ONLINE.
        handler_id : int
            The id of the handler to set as default.

        Raises
        ------
        DofError
            If tha handler_type parameter is unknown.
        DofError
            If the given handler_id desn't exist.
        DofError
            If the handler is already deleted.
        """

        if handler_type == DofObjectHandler.LOCAL:
            if not handler_id in cls.__local_handlers.keys():
                raise DofError('DofObject.set_default_handler(): handler id {} '
                               .format(handler_id) + 'doesn\'t exist in LOCAL' +
                               ' handlers.')
            if cls.__local_handlers[handler_id] is None:
                raise DofError('DofObject.set_default_handler(): handler id {}'
                               .format(handler_id) + ' in LOCAL is already ' +
                               'deleted.')
            cls.__local_default = handler_id
        elif handler_type == DofObjectHandler.ONLINE:
            if not handler_id in cls.__online_handlers.keys():
                raise DofError('DofObject.set_default_handler(): handler id {} '
                               .format(handler_id) + 'doesn\'t exist in ' +
                               'ONLINE handlers.')
            if cls.__online_handlers[handler_id] is None:
                raise DofError('DofObject.set_default_handler(): handler id {}'
                               .format(handler_id) + ' in ONLINE is already ' +
                               'deleted.')
            cls.__online_default = handler_id
        else:
            raise DofError('DofObject.set_default_handler(): Unsupported ' +
                           'handler type.')


    def set_path(self, path_type : str, new_value : str, is_relative : bool):
        """
        Set the path for further functions
        ==================================

        Parameters
        ----------
        path_type : str
            Type of path.
        new_value : str
            Value to set the new path.
        is_relative : bool
            Whether the path is relative or not.

        Raises
        ------
        DofError
            When the type of path is not supported.

        See Also
        --------
            Constants for selecting the path : storage.DofObjectHandler

        Notes
        -----
            Type of path can be local or online.
        """

        if path_type == DofObjectHandler.LOCAL:
            self.__local_path = new_value
            self.__is_relative_local = is_relative
        elif path_type == DofObjectHandler.ONLINE:
            self.__online_link = new_value
            self.__is_relative_online = is_relative
        else:
            raise DofError('DofObject.set_path(): Unsupported path type.')


    def to_json_dict(self, describe_only : bool = True) -> dict:
        """
        Create a dictionary that is compatible to make JSON from an instance
        ====================================================================

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

        _description = []
        _description.append((JSONDescription.OBJECT_TYPE,
                             '{}.{}'.format(self.data.__class__.__module__,
                                            self.data.__class__.__name__)))
        _description.append((JSONDescription.LOCAL_PATH, self.local_path))
        _description.append((JSONDescription.LOCAL_PATH_RELATIVE,
                             self.is_relative_local))
        _description.append((JSONDescription.ONLINE_LINK, self.online_link))
        _description.append((JSONDescription.ONLINE_LINK_RELATIVE,
                             self.is_relative_online))
        _description.append((JSONDescription.REAL_BINARY, self.is_binary))
        if describe_only:
            result = create_json_dict('DofObject', 'dof.core', describe_only,
                                      description=_description)
        else:
            result = create_json_dict('DofObject', 'dof.core', describe_only,
                                      content_form=ContentForm.PICKLE_BINARY,
                                      description=_description)
            result[JSONRoot.CONTENT.value] = pickle_dumps(self).hex()
        return result


    def __load_local(self):
        """
        Load data from local source
        ===========================

        Raises
        ------
        DofError
            When the local handler does not exist.
        DofError
            When the local handler have been deleted already.
        """

        if self.__local_handler_id > -1:
            _handler = self.__local_handlers[self.__local_handler_id]
        else:
            if self.__local_handler_id not in self.__local_handlers.keys():
                raise DofError('DofObject.load(): LOCAL handler of the ' +
                               'instance doesn\'t exist.')
            if self.__local_handlers[self.__local_handler_id] is None:
                raise DofError('DofObject.load(): LOCAL handler of the ' +
                               'instance is deleted.')
            _handler = self.__local_handlers[self.__local_handler_id]
        if not self.__is_binary:
            self.__data = _handler.load_as_instance(self.__local_path,
                                                self.__is_relative_local)
        else:
            self.__data = _handler.load_as_binary(self.__local_path,
                                                self.__is_relative_local)


    def __load_online(self):
        """
        Load data from online source
        ============================

        Raises
        ------
        DofError
            When the online handler does not exist.
        DofError
            When the online handler have been deleted already.
        """
        if self.__online_handler_id > -1:
            _handler = self.__online_handlers[self.__online_handler_id]
        else:
            if self.__online_handler_id not in \
                                            self.__online_handlers.keys():
                raise DofError('DofObject.load(): ONLINE handler of the ' +
                               'instance doesn\'t exist.')
            if self.__online_handlers[self.__online_handler_id] is None:
                raise DofError('DofObject.load(): ONLINE handler of the ' +
                               'instance is deleted.')
            _handler = self.__online_handlers[self.__online_handler_id]
        if not self.__is_binary:
            self.__data = _handler.load_as_instance(self.__online_link,
                                                self.__is_relative_online)
        else:
            self.__data = _handler.load_as_binary(self.__online_link,
                                                self.__is_relative_online)


    def __save_local(self):
        """
        Save data to local destination
        ==============================
        """
        if self.__local_handler_id > -1:
            _handler = self.__local_handlers[self.__local_handler_id]
        else:
            _handler = self.__local_handlers[self.__local_default]
        if not self.__is_binary:
            _handler.save_as_instance(self.__data, self.__local_path,
                                      self.__is_relative_local)
        else:
            _handler.save_as_binary(self.__data, self.__local_path,
                                      self.__is_relative_local)


    def __save_online(self):
        """
        Save data to online destination
        ===============================
        """
        if self.__online_handler_id > -1:
            _handler = self.__online_handlers[self.__online_handler_id]
        else:
            _handler = self.__online_handlers[self.__online_default]
        if not self.__is_binary:
            _handler.save_as_instance(self.__data, self.__online_link,
                                      self.__is_relative_online)
        else:
            _handler.save_as_binary(self.__data, self.__online_link,
                                      self.__is_relative_online)


if __name__ == '__main__':
    pass
