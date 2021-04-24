"""
DoF - Deep Model Core Output Framework
======================================

Submodule: information
"""


# pylint: disable=too-many-lines
#           I.  Docstring and code together consumes a lot of lines of code.
#          II.  We try to keep similar or related classes in the same file.
#         III.  The working code may be under the 1000 lines limit, but we
#               think, docstring with notations is useful to anybody to
#               understand our code and the way of our thinking.


from json import dumps, loads

from .core import DofObject
from .datamodel import ContentForm, JSONContent, JSONDescription, JSONRoot
from .datamodel import create_json_dict, get_content
from .error import DofError
from .storage import DofSerializable


class Information(dict, DofSerializable):
    """
    Base class for information classes
    ==================================
    """

    def __init__(self, initial_values : list):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]

        Raises
        ------
        DofError
            When the type of key is not string.
        DofError
            When the type of value is not string.
        DofError
            When tried to add the same key value twice.
        """

        super().__init__()
        for key, value in initial_values:
            if not isinstance(key, str):
                raise DofError('{}.init(): key of an info '
                               .format(self.__class__.__name__) +
                               'must be instance of str but is "{}".'
                               .format(type(key)))
            if not isinstance(value, str):
                raise DofError('{}.init(): value of an info '
                               .format(self.__class__.__name__) +
                               'must be instance of str but is "{}".'
                               .format(type(value)))
            if key in self.keys():
                raise DofError('{}.init(): tried to Initialize'
                               .format(self.__class__.__name__) +
                               'info "{}" twice. Original: "{}", new: "{}"'
                               .format(key, self[key], value))
            self[key] = value


    def from_json(self, json_string : str, **kwargs) -> any:
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
            If the function is not implemented in a subclass.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        raise DofError('{}.from_json() method must be implemented.'
                       .format(self.__class__.__name__))


    def get_key_by_value(self, value : str) -> str:
        """
        Get key of a value
        ==================

        Parameters
        ----------
        value : str
            The value to search for.

        Returns
        -------
        str
            The key that belongs to the given parameter.

        Raises
        ------
        DofError
            There is no existing value.

        See Also
        --------
            Checking the existence of value : has_value()

        Notes
        -----
            Since this function throws error when there is no founded key to the
            given value, it is advised to check the existence of value with the
            has_value() function before you run this.
        """

        for _key, _value in self.items():
            if _value == value:
                return _key
        raise DofError('{}.get_key_by_value() given value '
                       .format(self.__class__.__name__) +
                       '"{}" dosen\'t exist in the info.'.format(value))


    def has_key(self, key : str) -> bool:
        """
        Return whether the key exists or not
        ====================================

        Parameters
        ----------
        key : str
            The key to search for.

        Returns
        -------
        bool
            True if key exists, False if not.
        """

        return key in self.keys()


    def has_value(self, value : str) -> bool:
        """
        Return whether the value exists or not
        ======================================

        Parameters
        ----------
        value : str
            The value to search for.

        Returns
        -------
        bool
            True if value exists, False if not.
        """

        return value in self.values()


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
        dict(str : str)
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        if describe_only:
            result = create_json_dict(self.__class__.__name__,
                                      self.__class__.__module__, describe_only,
                                      description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                        len(self))])
        else:
            result = create_json_dict(self.__class__.__name__,
                                      self.__class__.__module__, describe_only,
                                      content_form=ContentForm.TEXTUAL,
                                      description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                        len(self))])
            for key, value in self.items():
                result[JSONRoot.CONTENT.value][key] = value
        return result


    def __setitem__(self, key : str, value : str):
        """
        Provide typed version of the built-in __setitem__ function
        ==========================================================

        Parameters
        ----------
        key : str
            The key to set.
        value : str
            The value to set.

        Raises
        ------
        TypeError
            When the type of key or value is not string.

        Notes
        -----
            The only reason why we override this built-in function is to ensure
            that both keys and values are strings only.
        """

        if isinstance(key, str) and isinstance(value, str):
            super().__setitem__(key, value)
        else:
            raise TypeError('{} setting item: type of key and value must be '
                            .format(self.__class__.__name__) +
                            'str, but key is "{}" and value is "{}".'
                            .format(type(key), type(value)))


class InformationStrict(Information):
    """
    Provide Information with mandatory keys
    =======================================

    Attributes
    ----------
    is_complete : bool (read-only)
        True if all mandatory infos are added or False if not.
    mandatory_keys : list (read-only)
        Get back the list of all mandatory keys.
    """

    def __init__(self, initial_values : list, mandatory_keys : list):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]
        mandatory_keys : list
            List of the neccessary information fields. Each elements of list
            must be string.
        """

        super().__init__(initial_values)
        self.__mandatory_keys = mandatory_keys


    @property
    def is_complete(self) -> bool:
        """
        Returns whether all mandatory infos are added or not
        ====================================================

        Returns
        -------
        bool
            True if each mandatory key exists, False if not.

        See Also
        --------
            How to fill mandatory fields with unknown values : class Contact
        """

        return all(element in self.keys() for element in self.__mandatory_keys)


    @property
    def mandatory_keys(self) -> list:
        """
        Return all mandatory keys
        =========================

        Returns
        -------
        list
            Copy of the list of all mandatory keys.

        Notes
        -----
            This property doesn't provide direct access to the inside list of
            mandatory keys, it is just a copy of it. If any change is made, it
            has no effect to the instance.
        """

        return self.__mandatory_keys[:]


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
        dict(str : str)
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        if describe_only:
            result = create_json_dict(self.__class__.__name__,
                                      self.__class__.__module__, describe_only,
                                      description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                        len(self)),
                                       (JSONDescription.IS_COMPLETE,
                                        self.is_complete)])
        else:
            result = create_json_dict(self.__class__.__name__,
                                      self.__class__.__module__, describe_only,
                                      content_form=ContentForm.TEXTUAL,
                                      description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                        len(self)),
                                       (JSONDescription.IS_COMPLETE,
                                        self.is_complete)])
            for key, value in self.items():
                result[JSONRoot.CONTENT.value][key] = value
        return result


