"""
DoF - Deep Model Core Output Framework
======================================

Submodule: data
"""


# pylint: disable=too-many-lines
#           I.  Docstring and code together consumes a lot of lines of code.
#          II.  We try to keep similar or related classes in the same file.
#         III.  The working code may be under the 1000 lines limit, but we
#               think, docstring with notations is useful to anybody to
#               understand our code and the way of our thinking.


from json import dumps, loads

from .core import DofObject
from .datamodel import create_json_dict, get_content
from .datamodel import ContentForm, JSONContent, JSONDescription, JSONRoot
from .error import DofError
from .information import DataElementInfo
from .storage import DofObjectHandler, DofSerializable


class DataElement(DofSerializable):
    """
    Class to wrap dataset's data elements
    =====================================

    Attributes
    ----------
    data : any (read-only)
        Content of dataset element.
    dof_object : DofObject
        Provide direct access to the DofObject.
    element_type : str (read-only)
        The element type.
    has_info : bool (read-only)
        Whether the instance contains info or not.
    info : DataElementInfo | NoneType
        The info that is stored or None if there is no info.
    is_x : bool (read-only)
        Whether the instance is X or not.
    is_y : bool (read-only)
        Whether the instance is Y or not.
    """


    # These variables should be static class level constants but this out of the
    # capabilites of Python.
    X = 'x'
    Y = 'y'


    def __init__(self, data : DofObject, element_type : str,
                 info : DataElementInfo = None):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        data : DofObject
            Data to store.
        element_type : str
            Type of data, actually X and Y is supported.
        info : DataElementInfo, optional (None if omitted)
            Information to store with the data element, or None if there is no
            unique info that belongs only to this element.

        Raises
        ------
        DofError
            When the value of element_type is not supported.
        DofError
            When info is not None or the type of info is not DataElementInfo.

        Notes
        -----
        I.
            Type of info is noted as any due to avoid import typing library.
            When Python can handle union notation without any import, it will be
            updated. Since this parameter is not mandatory, the value can be
            None or DataElementInfo. DofError is raised when the type of info
            is not DataElementInfo or None.
        II.
            However, the typing of data shows the function wants to get data as
            an instance of DofObject, the init try to handle the case when the
            data is not DofObject. This means the init try to create the desired
            DofObject from the given data. This approach provides more
            flexibilty and usability than raising an error.
        """

        if isinstance(data, DofObject):
            self.__data = data
        else:
            self.__data = DofObject(data)
        if element_type in [DataElement.X, DataElement.Y]:
            self.__element_type = element_type
        else:
            raise DofError('DataElement.init(): invalid element type "{}"'
                           .format(element_type))
        if info is None:
            self.__info = info
        if isinstance(info, DataElementInfo):
            self.__info = info
        else:
            raise DofError('DataElement.init(): type of info must be ' +
                           'DataElementInfo and not {}'.format(type(info)))


    @property
    def data(self) -> any:
        """
        Return the data of the instance
        ===============================

        Returns
        -------
        any
            The data that is stored.
        """

        return self.__data.data


    def del_info(self):
        """
        Delete the info of the instance
        ===============================
        """

        self.__info = None


    @property
    def dof_object(self) -> DofObject:
        """
        Provide direct access to the DofObject
        ======================================

        Returns
        -------
        DofObject
            The DofObject that wraps the data.
        """

        return self.__data


    @property
    def element_type(self) -> str:
        """
        Return the element type of the instance
        =======================================

        Returns
        -------
        str
            The element type.
        """

        return self.__element_type


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
        any
            The object that is created.

        Raises
        ------
        DofError
            When the given data is empty.
        DofError
            When there is no description value in the given JSON.
        DofError
            When there is no valid element info available in the given JSON.
        DofError
            When there is no valid element type available in the given JSON.
        DofError
            When the element type is not valid.

        See Also
        --------
            Valid values to element info and type : class DataElement

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'DataElement', 'dof.data',
                           describe_only=False)
        if data is None:
            raise DofError('DataElement.from_json(): JSON string is not valid' +
                           ' to create an instance.')
        if JSONRoot.DESCRIPTION.value not in json_dict.keys():
            raise DofError('DataElement.from_json(): JSON string is not ' +
                           'complete, without description restore is not ' +
                           'available.')
        _description = json_dict[JSONRoot.DESCRIPTION.value]
        if JSONDescription.ELEMENT_INFO.value not in _description.keys():
            raise DofError('DataElement.from_json(): JSON string is not ' +
                           'complete, without element info restore is not ' +
                           'available.')
        if JSONDescription.ELEMENT_TYPE.value not in _description.keys():
            raise DofError('DataElement.from_json(): JSON string is not ' +
                           'complete, without element type restore is not ' +
                           'available.')
        _element_info = _description[JSONDescription.ELEMENT_INFO.value]
        if _element_info is not None:
            _element_info = DataElementInfo.from_json(dumps(_element_info))
        _element_type = _description[JSONDescription.ELEMENT_TYPE.value]
        if _element_type not in [DataElement.X, DataElement.Y]:
            raise DofError('DataElement.from_json(): JSON string contains ' +
                           'invalid element type restore is not available.')
        _dof_object = DofObject.from_json(dumps(data))
        return DataElement(_dof_object, _element_type, _element_info)


    @property
    def has_info(self) -> bool:
        """
        Return whether the instance has info or not
        ===========================================

        Returns
        -------
        bool
            True if the instance has info, False if don't.
        """

        return self.__info is not None


    @property
    def info(self) -> any:
        """
        Return the info of the instance
        ===============================

        Returns
        -------
        DataElementInfo | NoneType
            The info that is stored or None if there is no info.

        Notes
        -----
            Type of info is noted as any due to avoid import typing library.
            When Python can handle union notation without any import, it will be
            updated.
        """

        return self.__info


    @info.setter
    def info(self, new_info: DataElementInfo):
        """
        Set the info of the instance
        ============================

        Parameters
        ----------
        DataElementInfo
            The info to set to the element.
        """

        self.__info = new_info


    @property
    def is_x(self) -> bool:
        """
        Return whether the instance is X or not
        =======================================

        Returns
        -------
        bool
            True if the instance as an X element, False if don't.
        """

        return self.__element_type == DataElement.X


    @property
    def is_y(self) -> bool:
        """
        Return whether the instance is Y or not
        =======================================

        Returns
        -------
        bool
            True if the instance as an Y element, False if don't.
        """

        return self.__element_type == DataElement.Y


    def to_info(self) -> dict:
        """
        Transforms information into dict
        ================================

        Returns
        -------
        dict
            Dictionary of information.
        """
        result = {}
        result[JSONDescription.ELEMENT_TYPE.value] = self.element_type
        if self.has_info:
            result[JSONDescription.ELEMENT_INFO.value] = \
                                    self.info.to_json_dict(describe_only=False)
        return result



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
            Dict that is compatible to create a JSON formatted string.

        Notes
        -----
        I.
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        II.
            If there is no element_info, the related result value is None.
        """

        _description = []
        _description.append((JSONDescription.ELEMENT_TYPE, self.element_type))
        if self.has_info:
            _description.append((JSONDescription.ELEMENT_INFO,
                                 self.info.to_json_dict(describe_only)))
        else:
            _description.append((JSONDescription.ELEMENT_INFO, None))
        if describe_only:
            result = create_json_dict('DataElement', 'dof.data', describe_only,
                                      description=_description)
        else:
            result = create_json_dict('DataElement', 'dof.data', describe_only,
                                      content_form=ContentForm.INSTANCE,
                                      description=_description)
            result[JSONRoot.CONTENT.value] = self.dof_object.to_json_dict(
                                                                describe_only)
        return result


    def __call__(self) -> any:
        """
        Return the data of the instance
        ===============================

        Returns
        -------
        any
            The data that is stored.
        """

        return self.__data.data


