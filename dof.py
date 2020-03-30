"""
        _                 _
       (_)               | |
 _ __   _  __  __   ___  | |
| '__| | | \ \/ /  / _ \ | |
| |    | |  >  <  |  __/ | |
|_|    |_| /_/\_\  \___| |_|

DoF - Deep Model Core Output Framework
--------------------------------------

Copyright rixel 2020
Distributed under the MIT License.
See accompanying file LICENSE.
"""



# Modul level constants.
__author__ = 'rixel'
__copyright__ = "Copyright 2020, DoF - Deep Model Core Output Framework"
__credits__ = ['rixel']
__license__ = 'MIT'
__version__ = '1.0'
__status__ = 'Beta'



# Imports from standard library
import json
from os import listdir, mkdir
from os.path import abspath, exists, isdir, isfile, join, splitext
import pickle
from shutil import rmtree
from zipfile import BadZipfile, ZipFile, ZIP_DEFLATED



class DofError(Exception):
    """
    Simple empty class to provide unique exception for the module
    -------------------------------------------------------------
    Subclass of Exception
    """

    pass



class DofInfo(dict):
    """
    Stores information about DoF dataset
    ------------------------------------
    Subclass of dict
    """



    def __init__(self, *args, **kwargs):
        """
        Initializes the class
        ---------------------
        @Params: positional ([dict])    List if dict with length 1. (This way
                                        is reserved for DofFile read mode.)
                 key, value pairs       Keys and values to add basic and more
                                        advanced information to dataset.
                                        Required keys are: coremodel_family,
                                        coremodel_type, coremodel_common,
                                        original_author, original_source,
                                        original_license, dof_author,
                                        dof_author_contact, dof_source and
                                        dof_license. In case if coremodel_common
                                        is False coremodel_source_architecture
                                        and coremodel_source_weightsandbiases
                                        are also required.
        @Raises: DofError               If required key is missing.
                                        If coremodel_common is not a bool.
        """

        super(self.__class__, self).__init__()
        if len(args) > 0:
            if len(args) == 1 and isinstance(args[0], dict):
                for key, value in args[0].items():
                    self[key] = value
            else:
                raise DofError('DofInfo: only 1 positional argument accepted and it should be a dict')
        else:
            required = ['coremodel_family', 'coremodel_type', 'coremodel_common',
                        'original_author', 'original_source', 'original_license',
                        'dof_author', 'dof_author_contact', 'dof_source', 'dof_license']
            for key in required:
                if key in kwargs:
                    self[key] = kwargs[key]
                else:
                    raise DofError('DofInfo: required key "{}" doesn\'t set.'.format(key))
            if not isinstance(self['coremodel_common'], bool):
                raise DofError('DofInfo: coremodel_common must be bool.')
            if not self['coremodel_common']:
                for key in ['coremodel_source_architecture', 'coremodel_source_weightsandbiases']:
                    if key in kwargs:
                        self[key] = kwargs[key]
                    else:
                        raise DofError('DofInfo: key "{}" is required when coremodel is not common.'.format(key))
            for key, value in kwargs.items():
                if key not in required:
                    self[key] = value



class DofElementInfo(dict):
    """
    Stores information about DoF dataset elements
    ---------------------------------------------
    Subclass of dict
    """



    def __init__(self, **kwargs):
        """
        Initializes the class
        ---------------------
        @Params: key, value pairs       Keys and values to add basic and more
                                        advanced information to dataset element.
                                        Required keys are: author,
                                        author_contact, source and license.
        @Raises: DofError               If required key is missing.
        """

        super(self.__class__, self).__init__()
        required = ['author', 'author_contact', 'source', 'license']
        for key in required:
            if key in kwargs:
                self[key] = kwargs[key]
            else:
                raise DofError('DofElemInfo: required key "{}" doesn\'t set.'.format(key))
        for key, value in kwargs.items():
            if key not in required:
                self[key] = value