class Contact(InformationStrict):
    """
    Contain contact information
    ===========================

    See Also
    --------
        Mandatory information : class InformationStrict(Information)

    Notes
    -----
    I.
        Dataset must be connected to any entity. It gives help the user to get
        in touch with the competent personif they have anyquestion about data,
        dataset, any subset of dataset or any other information connected to the
        DoF file.
        Mandatory information: 'name', 'entity_type', 'email'
        If any information is unknown, use the 'NA' string to fill the field.
    II.
        Entity_type can be for example: `person`, `researcher`, `university`,
                                        `research center`
    """

    def __init__(self, initial_values : list = []):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list, optional (empty list if omitted)
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.


        super().__init__(initial_values, ['name', 'entity_type', 'email'])


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
            If the content of the JSON string is not valid to create the
            instance.

        See Also
        --------
            Possible return values of data : datamodel.get_content()

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'Contact', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('Contact.from_json(): JSON string is not valid to' +
                           ' create an instance.')
        return Contact(list(data.items()))


class ContainerInfo(InformationStrict):
    """
    Contain information related to the whole dataset
    ================================================

    Attributes
    ----------
    is_complete : bool (read-only)
        True if all mandatory infos are added or False if not.
    mandatory_keys : list (read-only)
        Get back the list of all mandatory keys.

    See Also
    --------
        Mandatory information : class InformationStrict(Information)

    Notes
    -----
        Dataset must be connected to a small number of information. It gives
        help the user how to use, rework, cite or research the data, small
        subset of dataset or the whole dataset as well.
        Mandatory information: 'author', 'author_contact', 'source', 'license'
        If any information is unknown, use the 'NA' string to fill the field.
    """

    def __init__(self, initial_values : list = []):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list, optional (empty list if omitted)
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        super().__init__(initial_values, ['author', 'author_contact', 'source',
                                          'license'])


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
            If the content of the JSON string is not valid to create the
            instance.

        See Also
        --------
            Possible return values of data : datamodel.get_content()

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'ContainerInfo', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('ContainerInfo.from_json(): JSON string is not ' +
                           'valid to create an instance.')
        return ContainerInfo(list(data.items()))


class DataElementInfo(Information):
    """
    Contain information related to specific DataElements
    ====================================================

    Notes
    -----
        Connecting information to any DataElements is not neccessary. However,
        it is advised to use these fields to store the DataElement releted
        informations. If any element is different than the majority of elements,
        you should fill the fields with those information.

    See Also
    --------
        Super class init: Information.__init__()
    """


    def __init__(self, initial_values : list = []):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list, optional (empty list if omitted)
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        super().__init__(initial_values)


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
            If the content of the JSON string is not valid to create the
            instance.

        See Also
        --------
            Possible return values of data : datamodel.get_content()

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'DataElementInfo', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('DataElementInfo.from_json(): JSON string is not ' +
                           'valid to create an instance.')
        return DataElementInfo(list(data.items()))


