"""
DoF - Deep Model Core Output Framework
======================================

Submodule: datamodel
"""


from enum import Enum

from . import __version__


class ContentForm(Enum):
    """
    Provide constants for JSON output content form
    ==============================================

    Notes
    -----
        The meaning of nomenclature.
            BINARY : binary data only
            PICKLE_BINARY : pickle binary data only
            TEXTUAL : textual data only
            INSTANCE : one instance data only
            MULTIPLE_INSTANCES : multiple instances data
            MIXED_BINARY : binary and textual data
            MIXED_PICKLE : pickle binary and textual data
    """

    BINARY = 'binary'
    PICKLE_BINARY = 'pickle_binary'
    TEXTUAL = 'textual'
    INSTANCE = 'instance'
    MULTIPLE_INSTANCES = 'multiple_instances'
    MIXED_BINARY = 'mixed_binary'
    MIXED_PICKLE = 'mixed_pickle'


class JSONContent(Enum):
    """
    Provide constants for content fields of JSON in case of multiple instances
    ==========================================================================
    """

    DOF_DATASET = 'dof_dataset'
    DOF_DOCUMENTS = 'dof_documents'
    DOF_INFO = 'dof_info'
    DOF_MODEL_INFO = "dof_model_info"
    ELEMENT = 'element'
    ELEMENTS = 'elements'
    ELEMENTS_AND_INFO = 'elements_and_info'
    INFO = 'info'
    LINKS = 'links'
    MODEL_DATA_PROCESSING = 'model_data_processing'
    MODEL_INFO = 'model_info'
    MODEL_PERFORMANCE = 'model_performance'
    MODEL_TRAINING = 'model_training'


class JSONDescription(Enum):
    """
    Provide constants for description fields of JSON output
    =======================================================

    Notes
    -----
        Which constant refers to which property, attribute, variable or return
            ABOUT :
                information.Document[keys]
            DOF_BASEPATH :
                file.DofFile.dof_basepath
            ELEMENT_TYPE :
                data.DataElement.element_type
            ELEMENT_INFO :
                data.DataElement.info
            ELEMENTS_COUNT :
                dataset.Dataset.count_all()
            ELEMENTS_COUNT_DATA_PROCESSING :
                len(information.ModelInfo.__data_processing)
            ELEMENTS_COUNT_MODEL :
                len(information.ModelInfo.__model)
            ELEMENTS_COUNT_PERFORMANCE :
                len(information.ModelInfo.__performance)
            ELEMENTS_COUNT_TRAIN :
                len(information.ModelInfo.__training)
            IS_COMPLETE :
                file.DofFile.is_complete()
                information.Document.is_complete
                information.InformationStrict.is_complete
            IS_DOF :
                data.Dataset.is_dof
            LINKS_COUNT :
                data.LinkEngine.__links
            LOCAL_PATH :
                core.DofObject.local_path
            LOCAL_PATH_RELATIVE :
                core.DofObject.is_relative_local
            NEXT_ID :
                data.Dataset.next_available_id
            OBJECT_TYPE :
                core.DofObject.data.__class__.__module__
                core.DofObject.data.__class__.__name__
            ONLINE_LINK :
                core.DofObject.online_link
            ONLINE_LINK_RELATIVE :
                core.DofObject.is_relative_online
            REAL_BINARY :
                core.DofObject.is_binary
            X_ELEMENTS_COUNT :
                data.Dataset.count_x()
            Y_ELEMENTS_COUNT :
                data.Dataset.count_y()
    """

    ABOUT = 'about'
    DOF_BASEPATH = 'dof_basepath'
    ELEMENT_TYPE = 'element_type'
    ELEMENT_INFO = 'element_info'
    ELEMENTS_COUNT = 'elements_count'
    ELEMENTS_COUNT_DATA_PROCESSING = 'elements_count_data_processing'
    ELEMENTS_COUNT_MODEL = 'elements_count_data_model'
    ELEMENTS_COUNT_PERFORMANCE = 'elements_count_performance'
    ELEMENTS_COUNT_TRAIN = 'elements_count_train'
    IS_COMPLETE = 'is_complete'
    IS_DOF = 'is_dof'
    LINKS_COUNT = 'links_count'
    LOCAL_PATH = 'local_path'
    LOCAL_PATH_RELATIVE = 'local_path_relative'
    NEXT_ID = 'next_id'
    OBJECT_TYPE = 'object_type'
    ONLINE_LINK = 'online_link'
    ONLINE_LINK_RELATIVE = 'online_link_relative'
    REAL_BINARY = 'real_binary'
    X_ELEMENTS_COUNT = 'x_elements_count'
    Y_ELEMENTS_COUNT = 'y_elements_count'