class DofFile(object):
    """
    Manages Dof files
    -----------------
    """



    # Class level mode constants
    READ = 'r'
    WRITE = 'w'



    def __init__(self, *args, dataset_path='./dataset', use_compressed=False):
        """
        Initializes the class
        ---------------------
        @Params: positional ([string[2]])   Required argument(s). In read mode
                                            1 argument DofFile.READ is enough if
                                            dataset folder contains a fully
                                            extracted DoF dataset. If 2 argument
                                            is given, 1st argument is treated as
                                            the name of the DoF file to read or
                                            write and the 2nd argument is the
                                            access mode selector.
                 dataset_path (string)      [optional] Path to the dateset to
                                            locate incoming or outgoing files.
                 use_compressed (bool)      [optional] Sets dataset usage. If
                                            True files are extracted temporarily
                                            only. If False, files are extracted
                                            at the first use of Dof file, afterwards
                                            they are loaded from dataset directory.
                                            At the moment use_compressed=False
                                            is implemented only.
        @Raises: DofError                   If more tham 2 positional argument is given.
                                            If invalid mode is given.
                                            If uncompressed dataset doesn't contain
                                            required core elements.
                                            If the given file is not a DoF file.
                                            If tried to acces uncompressed mode.
                                            If the given file deosn't exist.
                                            If final check fail in read mode.
                                            If given filename is empty in write mode.
                                            If given dataset path is not empty
                                            in write mode.

        """

        if len(args) == 1:
            filename = ''
            mode = args[0]
        elif len(args) == 2:
            filename = args[0]
            mode = args[1]
        else:
            raise DofError('DofFile: accepts 1 or 2 position arguments but {} were given.'
                           .format(len(args)))
        self.__filename = filename
        self.__use_compressed = False
        # Will be out-remarked if runtime mode change is implemented.
        # self.use_compressed(use_compressed)
        self.__dataset_path = dataset_path
        if mode == DofFile.READ or mode == DofFile.WRITE:
            self.__mode = mode
        else:
            raise DofError('DofFile: invalid mode: "{}".'.format(mode))
        if self.__mode == DofFile.READ:
            if filename == '':
                if isfile(join(self.__dataset_path, '.dofinfo', 'elementslist.json')):
                    with open(join(self.__dataset_path, '.dofinfo', 'elementslist.json'), 'r') as instream:
                        self.__elementslist = json.load(instream)
                else:
                    raise DofError('DofFile: uncompressed dataset doesn\'t contain list of elements.')
                if isfile(join(self.__dataset_path, '.dofinfo', 'dataset.json')):
                    with open(join(self.__dataset_path, '.dofinfo', 'dataset.json'), 'r') as instream:
                        self.__dataset_info = json.load(instream)
                else:
                    raise DofError('DofFile: uncompressed dataset doesn\'t contain dataset info.')
            elif isfile(filename):
                try:
                    doffile = ZipFile(self.__filename, 'r', allowZip64=True)
                    self.__elementslist = json.loads(doffile.read('.dofinfo/elementslist.json'))
                    self.__dataset_info = DofInfo(json.loads(doffile.read('.dofinfo/dataset.json')))
                except BadZipfile:
                    raise DofError('DofFile: File "{}" is not a DoF file.'.format(filename))
                if not self.__use_compressed:
                    if isdir(self.__dataset_path):
                        for name in doffile.namelist():
                            if not exists(join(self.__dataset_path, name)):
                                doffile.extract(name, self.__dataset_path)
                    else:
                        mkdir(self.__dataset_path)
                        doffile.extractall(self.__dataset_path)
                else:
                    raise DofError('DofFile: compressed use not implemented yet.')
                doffile.close()
            else:
                raise DofError('DofFile: File "{}" doesn\'t exist.'.format(filename))
            if not self.check():
                raise DofError('DofFile: final check failed at init.')
            for i in range(len(self.__elementslist)):
                if len(self.__elementslist[i]) == 1:
                    self.__elementslist[i].append(None)
        elif self.__mode == DofFile.WRITE:
            if filename == '':
                raise DofError('DofFile: tried to set empty filename in write mode.')
            elif isfile(filename):
                name, extension = splitext(filename)
                i = 0
                while isfile('{}_{}.{}'.format(name, i, extension)):
                    i += 1
                self.__filename = '{}_{}.{}'.format(name, i, extension)
                print('DofFile: "{}" is not empty, using "{}" instead.'
                      .format(filename, self.__filename))
            if isdir(self.__dataset_path):
                if len(listdir(self.__dataset_path)) > 0:
                    raise DofError('DofFile: dataset path "{}" is not empty.'.format(self.__dataset_path))
            else:
                mkdir(self.__dataset_path)
            self.__elementslist = []
            self.__dataset_info = None
        self.__element_at = 0



    def append(self, data):
        """
        Appends the dataset with element(s)
        -----------------------------------
        @Params: data (DofElement | numpy.ndarray)  Data element(s) to add. It can
                                                    be a single DofElement or
                                                    a batch of tensors.
        @Raises: DofError                           If called in other than write mode.
                                                    If data has invalid type.
                                                    If x and y have different shape.
        """

        if self.__mode is not DofFile.WRITE:
            raise DofError('DofFile.append() this function is available in write mode only.')
        if isinstance(data, DofElement):
            if data.islink():
                self.__elementslist.append([data.y(), data.info(), data.link()])
            else:
                with open(join(self.__dataset_path, '{}.out'.format(len(self.__elementslist))), 'wb') as outstream:
                    pickle.dump(data.x(), outstream)
                self.__elementslist.append([data.y(), data.info()])
        elif isinstance(data, tuple):
            if hasattr(data[0], 'shape') and hasattr(data[1], 'shape'):
                if data[0].shape[0] == data[1].shape[0]:
                    for x, y in zip(data[0], data[1]):
                        with open(join(self.__dataset_path, '{}.out'.format(len(self.__elementslist))), 'wb') as outstream:
                            pickle.dump(x, outstream)
                        self.__elementslist.append([y.tolist(), None])
                else:
                    raise DofError('DofFile.append() x and y must have same 1st dimension.')
            else:
                raise DofError('DofFile.append() elements of tuple must have "shape" attribute.')
        else:
            raise DofError('DofFile.append() data must be DofElement or tuple.')



    def check(self):
        """
        Checks if Dof dataset is ready for use or save
        ----------------------------------------------
        @Return: (bool)     True if elements, dataset info and data files exist
                            False in other cases.
        @Raises: DofError   If called in other than uncompressed read mode.
        """

        if self.__mode == DofFile.READ and not self.__use_compressed:
            if not isfile(join(self.__dataset_path, '.dofinfo', 'elementslist.json')):
                return False
            if not isfile(join(self.__dataset_path, '.dofinfo', 'dataset.json')):
                return False
            for i, element in enumerate(self.__elementslist):
                if len(element) == 3:
                    filename = element[2]
                else:
                    filename = join(self.__dataset_path, '{}.out'.format(i))
                if not isfile(filename):
                    return False
            return True
        else:
            raise DofError('DofFile.check() only not compressed read mode is implemented yet.')



    def delete(self, id):
        """
        Removes an element from the dataset
        -----------------------------------
        @Params: id (int)   Index of the element.
        @Raises: DofError   If index is less than 0 or bigger than last data index.
        """

        if id >= len(self.__elementslist) or id < 0:
            raise DofError('DofFile.delete() element\'s index #{} out of range.'.format(id))
        self.__elementslist.pop(id)



    def filename(self):
        """
        Gets dataset's DoF file name
        ----------------------------
        @Return: (string)   Name of the file.
        """

        return self.__filename




    def info(self, newvalue=None):
        """
        Gets or sets the dataset level information
        -------------------------------------------
        @Params: newvalue   (DofInfo | None)    If DofInfo instance is given, it
                                                is set as new dataset info.
                                                If None is given, the current
                                                dataset info is returned.
        @Return: (DofInfo)                      Dataset info or None.
        @Raises: DofError                       If type of newvalue is invalid.
        """

        if isinstance(newvalue, DofInfo):
            self.__dataset_info = newvalue
        elif newvalue is None:
            return self.__use_compressed
        else:
            raise DofError('DofFile.info() to set info DofInfo is needed not "{}".'
                           .format(type(newvalue)))



    def mode(self, mode=None):
        """
        Gets or sets the Dof manager mode
        ---------------------------------
        @Params: mode   (str | None)    If mode is DofFile.READ or DofFile.WRITE
                                        new mode will be set in the future but
                                        at the time this is not allowed. If None
                                        is given the current mode is returned.
        @Return: (DofInfo)              DoF acces mode or None.
        @Raises: DofError               If mode value is invalid.
        """

        if mode == DofFile.READ or mode == DofFile.WRITE:
            raise DofError('DofFile.mode(): runtime mode change not implemented yet.')
            # self.__mode = mode
        elif mode is None:
            return self.__mode
        else:
            raise DofError('DofFile.mode(): Invalid mode "{}".'.format(mode))



    def save(self, remove_dataset_dir=False):
        """
        Saves the dataset to a DoF file
        -------------------------------
        @Params: remove_dataset_dir (bool)  Whether or not dataset directory
                                            should be removed at the and of save.
        @Raises: DofError                   If not in write mode.
                                            If dataset info is missing.
                                            If dataset is empty.
                                            If target file already exists.
        """

        if self.__mode is not DofFile.WRITE:
            raise DofError('DofFile.save() this function is available in write mode only.')
        if self.__dataset_info is None:
            raise DofError('DofFile.save() cannot save without dataset DofInfo.')
        if len(self.__elementslist) == 0:
            raise DofError('DofFile.save() cannot save empty dataset.')
        if isfile(self.__filename):
            raise DofError('DofFile.save() target file "{}" already exists.'
                           .format(self.__filename))
        elementslist = []
        filelist = []
        for i, element in enumerate(self.__elementslist):
            if len(element) == 3:
                filename = element[2]
            else:
                filename = join(self.__dataset_path, '{}.out'.format(i))
            filelist.append([filename, '{}.out'.format(i)])
            if hasattr(element[0], 'tolist'):
                y = element[0].tolist()
            else:
                y = element[0]
            if element[1] is None:
                elementslist.append([y])
            else:
                elementslist.append([y, element[1]])

        with ZipFile(self.__filename, 'w', allowZip64=True) as outstream:
            outstream.writestr('.dofinfo/dataset.json', json.dumps(self.__dataset_info, indent=1))
            outstream.writestr('.dofinfo/elementslist.json', json.dumps(elementslist, indent=1))
            for filedata in filelist:
                outstream.write(filedata[0], filedata[1])
        if remove_dataset_dir:
            rmtree(self.__dataset_path)




    def use_compressed(self, newvalue=None):
        """
        Gets or sets the Dof uncompressed mode
        --------------------------------------
        @Params: newvalue   (bool | None)   If newvalue is bool the new mode will be
                                            set in the future but at the moment it
                                            is not implemented yet. If None is given
                                            it returns the current use_compressed
                                            state.
        @Return: (bool | None)              The use_compressed state or None.
        @Raises: DofError                   If tried to set the value.
                                            If use_compressed value is invalid.
        """

        if isinstance(newvalue, bool):
            raise DofError('DofFile.use_compressed() compressed use not implemented yet.')
            # self.__use_compressed = newvalue
        elif newvalue is None:
            return self.__use_compressed
        else:
            raise DofError('DofFile.use_compressed() to set compression bool is needed not "{}".'
                           .format(type(newvalue)))



    def __getitem__(self, id):
        """
        Gets an item
        ------------
        @Params: id (int)           The id of the element to return.
        @Return: (object, object)   The x and y values of the element.
        @Raises: DofError           If index is less than 0 or bigger than last data index.
        """

        if id >= len(self.__elementslist) or id < 0:
            raise DofError('DofFile.get() element\'s index #{} out of range.'.format(id))
        if len(self.__elementslist[id]) == 3:
            filename = self.__elementslist[id][2]
        else:
            filename = join(self.__dataset_path, '{}.out'.format(id))
        with open(filename, 'rb') as instream:
            data = pickle.load(instream)
        return data, self.__elementslist[id][0]



    def __iter__(self):
        """
        Gets an iterable instance
        -------------------------
        @Return: (DofFile)  This instance.
        """

        return self



    def __len__(self):
        """
        Gets the length of the dataset
        ------------------------------
        @Return: (int)  Count of elements in the dataset.
        """

        return len(self.__elementslist)



    def __next__(self):
        """
        Gets next element
        -----------------
        @Return: (object, object)   The x and y values of the element.
        @Raises: StopIteration      If the end of the dataset is reached.
        """

        if self.__element_at == len(self.__elementslist):
            self.__element_at = 0
            raise StopIteration
        else:
            self.__element_at += 1
            return self.__getitem__(self.__element_at - 1)