class Document(InformationStrict):
    """
    Provide access to a document (related to dataset)
    =================================================

    Attributes
    ----------
    document : DofObject
        Provide direct access to the document.

    Notes
    -----
        This class is a subclass of InformationStrict due to that any real life
        documents (for example: pdf, docx) contains a lot of information and
        data. So we decided to abstract this real life problem and see and
        handle real documents and a special collection of information. That's
        why class Document is a special inheritence of the InformationStrict
        class.
    """

    def __init__(self, initial_values : list = [], document : DofObject = None):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        initial_values : list, optional (empty list if omitted)
            List that contains the key and content values. Key is the name of
            any information field. Key and value must be string.
            eg.:[[key1, content1], [key2, content2] ... [keyN, contentN]]
        document : DofObject, optional (None, if omitted)
            The document itself in a form of a binary DofObject.

        Raises
        ------
        DofError
            When the is_binary state of DofObject is True, the DofObject must
            be contains binary data.

        See Also
        --------
            Meaning the state of is_binary flag : core.DofObject
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        super().__init__(initial_values, ['file', 'title', 'short_description'
                                          'long_description', 'author',
                                          'credits', 'license', 'date',
                                          'originally_available_at',
                                          'howto_cite', 'publicated_at',
                                          'contact', 'version'])
        if document is None:
            self.__document = DofObject(is_binary=True)
        else:
            if not document.is_binary:
                raise DofError('Document.init(): DofObject containing a ' +
                               'document must be a binary DofObject.')
            self.__document = document


    @property
    def document(self) -> DofObject:
        """
        Provide direct access to the document
        =====================================

        Returns
        -------
        DofObject
            The stored document.
        """

        return self.__document


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
            If the content of the JSON string is not valid to create the
            instance.
        DofError
            When the JSON string does not contain description.
        DofError
            When the JSON string does not contain about.
        DofError
            When the is_binary state in JSON string is not True.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'Document', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('Document.from_json(): JSON string is not valid to' +
                           ' create an instance.')
        _description = json_dict.get(JSONRoot.DESCRIPTION.value)
        if _description is None:
            raise DofError('Document.from_json(): JSON string is not ' +
                           'complete, without description restore is not ' +
                           'available.')
        _about = _description.get(JSONDescription.ABOUT)
        if _about is None:
            raise DofError('Document.from_json(): JSON string is not ' +
                           'complete, without "about" fields restore is not ' +
                           'available.')
        _document = DofObject.from_json(dumps(data))
        if not _document.is_binary:
            raise DofError('Document.from_json(): JSON string is not ' +
                           'complete, embedded document must be binary ' +
                           'restore is not available.')
        return Document(list(data.items()), _document)


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
        dict(str : any)
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        _info = {}
        for key in sorted(self.keys()):
            _info[key] = self[key]
        if describe_only:
            result = create_json_dict('Document', 'dof.information',
                                      describe_only, description=
                                      [(JSONDescription.ABOUT, _info),
                                       (JSONDescription.IS_COMPLETE,
                                        self.is_complete)])
        else:
            result = create_json_dict('Document', 'dof.information',
                                      describe_only,
                                      content_form=ContentForm.BINARY,
                                      description=
                                      [(JSONDescription.ABOUT, _info),
                                       (JSONDescription.IS_COMPLETE,
                                        self.is_complete)])
            result[JSONRoot.CONTENT.value] = self.__document.to_json(
                                                                describe_only)
        return result


class DocumentContainer(list, DofSerializable):
    """
    Class to hold dataset related documents
    =======================================
    """

    def __init__(self, documents : list = []):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        documents : list, optional (empty list if omitted)
            List of documents to instantiate the object.

        Raises
        ------
        DofError
            When the instance of elements are not dof.information.
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        for document in documents:
            if not isinstance(document, Document):
                raise DofError('DocumentContainer.init(): initial documents' +
                               'must be instances of Document ' +
                               '(dof.information).')
        if len(documents) > 0:
            super().__init__(documents)


    def append(self, item : Document):
        """
        Provide append functionality with instance check
        ================================================

        Parameters
        ----------
        item : Document
            The element to add.

        Raises
        ------
        DofError
            When the instance of added element is not dof.information.
        """
        if isinstance(item, Document):
            super().append(item)
        else:
            raise DofError('DocumentContainer.append(): element must be ' +
                           'instance of Document (dof.information).')


    def force_load_to_memory(self) -> bool:
        """
        Load data to memory if possible
        ===============================

        Returns
        -------
        bool
            True if data get loaded into the memory, False if not.
        """

        return all(e.document.force_load_to_memory() for e in self)


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
            If the content of the JSON string is not valid to create the
            instance.
        DofError
            When the JSON storing does not contain lists.

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'DocumentContainer', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('DocumentContainer.from_json(): JSON string is not' +
                           ' valid to create an instance.')
        if not isinstance(data, list):
            raise DofError('DocumentContainer.from_json(): JSON string has ' +
                           'bad content, it must be instance of list, restore' +
                           ' is not available.')
        result = DocumentContainer()
        for element in data:
            result.append(Document.from_json(dumps(element)))
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
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        if describe_only:
            result = create_json_dict('DocumentContainer', 'dof.information',
                                      describe_only, description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                      len(self))])
        else:
            result = create_json_dict('DocumentContainer', 'dof.information',
                                      describe_only,
                                      content_form=
                                                ContentForm.MULTIPLE_INSTANCES,
                                      description=
                                      [(JSONDescription.ELEMENTS_COUNT,
                                      len(self))])
            _data = [element.to_json_dict(describe_only) for element in self]
            result[JSONRoot.CONTENT.value] = _data
        return result