class LinkEngine(DofSerializable):
    """
    Class to maintain connections between dataset elements
    ======================================================

    Attributes
    ----------
    links : list (read-only)
        All links between any X and Y values.

    Notes
    -----
        Use len() function for getting the number of links.
    """

    def __init__(self):
        """
        Initialize an instance of the object
        ====================================
        """

        self.__links = []
        self.__at = 0


    def count_all(self, id_to_count : int) -> int:
        """
        Count all connections of an id
        ==============================

        Parameters
        ----------
        id_to_count : int
            The id to count connections.

        Returns
        -------
        int
            Number of connections to the related id.
        """

        result = 0
        for row in self.__links:
            if row[0] == id_to_count:
                result += 1
            elif row[1] == id_to_count:
                result += 1
        return result


    def count_x(self, id_to_count : int) -> int:
        """
        Count all connections where id is in position as X
        ==================================================

        Parameters
        ----------
        id_to_count : int
            The id to count connections in position as X.

        Returns
        -------
        int
            Number of connections to the related id in X position.
        """

        result = 0
        for row in self.__links:
            if row[0] == id_to_count:
                result += 1
        return result


    def count_y(self, id_to_count : int) -> int:
        """
        Count all connections where id is in position as Y
        ==================================================

        Parameters
        ----------
        id_to_count : int
            The id to count connections in position as Y.

        Returns
        -------
        int
            Number of connections to the related id in Y position.
        """

        result = 0
        for row in self.__links:
            if row[1] == id_to_count:
                result += 1
        return result


    def delink(self, id_x : int, id_y : int):
        """
        Remove the connection between specified X and Y
        ===============================================

        Parameters
        ----------
        id_x : int
            Id of X for dropping the connection.

        id_y : int
            Id of Y for dropping the connection.

        Raises
        ------
        DofError
            Connection can be removed only when there is an existing link
            between the given ids of X and Y.
        """

        for i in range(len(self.__links)):
            if self.__links[i][0] == id_x:
                if self.__links[i][1] == id_y:
                    del self.__links[i]
                    return
        raise DofError('LinkEngine.delink(): nothing to delete at given X, Y' +
                       ': "{}"->"{}".'.format(id_x, id_y))


    def delink_all(self, id_to_delink : int):
        """
        Remove all connections between any X and Y that fits for the given id
        =====================================================================

        Parameters
        ----------
        id_to_delink : int
            Id of X or Y for dropping the connection.

        Raises
        ------
        DofError
            Connection can be removed only when there is an existing link
            between the given ids of X or Y.
        """

        indexes = []
        for i in range(len(self.__links)):
            if self.__links[i][0] == id_to_delink:
                indexes.append(i)
            elif self.__links[i][1] == id_to_delink:
                indexes.append(i)
        indexes.reverse()
        for i in indexes:
            del self.__links[i]
        if len(indexes) == 0:
            raise DofError('LinkEngine.delink_all(): nothing to delete at ' +
                           'given id "{}".'.format(id_to_delink))


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
        any
            The object that is created.

        Raises
        ------
        DofError
            When the given data is empty.
        DofError
            When there is no valid list instance in the given JSON.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'LinkEngine', 'dof.data',
                           describe_only=False)
        if data is None:
            raise DofError('LinkEngine.from_json(): JSON string is not valid' +
                           ' to create an instance.')
        if not isinstance(data, list):
            raise DofError('LinkEngine.from_json(): JSON string has invalid ' +
                           'content instance.')
        result = LinkEngine()
        for _x, _y in data:
            result.link(_x, _y)
        return result


    def get_link(self, id_to_get : int) -> list:
        """
        Return the list of ids of X and Y value pairs that fit for the given id
        =======================================================================

        Parameters
        ----------
        id_to_get : int
            Id of both X or Y values to find a connection.

        Returns
        -------
        int
            List of ids of X and Y value pairs that meet with the given id.

        Raises
        ------
        DofError
            When there is no linked X or Y value.
        """

        result = []
        for row in self.__links:
            if row[0] == id_to_get:
                result.append(row)
            elif row[1] == id_to_get:
                result.append(row)
        if len(result) == 0:
            raise DofError('LinkEngine.get_link(): given id ' +
                           '"{}" is not linked in X or Y positions.'
                           .format(id_to_get))
        return result


    def get_link_by_x(self, id_to_get : int) -> int:
        """
        Return the id of the linked Y value to the given X
        ==================================================

        Parameters
        ----------
        id_to_get : int
            Id of the X value.

        Returns
        -------
        int
            Id of the linked Y value.

        Raises
        ------
        DofError
            When there is no linked Y value to given X.
        """

        for row in self.__links:
            if row[0] == id_to_get:
                return row[1]
        raise DofError('LinkEngine.get_link_by_x(): the given id ' +
                       '"{}" is not linked as X.'.format(id_to_get))


    def get_link_by_y(self, id_to_get : int) -> int:
        """
        Return the id of the linked X value to the given Y
        ==================================================

        Parameters
        ----------
        id_to_get : int
            Id of the Y value.

        Returns
        -------
        int
            Id of the linked X value.

        Raises
        ------
        DofError
            When there is no linked X value to given Y.
        """

        for row in self.__links:
            if row[1] == id_to_get:
                return row[0]
        raise DofError('LinkEngine.get_link_by_y(): the given id ' +
                       '"{}" is not linked as Y.'.format(id_to_get))


    def has_link(self, id_to_check : int) -> int:
        """
        Get whether an id is connected or not
        =====================================

        Parameters
        ----------
        id_to_check : int
            Id to check if it is in any connection or not.

        Returns
        -------
        bool
            True if the given id is connected, False if not.
        """

        for row in self.__links:
            if id_to_check in row:
                return True
        return False


    def has_link_as_x(self, id_to_check : int) -> bool:
        """
        Get whether an id is connected in X position or not
        ===================================================

        Parameters
        ----------
        id_to_check : int
            Id to check if it is in any connection as X or not.

        Returns
        -------
        bool
            True if the given id is connected as X, False if not.
        """

        for row in self.__links:
            if row[0] == id_to_check:
                return True
        return False


    def has_link_as_y(self, id_to_check : int) -> bool:
        """
        Get whether an id is connected in Y position or not
        ===================================================

        Parameters
        ----------
        id_to_check : int
            Id to check if it is in any connection as Y or not.

        Returns
        -------
        bool
            True if the given id is connected as Y, False if not.
        """

        for row in self.__links:
            if row[1] == id_to_check:
                return True
        return False


    def link(self, id_x : int, id_y : int):
        """
        Connect X and Y together
        ========================

        Parameters
        ----------
        id_x : int
            The X parameter to connect.
        id_y : int
            The Y parameter to connect.

        Raises
        ------
        DofError
            If the X and Y parameters have been connected.
        """

        for row in self.__links:
            if row[0] == id_x:
                if row[1] == id_y:
                    raise DofError('LinkEngine.link(): given combination of ' +
                                   'X and Y already exists: "{}"->"{}"'
                                   .format(id_x, id_y))
        self.__links.append((id_x, id_y))


    @property
    def links(self) -> list:
        """
        Return all links
        ================

        Returns
        -------
        list
            Copy of the list of all links.

        Notes
        -----
            This property doesn't provide direct access to the inside list of
            links, it is just a copy of it. If any change is made, it has
            no effect to the instance.
        """

        return self.__links[:]


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
        _description.append((JSONDescription.LINKS_COUNT, len(self.__links)))
        if describe_only:
            result = create_json_dict('DataElement', 'dof.data', describe_only,
                                      description=_description)
        else:
            result = create_json_dict('DataElement', 'dof.data', describe_only,
                                      content_form=ContentForm.TEXTUAL,
                                      description=_description)
            result[JSONRoot.CONTENT.value] = self.links
        return result


    def __getitem__(self, id_to_get : any) -> any:
        """
        Get an item from the conncetions
        ================================

        Parameters
        ----------
        id_to_get : int | slice | tuple
            The identifier(s) of the connection(s) to get.

        Returns
        -------
        tuple(int, int) | list[tuple(int, int)]
            The id pair that is connected or list of id pairs that are
            connected.

        See Also
        --------
            Get everything about connections : DofFile.__getitem()
            Get connected elements : functional.Dataset.__getitem__()
        """

        return self.__links[id_to_get]


    def  __iter__(self) -> any:
        """
        Return iterator
        ===============

        Returns
        -------
        Iterator
            The iterator object connected to the links.
        """

        return self


    def __len__(self) -> int:
        """
        Get the count of all connections
        ================================

        Returns
        -------
        int
            Count of all connections.
        """

        return len(self.__links)


    def __next__(self) -> tuple:
        """
        Perform next on the conncetions
        ===============================

        Returns
        -------
        tuple(int, int)
            Pair of ids connected together.

        Raises
        ------
        StopIteration
            If iteration is finished.

        See Also
        --------
            Iterate over every information : DofFile.__next__()
            Iterate over elements : functional.Dataset.__next__()

        Notes
        -----
            The raise of StopIteration is the canonical way to well implement
            iteration. It doesn't stops the run of the code.
        """

        _at = self.__at
        self.__at += 1
        if self.__at == len(self.__links):
            self.__at = 0
            raise StopIteration
        return self.__links[_at]