class DofElement(object):
    """
    Represents a dataset element
    ----------------------------
    """



    def __init__(self, x, y, info=None):
        """
        Initializes the class
        ---------------------
        @Params: x      (object | string)       The x value of the element or the
                                                path to the file with the value.
                 y      (object)                The corresponding y value.
                 info   (DofElementInfo | None) [optional] Additional info to the
                                                element or None.
        @Raises: DofError                       If the given file link points to
                                                not existing file.
        """

        if isinstance(x, str):
            self.__x = None
            if isfile(x):
                self.__link = x
            else:
                raise DofError('DofElement: File "{}" doesn\'t exist.'.format(filename))
        else:
            self.__x = x
            self.__link = None
        self.__y = y
        if info is not None and not isinstance(info, DofElementInfo):
            raise DofError('DofElement: info should be DofElemInfo or None.')
        self.__info = info



    def info(self):
        """
        Gets the info of the elemnt
        ---------------------------
        @Return: (DofElemInfo | None)   The value of hte element's info or None.
        """

        return self.__info



    def islink(self):
        """
        Gets whether element contains data or link to data.
        ---------------------------------------------------
        @Return: (bool)     True if element is a link only, False else.
        """

        return self.__link is not None



    def link(self):
        """
        Gets the link to the elemnt's x value content
        ---------------------------------------------
        @Return: (string)   Path to element's x value.
        @Raises: DofError   If the element is not a link element.
        """

        if self.__link is not None:
            return self.__link
        else:
            raise DofError('DofElement.link() tried to get link from an element with content.')



    def x(self):
        """
        Gets x value
        ------------
        @Return: (object)   The x value of the element.
        """

        if self.__x is not None:
            return self.__x
        else:
            with open(self.__path, 'rb') as instream:
                data = pickle.load(instream)
            return data



    def y(self):
        """
        Gets y value
        ------------
        @Return: (object)   The y value of the element.
        """

        return self.__y