class ModelInfo(DofSerializable):
    """
    Class to hold information related to the applied model
    ======================================================
    """


    # Top level namespaces in ModelInfo
    DATA_PROCESSING = 'data_processing'
    MODEL = 'model'
    PERFORMANCE = 'performance'
    TRAINING = 'training'


    def __init__(self, model_settings : dict = {},
                 data_processing_settings : dict = {},
                 performance_settings : dict = {},
                 training_settings : dict = {}):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        model_settings : dict, optional (empty dictionary if omitted)
            Key, value pairs for a similarly named top_namespace.
        data_processing_settings : dict, optional (empty dictionary if omitted)
            Key, value pairs for a similarly named top_namespace.
        performance_settings : dict, optional (empty dictionary if omitted)
            Key, value pairs for a similarly named top_namespace.
        training_settings : dict, optional (empty dictionary if omitted)
            Key, value pairs for a similarly named top_namespace.

        See Also
        --------
            Using template to store model info : ModelInfo.from_template()
            Suggested keys for each top_namespace : ModelInfo.from_template()
        """

        # pylint: disable=dangerous-default-value
        #         Default value is needed to provide faster instance creation.

        self.__model = {}
        self.__training = {}
        self.__data_processing = {}
        self.__performance = {}
        if len(model_settings) > 0:
            for key, value in model_settings.items():
                self.add(ModelInfo.MODEL, key, value)
        if len(data_processing_settings) > 0:
            for key, value in data_processing_settings.items():
                self.add(ModelInfo.DATA_PROCESSING, key, value)
        if len(performance_settings) > 0:
            for key, value in performance_settings.items():
                self.add(ModelInfo.PERFORMANCE, key, value)
        if len(training_settings) > 0:
            for key, value in training_settings.items():
                self.add(ModelInfo.TRAINING, key, value)


    def add(self, top_namespace : str, key : str, element : any):
        """
        Add new element to namespace
        ============================

        Parameters
        ----------
        top_namespace : str
            Category of model description.
        key : str
            Subcategory as a key under the selected top_namespace.
        element : any
            Value of the selected subcategory.

        Raises
        ------
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.DATA_PROCESSING top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.MODEL top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.PERFORMANCE top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.TRAINING top_namespace.
        DofError
            When the given top_namespace does not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if isinstance(element, (DofObject, str)):
            _element = element
        else:
            _element = DofObject(element)
        if top_namespace == ModelInfo.DATA_PROCESSING:
            if key in self.__data_processing.keys():
                raise DofError('ModelInfo.add(): tried to add element to ' +
                               'an already existing data processing key.')
            self.__data_processing[key] = _element
        elif top_namespace == ModelInfo.MODEL:
            if key in self.__model.keys():
                raise DofError('ModelInfo.add(): tried to add element to ' +
                               'an already existing model key.')
            self.__model[key] = _element
        elif top_namespace == ModelInfo.PERFORMANCE:
            if key in self.__performance.keys():
                raise DofError('ModelInfo.add(): tried to add element to ' +
                               'an already existing performance key.')
            self.__performance[key] = _element
        elif top_namespace == ModelInfo.TRAINING:
            if key in self.__training.keys():
                raise DofError('ModelInfo.add(): tried to add element to ' +
                               'an already existing training key.')
            self.__training[key] = _element
        else:
            raise DofError('ModelInfo.add(): unsupported to level namespace.')


    def delete(self, top_namespace : str, key : str):
        """
        Delete element from namespace
        =============================

        Parameters
        ----------
        top_namespace : str
            Category of model description.
        key : str
            Subcategory as a key under the selected top_namespace.

        Raises
        ------
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.DATA_PROCESSING top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.MODEL top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.PERFORMANCE top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.TRAINING top_namespace.
        DofError
            When the given top_namespace does not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if top_namespace == ModelInfo.DATA_PROCESSING:
            if key not in self.__data_processing.keys():
                raise DofError('ModelInfo.delete(): tried to delete non-' +
                               'existing data processing key.')
            del self.__data_processing[key]
        elif top_namespace == ModelInfo.MODEL:
            if key not in self.__model.keys():
                raise DofError('ModelInfo.delete(): tried to delete non-' +
                               'existing model key.')
            del self.__model[key]
        elif top_namespace == ModelInfo.PERFORMANCE:
            if key not in self.__performance.keys():
                raise DofError('ModelInfo.delete(): tried to delete non-' +
                               'existing performance key.')
            del self.__performance[key]
        elif top_namespace == ModelInfo.TRAINING:
            if key not in self.__training.keys():
                raise DofError('ModelInfo.delete(): tried to delete non-' +
                               'existing training key.')
            del self.__training[key]
        else:
            raise DofError('ModelInfo.delete(): unsupported to level ' +
                           'namespace.')


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

        Notes
        -----
            This function requires a JSON string that is created with the
            .to_json(describe_only=False) function.
        """

        json_dict = loads(json_string, **kwargs)
        data = get_content(json_dict, 'ModelInfo', 'dof.information',
                           describe_only=False)
        if data is None:
            raise DofError('ModelInfo.from_json(): JSON string is not valid' +
                           'to create an instance.')
        _model_raw = data.get(JSONContent.MODEL_INFO.value)
        if _model_raw is None:
            raise DofError('ModelInfo.from_json(): JSON string content field ' +
                           'doesn\'t have model info field, restore is not ' +
                           'available.')
        _data_processing_raw = data.get(JSONContent.MODEL_DATA_PROCESSING.value)
        if _data_processing_raw is None:
            raise DofError('ModelInfo.from_json(): JSON string content field ' +
                           'doesn\'t have data processing field, restore is ' +
                           'not available.')
        _performance_raw = data.get(JSONContent.MODEL_PERFORMANCE.value)
        if _performance_raw is None:
            raise DofError('ModelInfo.from_json(): JSON string content field ' +
                           'doesn\'t have performance field, restore is not ' +
                           'available.')
        _training_raw = data.get(JSONContent.MODEL_TRAINING.value)
        if _training_raw is None:
            raise DofError('ModelInfo.from_json(): JSON string content field ' +
                           'doesn\'t have training field, restore is not '+
                           'available.')
        return ModelInfo({key : DofObject.from_json(dumps(value))
                          if isinstance(value, dict) else value
                          for key, value in _model_raw.items()},
                         {key : DofObject.from_json(dumps(value))
                          if isinstance(value, dict) else value
                          for key, value in _data_processing_raw.items()},
                         {key : DofObject.from_json(dumps(value))
                          if isinstance(value, dict) else value
                          for key, value in _performance_raw.items()},
                         {key : DofObject.from_json(dumps(value))
                          if isinstance(value, dict) else value
                          for key, value in _training_raw.items()})


    def force_load_to_memory(self) -> bool:
        """
        Load data to memory if possible
        ===============================

        Returns
        -------
        bool
            True if data get loaded into the memory, False if not.
        """

        return all([all(e.force_load_to_memory()
                        if isinstance(e, DofObject) else True
                        for e in self.__model),
                    all(e.force_load_to_memory()
                        if isinstance(e, DofObject) else True
                        for e in self.__data_processing),
                    all(e.force_load_to_memory()
                        if isinstance(e, DofObject) else True
                        for e in self.__performance),
                    all(e.force_load_to_memory()
                        if isinstance(e, DofObject) else True
                        for e in self.__training)])


    @classmethod
    def from_template(cls) -> any:
        """
        Create instance from a template
        ================================

        Returns
        -------
        ModelInfo
            A new instance with pre-defined keys.

        Notes
        -----
            Suggested keys in each top_namespace and it's meanings with
            example:

            DATA_PROCESSING
            ~~~~~~~~~~~~~~~
              > prepocessing_steps [str]
                Description of each transforms during the phase of prepocessing.
                eg: "(1) normalize between 0 and 1
                     (2) random crop
                     (3) random horizontal flip
                     (4) random vertical flip
                     (5) random zoom between 0.95 and 1.25"
              > crop [str]
                Description of cropping method.
                eg: "centercrop : 10", "fivecrop : 20" or "randomcrop : 15"
              > resize [str]
                Description of resizing method.
                eg: "randomresize : 0.9, scale : (0.1, 1.0), ratio : (0.8, 1.2)"
              > normalization [str]
                Description of normalization method.
                eg: "Between 0 and 1" or "with n/sum(N) formula"
              > horizontal_flip [str]
                Description of horizontal flip.
                eg: "False" or "random : 0.5"
              > vertical_flip [str]
                Description of vertical flip.
                eg: "False" or "random : 0.5"
              > height_shift [str]
                Description of height shift.
                eg: "False", "None", "random : (0.85, 2.3)", "random : (10px)"
              > width_shift [str]
                Description of width shift.
                eg: "False", "None", "random : (0.85, 2.3)", "random : (10px)"
              > rotation_angle [str]
                Description of rotating method.
                eg: "random : [degrees : (0.8, 1.2), center=True]"
              > shear_range [str]
                Description of shearing method.
                eg: "False" or "(0.2, 1.3)"
              > zoom_range [str]
                Description of zooming method.
                eg: "False", "center : 0.8" or
                    "random : [probability : 0.2, range : (0.9, 1.31)]"
              > other [str]
                Each preprocessing methods that do not fit into the categories
                above.
                eg: "RandomAffine [degrees : (0.8, 1.2), scale : (0.8, 1.2),
                                   shear : None]"
              > note [str]
                Any important information.
                eg: "This data processing method fits for the most use-cases
                     that can occur in healthcare. Vertical and horizontal flips
                     should not use since 'AP' and 'PA' X-rays or different and
                     a simple flip cannot represent that difference."
            MODEL
            ~~~~~
              > model_name [str]
                Name of the model. It is advised to use a descriptive name.
                eg: "MyFirstTest", "VGG11-headless-out25"
              > original_framework [str]
                The name of the used framework.
                eg: "Pytorch", "torch", "TensorFlow", "TF1.0", or "OpenVINO"
              > structure [str]
                The description of model's structure.
                eg: "Core model: Headless VGG-10
                     Classifier: 4 Dense layers with the following outputs:
                                 256, 512, 128, 25"
              > weights_and_biases_data [byte | bytearray]
                Saved model data.
                eg: result of torch.save()
              > trainable_parameters [str]
                Description of trainable params.
                eg: "5.000.000 trainable params in 3 Dense layers."
              > optimizer [str]
                Description of the optimizer.
                eg: "SGD", "ADAM" or "Adadelta with default parameters"
              > optimizer_parameters [str]
                Description of the optimizer's params.
                eg: "default", "learning rate : 1e-5" or
                    "lr : 0.2, lr_decay : 0.00095"
              > criterion [str]
                Description of the criterion.
                eg: "CrossEntropyLoss", "MSE" or "MSE [size_average : False]"
              > criterion_parameters [str]
                Description of the criterion's params.
                eg: "default", "size_average : False" or "reduction : sum"
              > x_structure [str]
                Description of X values.
                eg: "1st dim: temperature in celsius
                     2nd dim: humidity level
                     batch_first : True"
              > x_preprocessing_requirements [str]
                Description of each steps during the phase of X-preprocessing.
                Important: This is different than the content of
                           DATA_PROCESSING.prepocessing_steps. This is about
                           the preprocessing of X values.
                eg: "None", "batchfirst=True", "Do not use random sampling."
              > y_structure [str]
                Description of Y values.
                eg: "1st dim: possibility of forest fire in the next week
                     2nd dim: possibility of forest fire in the next month
                     postprocessing_required : True"
              > y_postprocessing_requirements [str]
                Description of each steps during the phase of Y-postprocessing.
                eg: "The energy prediction made for 1 kW/h production capacity.
                     To get the real value, you should multipy the result of the
                     available capacity of power plant." or
                     "result *= 1.5 / ln(result)"
              > intended_use_statement [str]
                This section refers to the part of the FDA's 501(k) submission.
                eg: "The software helps to radiologist in detection of pneumonia
                     in X-ray images by giving a prediction class and a
                     prediction score. However, this software do not contact
                     with the patients or with the patient's internal organs,
                     nervous- or cardiovascular system, it’s a diagnostic tool
                     for internal organ."
              > indications_for_use [str]
                This section refers to the part of the FDA's 501(k) submission.
                eg: "Indications for use is screening of PA or AP positioned
                     chest X-ray images from a target population with no prior
                     history of lung defectiveness or lung surgery. The X-ray
                     images shall be equals or higher than 224 x 224 pixels."
              > device_limitations [str]
                This section refers to the part of the FDA's 501(k) submission.
                eg: "Software is recommended to diagnose chest x-ray images of
                     patients who has both lung. It is adviced to use the model
                     without these comorbid pathologies:
                        - consolidation
                        - edema
                        - effusion
                        - emphysema

                     The model works well with negative cases, but fails with
                     positive ones. The age of patient shall be between 21 and
                     90 years, that’s why the model cannot be used on X-rays of
                     child patient. The structure of human body is changing
                     during years and the model wasn’t trained on young lungs.
                     Older patients regularly have several diseases and the
                     model wasn’t trained on them.

                     The model is written in TensorFlow, so the running machine
                     have to meet the system requirements of tensorflow
                     framework. Model cannot be trained or finetuned on the
                     machines of hospitals. The model is trained on Intel(R)
                     Core i3-4160 3,6GHz CPU and Nvidia GT640 GPU with 2 GB
                     GPU-RAM. The computation time of average image
                     pre-processing is 200 ms, max 201 ms. The average time of
                     inference is 1.36 s, max 1.37 s. The whole inference
                     workflow is under 1.4 s on a computer with Intel(R)
                     Core i3-4160 3,6GHz CPU and Nvidia GT640 GPU. For reaching
                     that performance similar (or higher) CPU and GPU is
                     recommended. The computational time of image pre-processing
                     depends on the performance of CPU, the time of inference
                     depends on CPU and GPU."
              > other [str]
                Any other keys or values are not be covered in the template.
                eg: "Dropout 0.4 was used to avoid overfitting."
              > note [str]
                Any important information.
                eg: "This model is ready for beginning the FDA validation
                     process." or "In the next experiment it would be good to
                     use big-batch-training where the batch size bigger than
                     4096."

            PERFORMANCE
            ~~~~~~~~~~~
              > training_performance [str]
                Performance data and description in general.
                eg: "The model fails when the input data comes from patient
                     who is older than 90 years old." or
                    "Average prediction time is 0.008 sec on a Raspberry Pi 4."
              > training_loss [str]
                Value representation of training loss.
                eg: "None", "0.000015" or "8.91568e-9"
              > test_loss [str]
                Value representation of test loss.
                eg: "None", "0.000015" or "8.91568e-9"
              > validation_loss [str]
                Value representation of validation loss.
                eg: "None", "0.000015" or "8.91568e-9"
              > ROC_curve [byte | bytearray]
                Image representation of ROC curve.
                eg: result of sklearn.metrics.roc_curve()
              > P-R_curve [byte | bytearray]
                Image representation of P-R curve.
                eg: result of sklearn.metrics.precision_recall_curve()
              > F1_score [str]
                Value of F1 score.
                eg: calculated from the result of
                    sklearn.metrics.precision_recall_curve()
              > confusion_matrix [byte | bytearray]
                Image representation of confusion matrix curve.
                eg: result of sklearn.metrics.confusion_matrix()
              > other [str]
                Any other keys or values are not be covered in the template.
                eg: "Image representation of precision/recall by different
                     thresholds"
              > note [str]
                Any important information.
                eg: "The average F1 score of human radiologists is 0.387
                     according to paper of CheXNet, that is available here:
                     https://arxiv.org/pdf/1711.05225.pdf

                     The performance of this model is quite good based on the
                     metrics. Major measures related to the final threshold:
                        F1 score max:   0.4000
                        Threshold:      0.5512
                        Precision:      0.3500
                        Recall:         0.4375"

            TRAINING
            ~~~~~~~~
              > initialization_method [str]
                The method of initialization.
                eg: "node : xavier_uniform", "bias : ones" or
                    "node : kaiming_uniform, bias : zeros"
              > batch_size [str]
                The value of batch size.
                eg: "256"
              > optimizer_learning_rate [str]
                The value of learning rate.
                eg: "1e-4" or "0.000005"
              > optimizer_momentum [str]
                The value of optimizer's momentum.
                eg: "0.05"
              > other [str]
                Any other keys or values are not be covered in the template.
                eg: "optimizer learning rate decay : 0.00095"
              > note [str]
                Any important information.
                eg: "Big batch size (> 386) caused out of memory error on
                     GTX-1060Ti 4GB."
        """

        model_keys = ['model_name', 'original_framework',
                      'structure', 'weights_and_biases_data',
                      'trainable_parameters', 'optimizer',
                      'optimizer_parameters', 'criterion',
                      'criterion_parameters', 'x_structure',
                      'x_preprocessing_requirements', 'y_structure',
                      'y_postprocessing_requirements', 'intended_use_statement',
                      'indications_for_use', 'device_limitations', 'other',
                      'note']
        data_processing_keys = ['prepocessing_steps' , 'crop', 'resize',
                                'normalization', 'horizontal_flip',
                                'vertical_flip', 'height_shift', 'width_shift',
                                'rotation_angle', 'shear_range', 'zoom_range',
                                'other', 'note']
        performance_keys = ['training_performance', 'training_loss',
                            'test_loss', 'validation_loss', 'ROC_curve',
                            'P-R_curve', 'F1_score', 'confusion_matrix',
                            'other', 'note']
        training_keys = ['initialization_method', 'batch_size',
                         'optimizer_learning_rate', 'optimizer_momentum',
                         'other', 'note']
        return ModelInfo({key : None for key in model_keys},
                         {key : None for key in data_processing_keys},
                         {key : None for key in performance_keys},
                         {key : None for key in training_keys})


    def get(self, top_namespace : str, key : str) -> any:
        """
        Get element from namespace
        ==========================

        Parameters
        ----------
        top_namespace : str
            Category of model description.
        key : str
            Subcategory as a key under the selected top_namespace.

        Returns
        -------
        any
            Value of the selected subcategory, where top_namespace is the
            main category and key is the subcategory.

        Raises
        ------
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.DATA_PROCESSING top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.MODEL top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.PERFORMANCE top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.TRAINING top_namespace.
        DofError
            When the given top_namespace does not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if top_namespace == ModelInfo.DATA_PROCESSING:
            if key not in self.__data_processing.keys():
                raise DofError('ModelInfo.get(): tried to get non-existiing ' +
                               'data processing key.')
            result = self.__data_processing[key]
        elif top_namespace == ModelInfo.MODEL:
            if key not in self.__model.keys():
                raise DofError('ModelInfo.get(): tried to get non-existiing ' +
                               'model key.')
            result = self.__model[key]
        elif top_namespace == ModelInfo.PERFORMANCE:
            if key not in self.__performance.keys():
                raise DofError('ModelInfo.get(): tried to get non-existiing ' +
                               'performance key.')
            result = self.__performance[key]
        elif top_namespace == ModelInfo.TRAINING:
            if key not in self.__training.keys():
                raise DofError('ModelInfo.get(): tried to get non-existiing ' +
                               'training key.')
            result = self.__training[key]
        else:
            raise DofError('ModelInfo.get(): unsupported to level namespace.')
        return result


    def get_all(self, top_namespace : str) -> dict:
        """
        Get all elements from a namespace
        =================================

        Parameters
        ----------
        top_namespace : str
            Category of model description.

        Returns
        -------
        dict
            Copy of the original namespace dictionary.

        Raises
        ------
        DofError
            When the given top_namespace does not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if top_namespace == ModelInfo.DATA_PROCESSING:
            result = self.__data_processing.copy()
        elif top_namespace == ModelInfo.MODEL:
            result = self.__model.copy()
        elif top_namespace == ModelInfo.PERFORMANCE:
            result = self.__performance.copy()
        elif top_namespace == ModelInfo.TRAINING:
            result = self.__training.copy()
        else:
            raise DofError('ModelInfo.get_all(): unsupported to level ' +
                          'namespace.')
        return result


    def has_key(self, top_namespace : str, key : str) -> bool:
        """
        Get element from namespace
        ==========================

        Parameters
        ----------
        top_namespace : str
            Category of model description.
        key : str
            Subcategory as a key under the selected top_namespace.

        Returns
        -------
        bool
            Whether the given key is exist in the given category or not.

        Raises
        ------
        DofError
            When the given top_namespace is not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if top_namespace == ModelInfo.DATA_PROCESSING:
            result = key in self.__data_processing.keys()
        elif top_namespace == ModelInfo.MODEL:
            result = key in self.__model.keys()
        elif top_namespace == ModelInfo.PERFORMANCE:
            result = key in self.__performance.keys()
        elif top_namespace == ModelInfo.TRAINING:
            result = key in self.__training.keys()
        else:
            raise DofError('ModelInfo.get(): unsupported to level namespace.')
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
            Dict that is complatible to create a JSON formatted string.

        Notes
        -----
            If the value of describe_only parameter is True, only description
            data returns. This means the dataset won't be included. It does not
            matter that the dataelements are images or strings. The goal of
            describe_only is not to store the data but to describe it.
        """

        _description = [(JSONDescription.ELEMENTS_COUNT_MODEL,
                         len(self.__model)),
                        (JSONDescription.ELEMENTS_COUNT_DATA_PROCESSING,
                         len(self.__data_processing)),
                        (JSONDescription.ELEMENTS_COUNT_PERFORMANCE,
                         len(self.__performance)),
                        (JSONDescription.ELEMENTS_COUNT_TRAIN,
                         len(self.__training))]
        if describe_only:
            result = create_json_dict('ModelInfo', 'dof.information',
                                      describe_only, description=_description)
        else:
            result = create_json_dict('ModelInfo', 'dof.information',
                                      describe_only,
                                      content_form=
                                                ContentForm.MULTIPLE_INSTANCES,
                                      description=_description)
            _content = {JSONContent.MODEL_INFO.value :
                        {key : value.json_dict(describe_only)
                         if isinstance(value, DofObject) else value
                         for key, value in self.__model.items()},
                        JSONContent.MODEL_DATA_PROCESSING.value :
                        {key : value.json_dict(describe_only)
                         if isinstance(value, DofObject) else value
                         for key, value in self.__data_processing.items()},
                        JSONContent.MODEL_PERFORMANCE.value :
                        {key : value.json_dict(describe_only)
                         if isinstance(value, DofObject) else value
                         for key, value in self.__performance.items()},
                        JSONContent.MODEL_TRAINING.value :
                        {key : value.json_dict(describe_only)
                         if isinstance(value, DofObject) else value
                         for key, value in self.__training.items()}}
            result[JSONRoot.CONTENT.value] = _content
        return result


    def update(self, top_namespace : str, key : str, new_element : any):
        """
        Update element in the namespace
        ===============================

        Parameters
        ----------
        top_namespace : str
            Category of model description.
        key : str
            Subcategory as a key under the selected top_namespace.
        new_element : any
            Value of the selected subcategory.

        Raises
        ------
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.DATA_PROCESSING top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.MODEL top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.PERFORMANCE top_namespace.
        DofError
            When the given subcategory is not exist in the selected
            ModelInfo.TRAINING top_namespace.
        DofError
            When the given top_namespace does not exist.

        See Also
        --------
            Values of top_namespace : class ModelInfo
        """

        if isinstance(new_element, str):
            _element = new_element
        else:
            _element = DofObject(new_element)
        if top_namespace == ModelInfo.DATA_PROCESSING:
            if key not in self.__data_processing.keys():
                raise DofError('ModelInfo.update(): tried to update a non-' +
                               'existing element with data processing key.')
            self.__data_processing[key] = _element
        elif top_namespace == ModelInfo.MODEL:
            if key not in self.__model.keys():
                raise DofError('ModelInfo.update(): tried to update a non-' +
                               'existing element with model key.')
            self.__model[key] = _element
        elif top_namespace == ModelInfo.PERFORMANCE:
            if key not in self.__performance.keys():
                raise DofError('ModelInfo.update(): tried to update a non-' +
                               'existing element with performance key.')
            self.__performance[key] = _element
        elif top_namespace == ModelInfo.TRAINING:
            if key not in self.__training.keys():
                raise DofError('ModelInfo.update(): tried to update a non-' +
                               'existing element with training key.')
            self.__training[key] = _element
        else:
            raise DofError('ModelInfo.update(): unsupported to level ' +
                           'namespace.')


if __name__ == '__main__':
    pass