class JSONInstance(Enum):
    """
    Provide constants for instance fields of JSON output
    ====================================================
    """


    CLASS = 'class'
    MODULE = 'module'
    CONTENT_FORM = 'content_form'
    DOF_VERSION = 'dof_version'


class JSONRoot(Enum):
    """
    Provide constants for JSON output
    =================================
    """


    INSTANCE = 'instance'
    DESCRIPTION = 'description'
    CONTENT = 'content'


def create_json_dict(class_name : str, module_name : str, describe_only : bool,
                     content_form : ContentForm = ContentForm.PICKLE_BINARY,
                     description : list = []) -> dict:
    """
    Create JSON output as a dictonary
    =================================

    Parameters
    ----------
    class_name : str
        Name of the class to put on JSON.
    module_name : str
        Name of the module to put on JSON.
    describe_only : bool
        Whether the goal of JSON output is description only or not.
    content_form : str, optional ('pickle_binary' if omitted)
        Form of content.
    description : list[(JSONDescription, value)]
        List of desired descriptions.

    Results
    -------
    dict
        JSON output as a dict.

    See Also
    --------
        Describe_only : storage.DofSerializable.to_json()
        Possible values of content_for : ContentForm(Enum)
        Possible values for description : JSONDescription(Enum)
    """

    # pylint: disable=dangerous-default-value
    #         Default value is needed to provide faster instance creation.

    result = {}
    result[JSONRoot.INSTANCE.value] = {}
    result[JSONRoot.INSTANCE.value][JSONInstance.CLASS.value] = class_name
    result[JSONRoot.INSTANCE.value][JSONInstance.MODULE.value] = module_name
    if len(description) > 0:
        result[JSONRoot.DESCRIPTION.value] = {}
        for _description_key, _value in description:
            result[JSONRoot.DESCRIPTION.value][_description_key.value] = _value
    if not describe_only:
        result[JSONRoot.CONTENT.value] = {}
        result[JSONRoot.INSTANCE.value][JSONInstance.CONTENT_FORM.value] = \
                                                            content_form.value
    result[JSONRoot.INSTANCE.value][JSONInstance.DOF_VERSION.value] = \
                                                            __version__
    return result


def get_content(json_dict : dict, class_name : str, module_name : str,
                describe_only : bool) -> dict:
    """
    Get content of JSON dict if valid
    =================================

    Parameters
    ----------
    json_dict : dict
        Well formatted JSON dict.
    class_name : str
        Class name to check.
    module_name : str
        Module name to check.

    Returns
    -------
    dict | bool | None
        Content and parameter dependant output.

    dict
        Content of the JSON dict if describe_only is False and the JSON dict is
        valid to the given class and module.
    None
        None if describe_only is False and the JSON dict is not valid or it
        does not contain content.
    True
        True if describe_only is True and the JSON dict is valid to the given
        class and module.
    False
        False if describe_only is True but the JSON dict is not valid.
    """

    if describe_only:
        return validate_json_dict(json_dict, class_name, module_name)
    if not validate_json_dict(json_dict, class_name, module_name):
        return None
    return json_dict.get(JSONRoot.CONTENT.value)


def validate_json_dict(json_dict : dict, class_name : str,
                       module_name : str) -> bool:
    """
    Provide validation for JSON output
    ==================================

    Parameters
    ----------
    json_dict : dict
        Well formatted JSON dict.
    class_name : str
        Class name to check.
    module_name : str
        Module name to check.

    Returns
    -------
    bool
        Whether the JSON dict is valid or not.

    Notes
    -----
        Valid means the class names are equal and the module names are equal.
    """

    if json_dict[JSONRoot.INSTANCE.value] is None:
        return False
    good_class = json_dict[JSONRoot.INSTANCE.value].get(
                                    JSONInstance.CLASS.value) == class_name
    good_module = json_dict[JSONRoot.INSTANCE.value].get(
                                    JSONInstance.MODULE.value) == module_name
    return all([good_class, good_module])


if __name__ == '__main__':
    pass
