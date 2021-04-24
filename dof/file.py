"""
DoF - Deep Model Core Output Framework
======================================

Submodule: file

Notes
-----
    We tried to minimize the number of imports to the neccessary ones. That's
    why we used `from json import loads` instead of `import json` and
    `from pickle import dump, loads` instead of `import pickle`. Due to the
    readability of code we named some imports. Users usually see for example
    `json.loads` or `pickle.load` in code, so we use `json_loads`,
    `pickle_dump` and `pickle_load` expressions to provide both readability of
    code and optimization at the same time.
"""


from json import dumps as json_dumps, loads as json_loads
from os import mkdir
from os.path import isdir, splitext
from pickle import dump as pickle_dump, load as pickle_load
from zipfile import ZipFile

from .core import DofObject
from .data import Dataset
from .datamodel import ContentForm, JSONContent, JSONDescription, JSONRoot
from .datamodel import create_json_dict, get_content
from .error import DofError
from .information import ContainerInfo, DocumentContainer, ModelInfo
from .storage import DofObjectHandler, LocalHandler


class DofFile:
    """
    DoF main class
    ==============

    Attributes
    ----------
    dataset : Dataset
        Provide access to the dataset of the DofFile.
    documents : DocumentContainer
        Provide access to the document container of the DofFile.
    dof_basepath : str
        The working directory of DoF.
    info : ContainerInfo
        Provide access to the information container of the DofFile.
    model_info : ModelInfo
        Provide access to the model informations of the DofFile.
    """


    DOF_AUTODETECT = ''
    DOF_FILE = 'dof'
    DOF_JSON = 'dofj'
    DOF_PYTHON = 'dofpy'


    def __init__(self, *args : any, dof_basepath : str = './dof_basepath',
                 restore_mode : bool = False):
        """
        Initialize an instance of the object
        ====================================

        Parameters
        ----------
        args : any
            Arguments to instantiate a DofFile from already existing elements.
        dof_basepath : str, optional ('./dataset' if omitted)
            Base directory of the content of the DofFile.
        restore_mode : bool, optional (False if omitted)
            Mode selector flag between normal mode (False) and restore mode
            (True).

        Raises
        ------
        DofError
            When the given instance type in *args is unsupported.

        Notes
        -----
        I.
            Supported instances: Dataset, ContainerInfo, DataProfiler,
                                 DocumentContainer, ModelInfo,
                                 ErrorCorrection, Security
        II.
            DofFile has three main instantiation approaches:
                1. without any arguments in normal mode
                2. with some arguments in normal mode
                3. restore mode.
            1.  Normal mode with no arguments:
                In this mode DofFile creates its own parts as empty instances.
                If you want to create a new DofFile, you should use this
                instantiation method.
            2.  Normal mode with some arguments:
                In this mode DofFile creates its own parts as empty instances
                and accepts parts already instantiated. This is useful e.g. if a
                new DofFile is created with an existing dataset.
            3.  Restore mode:
                In this mode DofFile requires all parts to be already
                instantiated. This mode is used to re-generate DofFile from
                any kind of stored form.
                This mode is mainly used by external instantiation methods like
                DofiFile.from_file() or DofFile.from_json() only.
        """

        self.__dataset = None
        self.__info = None
        self.__documents = None
        self.__model_info = None
        self.__at = 0
        for index, arg in enumerate(args):
            if isinstance(arg, Dataset):
                self.__dataset = arg
            elif isinstance(arg, ContainerInfo):
                self.__info = arg
            elif isinstance(arg, DocumentContainer):
                self.__documents = arg
            elif isinstance(arg, ModelInfo):
                self.__model_info = arg
            else:
                raise DofError('DofFile.init(): unsupported instance type is ' +
                               '"{}" is given at position {}.'
                               .format(type(arg), index))
        if restore_mode:
            errormessage = self.__check_attributes()
            if len(errormessage) > 0:
                raise DofError('DofFile.init(restore_mode): ' +
                               '\n'.join(errormessage))
        else:
            self.__create_attributes()
        if not isdir(dof_basepath):
            mkdir(dof_basepath)
        self.__dof_basepath = dof_basepath
        self.__handler_id = DofObject.add_handler(
                            LocalHandler(self.__dof_basepath), as_default=False)


    def check(self) -> tuple:

        """
        basic check method for DofFile
        ==============================

        Returns
        -------
        tuple(bool, dict)
            Results of checks. First value of tuple is an overall result. The
            dictionary contains any results.
            ((True | False), {'has_data' : (True | False),
                              'has_links' : (True | False),
                              'has_complete_info' : (True | False)})
            First value is True if all checks are True.
        """

        has_data = self.__dataset.count_all() > 0
        has_links = len(self.__dataset.linker) > 0
        has_complete_info = self.__info.is_complete()
        return (all([has_data, has_links, has_complete_info]),
                {'has_data' : has_data, 'has_links' : has_links,
                 'has_complete_info' : has_complete_info})


    @property
    def dataset(self) -> Dataset:
        """
        Provide access to the dataset of the DofFile
        ============================================

        Returns
        -------
        Dataset
            The dataset of the instance.
        """

        return self.__dataset


    @property
    def documents(self) -> DocumentContainer:
        """
        Provide access to the document container of the DofFile
        =======================================================

        Returns
        -------
        DocumentContainer
            The document container of the instance.
        """

        return self.__documents


    @property
    def dof_basepath(self) -> str:
        """
        Get the value of working directory
        ==================================

        Returns
        -------
        str
            Path to the working directory of DoF.
        """

        return self.__dof_basepath


    @dof_basepath.setter
    def dof_basepath(self, new_path : str):
        """
        Set the value of working directory
        ==================================

        Parameters
        ----------
        new_path : str
            Base path of the DoF.
        """

        if not isdir(new_path):
            mkdir(new_path)
        self.__dof_basepath = new_path
        self.__handler_id = DofObject.add_handler(
                            LocalHandler(self.__dof_basepath), as_default=True)


    @staticmethod
    def from_file(filename : str, file_type : str = '',
                  dof_basepath : str = '!') -> any:
        """
        Create DoF file from a file
        ===========================

        Parameters
        ----------
        filename : str
            Filename to load.
        file_type : str, optional (empty string if omitted)
            Extension of file.
        dof_basepath : str, optional ('!' if omitted)
            Base directory of the content of the DofFile.

        Returns
        -------
        DofFile
            The loaded object.

        Raises
        ------
        DofError
            When the extension of file is not supported.
        DofError
            In autodetect mode the extension of file cannot be detected.
        DofError
            The content of source file is invalid.

        See Also
        --------
            Possible value of file extensions : class DofFile

        Notes
        -----
            When the file_type is an empty string, the function works in
            autodetect mode.
        """
        if file_type not in [DofFile.DOF_AUTODETECT, DofFile.DOF_FILE,
                             DofFile.DOF_JSON, DofFile.DOF_PYTHON]:
            raise DofError('DofFile.from_file(): unsupported file type.')
        if file_type == DofFile.DOF_AUTODETECT:
            _, _file_type = splitext(filename)
            if _file_type not in [DofFile.DOF_FILE, DofFile.DOF_JSON,
                                  DofFile.DOF_PYTHON]:
                raise DofError('DofFile.from_file(): cannot autodetect file ' +
                               'type.')
        else:
            _file_type = file_type
        if _file_type == DofFile.DOF_FILE:
            _handler_id = DofObject.add_handler(LocalHandler(dof_basepath))
            _handler = DofObject.get_handler(DofObjectHandler.LOCAL,
                                             _handler_id)
            with ZipFile(filename, 'r') as instream:
                _dof_basepath = instream.read('dof.basepath')
                if dof_basepath != '!':
                    _dof_basepath = dof_basepath
                instream.extractall(_dof_basepath)
            _handler_id = DofObject.add_handler(LocalHandler(_dof_basepath))
            _handler = DofObject.get_handler(DofObjectHandler.LOCAL,
                                                                _handler_id)
            _dataset = Dataset()
            _dataset.load_from(_handler_id)
            _docments = _handler.load_as_instance('dof.documents')
            _info = _handler.load_as_instance('dof.info')
            _model_info = _handler.load_as_instance('dof.modelinfo')
            result = DofFile(_dataset, _docments, _info, _model_info,
                             dof_basepath=_dof_basepath)
        elif _file_type == DofFile.DOF_JSON:
            with open(filename, 'r') as instream:
                json_string = instream.read()
            result = DofFile.from_json(json_string)
        elif _file_type == DofFile.DOF_PYTHON:
            with open(filename, 'rb') as instream:
                result = pickle_load(instream)
        if not isinstance(result, DofFile):
            raise DofError('DofFile.from_file(): got invalid instance.')
        return result


    @classmethod
    def from_json(cls, json_string : str, **kwargs) -> any:
        """
        Create DoF file from JSON string
        ================================

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
            When the description field is not complete.
        DofError
            When the dof_basepath is missing from the given JSON.
        DofError
            When the dataset field is missing from the given JSON.
        DofError
            When the info field is missing from the given JSON.
        DofError
            When the documents field is missing from the given JSON.
        DofError
            When the model_info field is missing from the given JSON.
        """

        json_dict = json_loads(json_string, **kwargs)
        data = get_content(json_dict, 'DofFile', 'dof.file',
                           describe_only=False)
        if data is None:
            raise DofError('DofFile.from_json(): JSON string is not valid' +
                           'to create an instance.')
        if json_dict.get(JSONRoot.DESCRIPTION) is None:
            raise DofError('DofFile.from_json(): JSON string is missing ' +
                           'description field.')
        _dof_basepath = json_dict[JSONRoot.DESCRIPTION].get(
                                                JSONDescription.DOF_BASEPATH)
        if _dof_basepath is None:
            raise DofError('DofFile.from_json(): description field in JSON ' +
                           'string doesn\'t contain the DoF base path.')
        _dataset_raw = data.get(JSONContent.DOF_DATASET.value)
        if _dataset_raw is None:
            raise DofError('DofFile.from_json(): JSON string content doesn\'t' +
                           'contain dataset field.')
        _info_raw = data.get(JSONContent.DOF_INFO.value)
        if _info_raw is None:
            raise DofError('DofFile.from_json(): JSON string content doesn\'t' +
                           'contain dof file info field.')
        _documents_raw = data.get(JSONContent.DOF_DOCUMENTS.value)
        if _documents_raw is None:
            raise DofError('DofFile.from_json(): JSON string content doesn\'t' +
                           'contain documents field.')
        _model_raw = data.get(JSONContent.DOF_MODEL_INFO.value)
        if _model_raw is None:
            raise DofError('DofFile.from_json(): JSON string content doesn\'t' +
                           'contain model info field.')
        return DofFile(Dataset.from_json(_dataset_raw),
                       ContainerInfo.from_json(_info_raw),
                       DocumentContainer.from_json(_documents_raw),
                       ModelInfo.from_json(_model_raw),
                       dof_basepath=_dof_basepath, restore_mode=True)


    @property
    def info(self) -> ContainerInfo:
        """
        Provide access to the information container of the DofFile
        ==========================================================

        Returns
        -------
        ContainerInfo
            The dataset level information container.
        """

        return self.__info


    def load(self, filename : str, file_type : str = '',
             dof_basepath : str = '!'):
        """
        Load the content of the instance from file
        ==========================================

        Parameters
        ----------
        filename : str
            Filename to load.
        file_type : str, optional (empty string if omitted)
            Extension of file.
        dof_basepath : str, optional ('!' if omitted)
            Base directory of the content of the DofFile.

        See Also
        --------
            Possible value of file extensions : class DofFile

        Notes
        -----
            When the file_type is an empty string, the function works in
            autodetect mode.
        """
        other = self.from_file(filename, file_type, dof_basepath)
        self.__dataset = other.dataset
        self.__documents = other.documents
        self.__dof_basepath = other.dof_basepath
        self.__info = other.info
        self.__model_info = other.model_info


    @property
    def model_info(self) -> ModelInfo:
        """
        Provide access to the model informations of the DofFile
        =======================================================

        Returns
        -------
        ModelInfo
            The model informations of the instance.
        """

        return self.__model_info


    def report(self, **kwargs) -> str:
        """
        Make a detailed report about the DofFile
        ========================================

        Parameters
        ----------
        keyword arguments
            Arguments to forward to json.dumps() funtion.

        Returns
        -------
        str
            Well structured and formatted report.

        Notes
        -----
            The output of this function is suitable for post-processing to
            provide extra gateway layer towards any 3rd party softwares.
        """

        result = self.to_json_dict(describe_only=False)
        for key in result[JSONRoot.CONTENT.value][JSONContent.DOF_DATASET
                          .value][JSONRoot.CONTENT.value][JSONContent.ELEMENTS
                          .value].keys():
            del result[JSONRoot.CONTENT.value][JSONContent.DOF_DATASET.value][
                       JSONRoot.CONTENT.value][JSONContent.ELEMENTS.value][
                       key][JSONRoot.CONTENT.value]
        for key in result[JSONRoot.CONTENT.value][JSONContent.DOF_DOCUMENTS
                          .value][JSONRoot.CONTENT.value].keys():
            del result[JSONRoot.CONTENT.value][JSONContent.DOF_DOCUMENTS.value][
                       JSONRoot.CONTENT.value][key][JSONRoot.CONTENT.value]
        for key, value in result[JSONRoot.CONTENT.value][JSONContent
                                 .DOF_MODEL_INFO.value][JSONRoot.CONTENT.value][
                                 JSONContent.MODEL_INFO.value].items():
            if not isinstance(value, str):
                del result[JSONRoot.CONTENT.value][JSONContent.DOF_MODEL_INFO
                           .value][JSONRoot.CONTENT.value][JSONContent
                           .MODEL_INFO.value][key]
        for key, value in result[JSONRoot.CONTENT.value][JSONContent
                                 .DOF_MODEL_INFO.value][JSONRoot.CONTENT.value][
                                 JSONContent.MODEL_DATA_PROCESSING.value
                                 ].items():
            if not isinstance(value, str):
                del result[JSONRoot.CONTENT.value][JSONContent.DOF_MODEL_INFO
                           .value][JSONRoot.CONTENT.value][JSONContent
                           .MODEL_DATA_PROCESSING.value][key]
        for key, value in result[JSONRoot.CONTENT.value][JSONContent
                                 .DOF_MODEL_INFO.value][JSONRoot.CONTENT.value][
                                 JSONContent.MODEL_PERFORMANCE.value].items():
            if not isinstance(value, str):
                del result[JSONRoot.CONTENT.value][JSONContent.DOF_MODEL_INFO
                           .value][JSONRoot.CONTENT.value][JSONContent
                           .MODEL_PERFORMANCE.value][key]
        for key, value in result[JSONRoot.CONTENT.value][JSONContent
                                 .DOF_MODEL_INFO.value][JSONRoot.CONTENT.value][
                                 JSONContent.MODEL_TRAINING.value].items():
            if not isinstance(value, str):
                del result[JSONRoot.CONTENT.value][JSONContent.DOF_MODEL_INFO
                           .value][JSONRoot.CONTENT.value][JSONContent
                           .MODEL_TRAINING.value][key]
        return json_dumps(result, **kwargs)


    def save(self, filename : str, file_type : str = '',
             halt_if_not_in_memory : bool = False,
             verbose_memory_state : bool = False):
        """
        Parameters
        ----------
        filename : str
            Filename to load.
        file_type : str, optional (empty string if omitted)
            Extension of file.
        halt_if_not_in_memory : bool, optional (False if omitted)
            Whether to stop the function if load into memory process failed.
        verbose_memory_state : bool, optional (False if omitted)
        Whether to write error message if load into memory process failed.

        Returns
        -------
        DofFile
            The loaded object.

        Raises
        ------
        DofError
            When the extension of file is not supported.
        DofError
            In autodetect mode the extension of file cannot be detected.
        DofError
            When some object could not be loaded into memory and
            halt_if_not_in_memory flag is True.

        See Also
        --------
            Possible value of file extensions : class DofFile

        Notes
        -----
        I.
            When the file_type is an empty string, the function works in
            autodetect mode.
        II.
            When verbose_memory_state is True and some object could not be
            loaded into memory, code give only a printed message as feedback. If
            you want to avoid the possibility of some data might won't be saved,
            turn halt_if_not_in_memory flag to True.
        """

        if file_type not in [DofFile.DOF_AUTODETECT, DofFile.DOF_FILE,
                             DofFile.DOF_JSON, DofFile.DOF_PYTHON]:
            raise DofError('DofFile.save(): unsupported file type.')
        if file_type == DofFile.DOF_AUTODETECT:
            _, _file_type = splitext(filename)
            if _file_type not in [DofFile.DOF_FILE, DofFile.DOF_JSON,
                                  DofFile.DOF_PYTHON]:
                raise DofError('DofFile.save(): cannot autodetect file type.')
        else:
            _file_type = file_type
        _in_memory = all([self.__dataset.force_load_to_memory(),
                          self.__documents.force_load_to_memory(),
                          self.__model_info.force_load_to_memory()])
        if verbose_memory_state and not _in_memory:
            print('DofFile.save(): failed to load objects into the memory, ' +
                  'some data might not get saved.')
        if halt_if_not_in_memory and not _in_memory:
            raise DofError('DofFile.save(): failed to load objects into the ' +
                           'memory.')
        if file_type == DofFile.DOF_FILE:
            self.save_as_dof_file(filename)
        elif file_type == DofFile.DOF_JSON:
            with open(filename, 'w') as outstream:
                outstream.write(self.to_json(describe_only=False))
        elif file_type == DofFile.DOF_PYTHON:
            with open(filename, 'wb') as outstream:
                pickle_dump(self, outstream)


    def save_as_dof_file(self, filename : str):
        """
        Parameters
        ----------
        filename : str
            Filename to load.

        Returns
        -------
        DofFile
            The loaded object.

        Raises
        ------
        DofError
            When the extension of file is not supported.
        DofError
            In autodetect mode the extension of file cannot be detected.
        DofError
            When some object could not be loaded into memory and
            halt_if_not_in_memory flag is True.
        """

        self.__dataset.save_to(self.__handler_id)
        _handler = DofObject.get_handler(DofObjectHandler.LOCAL,
                                         self.__handler_id)
        _handler.save_as_instance(self.__documents, 'dof.documents')
        _handler.save_as_instance(self.__dof_basepath, 'dof.basepath')
        _handler.save_as_instance(self.__info, 'dof.info')
        _handler.save_as_instance(self.__model_info, 'dof.modelinfo')
        _files = _handler.files('')
        with ZipFile(filename, 'w', allowZip64=True) as outstream:
            for _filename in _files:
                outstream.writestr(_filename,
                                   _handler.load_as_binary(_filename))


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
        return json_dumps(data, **kwargs)


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
            result = create_json_dict('DofFile', 'dof.file', describe_only,
                                      description=
                                      [(JSONDescription.DOF_BASEPATH,
                                        self.dof_basepath)])
        else:
            result = create_json_dict('DofFile', 'dof.file', describe_only,
                                      content_form=
                                                ContentForm.MULTIPLE_INSTANCES,
                                      description=
                                      [(JSONDescription.DOF_BASEPATH,
                                        self.dof_basepath)])
            _content = {JSONContent.DOF_DATASET.value :
                        self.__dataset.to_json_dict(describe_only),
                        JSONContent.DOF_INFO.value :
                        self.__info.to_json_dict(describe_only),
                        JSONContent.DOF_DOCUMENTS.value :
                        self.__documents.to_json_dict(describe_only),
                        JSONContent.DOF_MODEL_INFO.value :
                        self.__model_info.to_json_dict(describe_only)}
            result[JSONRoot.CONTENT.value] = _content
        return result


    def __check_attributes(self) -> list:
        """
        Check the missing attributes
        ============================

        Returns
        -------
        list[str]
            List of error mesaage alike text about instances that are missing.
            Empty list if nothing is missing.
        """

        result = []
        if self.__dataset is None:
            result.append('No Dataset is given.')
        if self.__info is None:
            result.append('No ContainerInfo is given.')
        if self.__documents is None:
            result.append('No DocumentContainer is given.')
        if self.__model_info is None:
            result.append('No ModelInfo is given.')
        return result


    def __create_attributes(self):
        """
        Create all instance attributes
        ==============================
        """

        if self.__dataset is None:
            self.__dataset = Dataset()
        if self.__info is None:
            self.__info = ContainerInfo()
        if self.__documents is None:
            self.__documents = DocumentContainer()
        if self.__model_info is None:
            self.__model_info = ModelInfo()


    def __getitem__(self, id_to_get : int) -> any:
        """
        Get an item from the dataset
        ============================

        Parameters
        ----------
        id_to_get : int | slice | tuple
            The identyfier(s) of the connection(s) to get the every information
            about the connected elements.

        Returns
        -------
        tuple(tuple(DataElement, DataElementInfo | None, list | None),
              tuple(DataElement, DataElementInfo | None, list | None)) |
        list[tuple(tuple(DataElement, DataElementInfo | None, list | None),
             tuple(DataElement, DataElementInfo | None, list | None))]
            The pair of full information of the connected dataset elements or
            list of pairs of full information of the connected dataset elements.

        See Also
        --------
            Get connected elements : data.Dataset.__getitem__()
            Get the id of the connected elements : data.LinkEngine.__getitem__()
        """

        if isinstance(id_to_get, int):
            _x, _y = self.__dataset.linker[id_to_get]
            result = (self.__dataset.get_everything_by_id[_x],
                      self.__dataset.get_everything_by_id[_y])
        else:
            result = []
            for _x, _y in self.__dataset.linker[id_to_get]:
                result.append((self.__dataset.get_everything_by_id[_x],
                               self.__dataset.get_everything_by_id[_y]))
        return result


    def __iter__(self) -> any:
        """
        Return iterator
        ===============

        Returns
        -------
        Iterator
            The complex iterator object connected to the dataset.
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
            Get back the number of Xs and Ys : data.Dataset.describe()

        Notes
        -----
            Length of dataset equals with the count of all connections in the
            dataset since only the connected Xs and Ys can be used for training
            or validating purposes. If you want to get back the number of X and
            Y values, use describe() function from the dataset.
        """

        return len(self.__dataset.linker)


    def __next__(self) -> tuple:
        """
        Perform next on the dataset
        ===========================

        Returns
        -------
        tuple(tuple(DataElement, DataElementInfo | None, list | None),
              tuple(DataElement, DataElementInfo | None, list | None))
            The pair of full information of the connected dataset elements.

        Raises
        ------
        StopIteration
            If iteration is finished.

        See Also
        --------
            Iterate over elements : data.Dataset.__next__()
            Iterate over ids : data.LinkEngine.__next__()

        Notes
        -----
        I.
            The raise of StopIteration is the canonical way to well implement
            iteration. It doesn't stops the run of the code.
        II.
            DofFile, dataset and linker engine have separate iteration it is
            recommended not to mix the call of them in the same loop.
        """

        dof_at = self.__at
        self.__at += 1
        if self.__at == len(self.__dataset):
            self.__at = 0
            raise StopIteration
        _x, _y = self.__dataset.linker[dof_at]
        return (self.__dataset.get_everything_by_id[_x],
                self.__dataset.get_everything_by_id[_y])


if __name__ == '__main__':
    pass