class Dataset(DofSerializable):
    """
    Class to maintain dataset in a DoF file
    =======================================

    Attributes
    ----------
    as_dataset : list (read-only)
        Get the whole dataset with connections between X and Y values as
        elements of list.
    is_dof : bool
        Whether the dataset is a pre-trained model output or not.
    linker : LinkEngine (read-only)
        Provide direct access to the linker engine of the instance.
    next_available_id : int (read-only)
        The next available id.
    x_datalist : list (read-only)
        Get each X data as list.
    x_elements : list (read-only)
        Get each X as elements of list.
    y_datalist : list (read-only)
        Get each Y data as list.
    y_elements : list (read-only)
        Get each Y as elements of list.
    """

    # pylint: disable=too-many-public-methods
    #         The amount of public methods is needed due to the functionality.

    def __init__(self, elements : list = [], linker_engine : any = None,
                 links : list = [], is_dof : bool = True):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        elements : list, optional (empty list if ommited)
            Elements to add.
        links : list, optional (empty list if ommited)
            Connections between elements.
        linker_engine : LinkEngine, optional (None if omitted)
            Engine that makes connections between elements.
        is_dof : bool, optional (True if omitted)
            Whether the dataset is a pre-trained model output or not.

        Raises
        ------
        DofError
            When linker_engine is not None or the type of linker_engine is not
            DataElementInfo.

        See Also
        --------
            add elements : add_elements()

        Notes
        -----
        I.
            Type of linker_engine is noted as any due to avoid import typing
            library. When Python can handle union notation without any import,
            it will be updated. Since this parameter is not mandatory, the value
            can be None or LinkEngine. DofError is raised when the type of info
            is not LinkEngine or None.
        II.
            If is_dof is set to False, it means that the dataset is raw dataset
            not a pre-trained model output e.g. the output comes from a
            headless pre-trained model. The use of that kind of data is somewhat
            against the original goals of DoF but the flexibility of the
            framework allows that kind of use too.
        III.
            The proper use of is_dof is mandatory because the treatment of raw
            or non-raw data can be significantly different.
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        self.__elements = {}
        self.__at = 0
        if linker_engine is not None:
            if not isinstance(linker_engine, LinkEngine):
                raise DofError('Dataset.init(): linker_engine must be ' +
                               'instance (or subclass) of LinkEngine, but it ' +
                               'is "{}".'.format(type(linker_engine)))
            self.__linker = linker_engine
        else:
            self.__linker = LinkEngine()
        if len(elements) > 0:
            self.add_elements(elements, links)
        self.__is_dof = is_dof


    def add_element(self, element : DataElement, link : any = None) -> int:
        """
        Add element to the dataset
        ==========================

        Parameters
        ----------
        element : DataElement
            Element to add.
        link : int, list, optional (None if omitted)
            Information to linker, int if one-to-one linker is used, list if
            one-to-many linker is used, or None if no linking information
            is added.

        Returns
        -------
        int
            The id of the added element.

        Raises
        ------
        DofError
            When type of element is not DataElement.

        Notes
        -----
            Type of element is noted as any due to avoid import typing library.
            When Python can handle union notation without any import, it will be
            updated. Since this parameter is not mandatory, the value can be
            None or DataElement. DofError is raised when the type of info is
            not DataElement.
        """

        if not isinstance(element, DataElement):
            raise DofError('Dataset.add_element(): element must be instance'
                           + ' of DataElement but is instance of {}.'
                           .format(type(element)))
        _id = len(self.__elements)
        self.__elements[_id] = element
        if link is not None:
            self.__linker.link(_id, link)
        return _id


    def add_elements(self, elements : list, links : list = []) -> list:
        """
        Add multiple elements to the dataset
        ====================================

        Parameters
        ----------
        elements : list
            Elements to add.
        links : list, optional (empty list if ommited)
            Connections between elements.

        Returns
        -------
        list[int]
            List of ids of the added elements.

        Raises
        ------
        DofError
            There is an empty list for adding elements.
        DofError
            It occurs when the number of elements does not equal with the number
            links.
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        _links = []
        if len(elements) == 0:
            raise DofError('Dataset.add_elements(): nothing to add.')
        if len(links) > 0:
            if len(elements) != len(links):
                raise DofError('Dataset.add_elements(): length of ' +
                               'elements and length of links must match ' +
                               'but they are different: {}<->{}'
                               .format(len(elements), len(links)))
            _links = links
        else:
            _links = [None for x in range(len(elements))]
        result = []
        for element, link in zip(elements, _links):
            result.append(self.add_element(element, link))
        return result


    @property
    def as_dataset(self) -> list:
        """
        Get the whole dataset in x -> y form
        ====================================

        Returns
        -------
        list[tuple[DataElement, DataElement]]
            List of connected elements.
        """

        result = []
        for _x, _y in self.__linker:
            result.append((self.__elements[_x], self.__elements[_y]))
        return result


    def count_all(self) -> int:
        """
        Get count of all elements in the dataset
        ========================================

        Returns
        -------
        int
            The number of the existing elements in the dataset.
        """

        count = 0
        for element in self.__elements:
            if element is not None:
                count += 1
        return count


    def count_x(self) -> int:
        """
        Get count of all X elements in the dataset
        ==========================================

        Returns
        -------
        int
            The number of the existing X elements in the dataset.
        """

        count = 0
        for element in self.__elements:
            if element is not None:
                if element.is_x:
                    count += 1
        return count


    def count_y(self) -> int:
        """
        Get count of all X elements in the dataset
        ==========================================

        Returns
        -------
        int
            The number of the existing X elements in the dataset.
        """

        count = 0
        for element in self.__elements:
            if element is not None:
                if element.is_y:
                    count += 1
        return count


    def delete(self, id_to_delete : int):
        """
        Delete existing element from the dataset
        ========================================

        Parameters
        ----------
        id_to_delete : int
            The id of the element to delete.

        Raises
        ------
        DofError
            When tried to delete an element that have been deleted.
        DofError
            When tried to delete a non-existing id.

        Notes
        -----
            Every id is unique in the dataset. If you delete an element with an
            id, the id gets repealed permanently.
        """

        if id_to_delete in self.__elements.keys():
            if self.__elements[id_to_delete] is not None:
                self.__elements[id_to_delete] = None
                self.__linker.delink_all(id_to_delete)
            else:
                raise DofError('Dataset.delete(): tried to delete an ' +
                               'element id "{}" that is already deleted.'
                               .format(id_to_delete))
        else:
            raise DofError('Dataset.delete(): tried to delete a ' +
                           'non-existing id "{}".'.format(id_to_delete))


    def describe(self) -> dict:
        """
        Describe the dataset
        ====================

        Returns
        -------
        dict
            Descriptive information about the dataset in key, value form.

        Notes
        -----
            len = length of the whole dataset that is equals with the number of
                  all connection
            count_all = count of all elements in the dataset
            count_x = number of the X values in the dataset
            count_y = number of the Y values in the dataset
        """

        result = {}
        result['len'] = len(self)
        result['count_all'],  result['count_x'], result['count_y'] \
              = self.count_elements_()
        return result


    def force_load_to_memory(self) -> bool:
        """
        Load data to memory if possible
        ===============================

        Returns
        -------
        bool
            True if data get loaded into the memory, False if not.
        """

        return all(e.dof_object.force_load_to_memory() for e in self.__elements)


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
        any
            The object that is created.

        Raises
        ------
        DofError
            When the given data is empty.
        DofError
            When there is no description value in the given JSON.
        DofError
            When the value of is_dof is not valid in the given JSON.
        DofError
            When the value of next_id is not valid in the given JSON.
        DofError
            When there are no links in the given JSON.
        DofError
            When there are no elements in the given JSON.
        DofError
            When elements information has invalid content in the given JSON.
        DofError
            Length of elements must be lower or equal than the value of next id.
        DofError
            There is an inner error connected to the list of elements.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'Dataset', 'dof.data',
                           describe_only=False)
        if data is None:
            raise DofError('Dataset.from_json(): JSON string is not valid ' +
                           'to create an instance.')
        if JSONRoot.DESCRIPTION.value not in json_dict.keys():
            raise DofError('Dataset.from_json(): JSON string is not complete' +
                           ', without description restore is not available.')
        _description = json_dict[JSONRoot.DESCRIPTION.value]
        if JSONDescription.IS_DOF.value not in _description.keys():
            raise DofError('Dataset.from_json(): JSON string is not complete' +
                           ', without is_dof state restore is not available.')
        if JSONDescription.NEXT_ID.value not in _description.keys():
            raise DofError('Dataset.from_json(): JSON string is not complete' +
                           ', without the next id restore is not available.')
        _is_dof = _description[JSONDescription.IS_DOF.value]
        _total_len = _description[JSONDescription.NEXT_ID.value]
        if JSONContent.LINKS.value not in data.keys():
            raise DofError('Dataset.from_json(): JSON string\'s content ' +
                           'doesn\'t include links, restore is not available.')
        if JSONContent.ELEMENTS.value not in data.keys():
            raise DofError('Dataset.from_json(): JSON string\'s content ' +
                           'doesn\'t include elements, restore is not ' +
                           'available.')
        _link_engine = LinkEngine.from_json(dumps(
                                            data[JSONContent.LINKS.value]))
        _elements = data[JSONContent.ELEMENTS.value]
        if not isinstance(_elements, dict):
            raise DofError('Dataset.from_json(): JSON string contains bad ' +
                           'elements information restore is not available.')
        if sorted(_elements.keys())[-1] > _total_len:
            raise DofError('Dataset.from_json(): there are elements with ' +
                           'a higher id in the JSON string then the maximum ' +
                           'of id\'s.')
        result = Dataset(linker_engine=_link_engine, is_dof=_is_dof)
        for i in range(_total_len):
            if i in _elements.keys():
                result.add_element(_elements[i])
            else:
                _i = result.add_element(DataElement('', DataElement.X))
                if _i != i:
                    raise DofError('Dataset.from_json(): ambigous elements in' +
                                   'JSON string restore is not available.')
                result.delete(_i)
        return result


    def get_element_by_id(self, id_to_get : int) -> DataElement:
        """
        Get an element by id
        ====================

        Parameters
        ----------
        id_to_get : int
            Id for getting a specified data elemet from the dataset.

        Returns
        -------
        DofDataElement
            The element itself.

        Raises
        ------
        DofError
            When tried to get an element that is never existed.
        DofError
            When tried to get an element that have been deleted.
        """

        if id_to_get not in self.__elements.keys():
            raise DofError('Dataset.get_element_by_id(): tried to get ' +
                           'an element by id "{}", that never existed.'
                           .format(id_to_get))
        if self.__elements[id_to_get] is None:
            raise DofError('Dataset.get_element_by_id(): tried to get ' +
                           'a deleted element by id "{}".'.format(id_to_get))
        return self.__elements[id_to_get]


    def get_element_by_info(self, key : str, value : str) -> list:
        """
        Get an element by info
        ======================

        Parameters
        ----------
        key : str
            Key to search for.
        value : str
            Value to search for.

        Returns
        -------
        list[DataElement]
            List of DataElement object that has info with the given
            parameters.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].has_info:
                    if self.__elements[_id].info.has_key(key):
                        if self.__elements[_id].info[key] == value:
                            result.append(self.__elements[_id])
        return result


    def get_everything_by_id(self, id_to_get : int) -> tuple:
        """
        Get an element and the additional information and links by id
        =============================================================

        Parameters
        ----------
        id_to_get : int
            Id for getting a specified data elemet and its additional
            information and links from the dataset.

        Returns
        -------
        tuple(DataElement, list | None)
            The element itself with its additional information and links. When
            there is no link, tuple[1] is None.

        Raises
        ------
        DofError
            When tried to get an element that is never existed.
        DofError
            When tried to get an element that have been deleted.
        """

        if id_to_get not in self.__elements.keys():
            raise DofError('Dataset.get_element_by_id(): tried to get ' +
                           'an element by id "{}", that never existed.'
                           .format(id_to_get))
        if self.__elements[id_to_get] is None:
            raise DofError('Dataset.get_element_by_id(): tried to get ' +
                           'a deleted element by id "{}".'.format(id_to_get))
        return (self.__elements[id_to_get], self.__linker.get_link(id_to_get))


    def get_everything_by_info(self, key : str, value : str) -> list:
        """
        Get an element and the additional information and links by info
        ===============================================================

        Parameters
        ----------
        key : str
            Key to search for.
        value : str
            Value to search for.

        Returns
        -------
        list[tuple(DataElement, list | None)]
            List of tuples from where any tuple contatains DataElement object
            and list of links it has been found. When there is no link
            information available, tuple[1] is None.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].has_info:
                    if self.__elements[_id].info.has_key(key):
                        if self.__elements[_id].info[key] == value:
                            result.append((self.__elements[_id],
                                           self.__linker.get_link(_id)))
        return result


    @property
    def is_dof(self) -> bool:
        """
        Get whether the dataset is a pre-trained model output or not
        ============================================================

        Returns
        -------
        bool
            True if the dataset is the result of a pre-trained model output,
            False if not.
        """

        return self.__is_dof

    @is_dof.setter
    def is_dof(self, new_value : bool):
        """
        Set the value of is_dof
        =======================

        Parameters
        ----------
        new_value : bool
            The new state of the dataset's output source.

        See Also
        --------
            meaning of is_dof : class Dataset
        """

        self.__is_dof = new_value


    @property
    def linker(self) -> LinkEngine:
        """
        Provide direct access to the linker engine of the instance
        ==========================================================

        Returns:
        LinkEngine
            The linker engine.
        """

        return self.__linker


    def load_from(self, handler_id : int):
        """
        Load dataset from the working directory of DofFile
        ==================================================

        Parameters
        ==========
        handler_id : int
            Id of a local handler to use.

        Raises
        ------
        DofError
            If the dataset is not empty.
        DofError
            If there is no is_dof data field in the dataset.base file.
        DofError
            If there is no max_id data field in the dataset.base file.
        DofError
            If the data in dataset.info file does not contain required fields.
        DofError
            If there is no element_type data field in the dataset.info file.
        """

        if len(self.__elements) > 0:
            raise DofError('Dataset.load_from(): only empty dataset can be ' +
                           'filled with this method.')
        _handler = DofObject.get_handler(DofObjectHandler.LOCAL, handler_id)
        _dataset_base = _handler.load_as_instance('dataset.base')
        _is_dof = _dataset_base.get(JSONDescription.IS_DOF.value)
        if _is_dof is None:
            raise DofError('Dataset.load_from(): dataset.base is invalid, ' +
                           'it doesn\'t contain is_dof data.')
        self.__is_dof = _is_dof
        _next_id = _dataset_base.get(JSONDescription.NEXT_ID.value)
        if _next_id is None:
            raise DofError('Dataset.load_from(): dataset.base is invalid, ' +
                           'it doesn\'t contain next_id data.')
        _element_info = _handler.load_as_instance('elements.info')
        for i in range(_next_id):
            _filename = '{}.obj'.format(i)
            if _handler.exist(_filename):
                _data = _handler.load_as_instance(_filename)
                _info_dict = _element_info.get(i)
                if _info_dict is None:
                    raise DofError('Dataset.load_from(): dataset element.info' +
                                   ' contains bad data.')
                _element_type = _info_dict.get(
                                            JSONDescription.ELEMENT_TYPE.value)
                if _element_type is None:
                    raise DofError('Dataset.load_from(): dataset missing ' +
                                   'element type data in element.info.')
                _info = _info_dict.get(JSONDescription.ELEMENT_INFO.value)
                if _info is not None:
                    _info = DataElementInfo.from_json(dumps(_info))
                self.__elements[i] = DataElement(_data, _element_type, _info)
            else:
                self.__elements[i] = None
        _linker_dict = _handler.load_as_instance('elements.links')
        self.__linker = LinkEngine.from_json(dumps(_linker_dict))


    @property
    def next_available_id(self) -> int:
        """
        Get next available id
        =====================

        Returns
        int
            The identifier of the next element if added.
        """

        return len(self.__elements)


    def save_to(self, handler_id : int):
        """
        Save dataset to the working directory of DofFile
        ================================================

        Parameters
        ==========
        handler_id : int
            Id of a local handler to use.
        """

        _element_info = {}
        for i, element in self.__elements.items():
            element.dof_object.save_to(handler_id, '{}.obj'.format(i))
            _element_info[i] = element.to_info()
        _handler = DofObject.get_handler(DofObjectHandler.LOCAL, handler_id)
        _handler.save_as_instance(_element_info, 'elements.info')
        _dataset_base = {}
        _dataset_base[JSONDescription.IS_DOF.value] = self.is_dof
        _dataset_base[JSONDescription.NEXT_ID.value] = self.next_available_id
        _handler.save_as_instance(_dataset_base, 'dataset.base')
        _linker = self.__linker.to_json_dict(describe_only=False)
        _handler.save_as_instance(_linker, 'elements.links')


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
        I.
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        II.
            If there is no valid element key, the related result value is None.
        """

        _description = []
        _count, _x_count, _y_count = self.count_elements_()
        _description.append((JSONDescription.ELEMENTS_COUNT, _count))
        _description.append((JSONDescription.X_ELEMENTS_COUNT, _x_count))
        _description.append((JSONDescription.Y_ELEMENTS_COUNT, _y_count))
        _description.append((JSONDescription.LINKS_COUNT, len(self.linker)))
        _description.append((JSONDescription.IS_DOF, self.is_dof))
        _description.append((JSONDescription.NEXT_ID, self.next_available_id))
        if describe_only:
            result = create_json_dict('Dataset', 'dof.data', describe_only,
                                      description=_description)
        else:
            result = create_json_dict('Dataset', 'dof.data', describe_only,
                                      content_form=
                                      ContentForm.MULTIPLE_INSTANCES,
                                      description=_description)
            _content = {}
            _content[JSONContent.LINKS.value] = self.linker.to_json_dict(
                                                                describe_only)
            _elements = {}
            for key in sorted(self.__elements.keys()):
                if self.__elements[key] is not None:
                    _elements[key] = self.__elements[key].to_json_dict(
                                                                describe_only)
            _content[JSONContent.ELEMENTS.value] = _elements
            result[JSONRoot.CONTENT.value] = _content
        return result


    @property
    def x_datalist(self) -> list:
        """
        Get each X data as list
        =======================

        Returns:
        list[any]
            All X data.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].is_x:
                    result.append(self.__elements[_id].data)
        return result


    @property
    def y_datalist(self) -> list:
        """
        Get each Y data as list
        =======================

        Returns:
        list[any]
            All Y data.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].is_y:
                    result.append(self.__elements[_id].data)
        return result


    @property
    def x_elements(self) -> list:
        """
        Get all elements that are X
        ===========================

        Returns:
        list[DataElement]
            Elements that are X elements.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].is_x:
                    result.append(self.__elements[_id])
        return result


    @property
    def y_elements(self) -> list:
        """
        Get all elements that are Y
        ===========================

        Returns:
        list[DataElement]
            Elements that are Y elements.
        """

        result = []
        for _id in sorted(self.__elements.keys()):
            if self.__elements[_id] is not None:
                if self.__elements[_id].is_y:
                    result.append(self.__elements[_id])
        return result


    def count_elements_(self) -> tuple:
        """
        Get count of elements in the dataset from more aspects
        ======================================================

        Returns
        -------
        tuple(int, int, int)
            A tuple with the number of the existing elements, X and Y elements
            in the dataset.

        Notes
        -----
            If only one of those counts is needed only, it is suggested to use
            count_all(), count_x() or count_y() respectively.
        """

        count, count_x, count_y = 0, 0, 0
        for element in self.__elements:
            if element is not None:
                count += 1
                if element.is_x:
                    count_x += 1
                if element.is_y:
                    count_y += 1
        return (count, count_x, count_y)


    def __getitem__(self, id_to_get : int) -> any:
        """
        Get an item from the dataset
        =============================

        Parameters
        ----------
        id_to_get : int | slice | tuple
            The identifier(s) of the connection(s) to get the connected
            elements.

        Returns
        -------
        tuple(any, any) | list[tuple(any, any)]
            The pair of the connected dataset elements or list of pairs of
            connected dataset elements.

        See Also
        --------
            Get everything about connections : DofFile.__getitem()
            Get the id of the connected elements :
                functional.LinkEngine.__getitem__()
        """

        if isinstance(id_to_get, int):
            _x, _y = self.__linker[id_to_get]
            result = (self.__elements[_x].data, self.__elements[_y].data)
        else:
            result = []
            for _x, _y in self.__linker[id_to_get]:
                result.append((self.__elements[_x].data,
                               self.__elements[_y].data))
        return result


    def __iter__(self) -> any:
        """
        Return iterator
        ===============

        Returns
        -------
        Iterator
            The iterator object connected to the dataset.
        """

        return self


    def __len__(self) -> int:
        """
        Get the length of the dataset
        =============================

        Returns
        -------
        int
            Count of connected X->Y pairs.

        See Also
        --------
            Get back the number of Xs and Ys : describe()

        Notes
        -----
            Length of dataset equals with the count of all connections in the
            dataset since only the connected Xs and Ys can be used for training
            or validating purposes. If you want to get back the number of X and
            Y values, use describe() function.
        """

        return len(self.__linker)


    def __next__(self) -> tuple:
        """
        Perform next on the dataset
        ===========================

        Returns
        -------
        tuple(any, any)
            The pair of the connected dataset elements.

        Raises
        ------
        StopIteration
            If iteration is finished.

        See Also
        --------
            Iterate over every information : DofFile.__next__()
            Iterate over ids : functional.LinkEngine.__next__()

        Notes
        -----
        I.
            The raise of StopIteration is the canonical way to well implement
            iteration. It doesn't stops the run of the code.
        II.
            Dataset and linker engine have separate iteration it is recommended
            not to mix the call of them in the same loop.
        """

        _at = self.__at
        self.__at += 1
        if self.__at == len(self.__linker):
            self.__at = 0
            raise StopIteration
        _x, _y = self.__linker[_at]
        return (self.__elements[_x].data, self.__elements[_y].data)


if __name__ == '__main__':
    pass
