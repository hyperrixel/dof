# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Future
### Added
- Error correction function
- Security functions: checksums and digital signatures
- DataProfiler to provide EDA functionality and description to dataset
- New LinkEngine to provide connection between multiple X values and Y value
- Working DofFileServer
- Create a blockchain-based variant of DoF
- Create a cloud-based variant of DoF (eg: AWS, Microsoft Azure, Google Cloud,
  IBM Cloud, Alibaba Cloud)
- New DoF file type: DofTorrent


## [2.0.0] - 2021-04-01
### Added
- New structure for DoF files
- New DoF file type: DoFJSON
- New program structure: core.py, data.py, datamodel.py, file.py, error.py,
  information.py, services.py, storage.py
- Use native typing for every input parameters (`>= Python 3.7`)
- Use init.py
- Create class DofObject in core to have the main class of DoF
- Create class Contact in information to provide contact data management
- Create class LinkEngine in functional to establish a connection between the
  different types of DataElements data (`X` and `Y` is supported)
- Create class Dataset in data to contain the whole dataset of DataElements
- Create class Document in information to provide document management
- Create class DocumentContainer in information to hold multiple documents
- Create class Information in information to handle information data
- Create class InformationStrict in information to maange mandatory keys
- Create class ModelInfo in information to store model related information
- Create abstract class DofSearch in services to provide search functionality
- Create abstract class DofFileServer in services to manage DoF file sharing
- Create abstract class DofObjectHandler in storage to
- Create abstract class DofSerializable in storage to
- Create class LocalHandler in storage to
- Docstring based on numpy docstring format

### Changed
- Reworked DoF dataset information
- Dataset information section can be rewritten
- Project status is now final instead of beta
- Rename DofElement to DataElement
- Rename DofElementInfo to DataElementInfo
- Rename DofInfo to ContainerInfo

### Remove
- rixel logo removed from file header due to pylint score calculation method


## [1.0.0] - 2020-03-30
### Added
- Create DoF file is available
- Load from DoF file is available
- Support following DoF dataset information: coremodel_family, coremodel_type,
  coremodel_common, original_author, original_source, original_license,
  dof_author, dof_author_contact, dof_source and dof_license,
  coremodel_source_architecture, coremodel_source_weightsandbiases
- Create Class DofElement to hold dataset element in DoF style
- Create Class DofElementInfo to store dataset element level information
- Create Class DofError for error handling with unique exception
- Create Class DofFile to manage DoF file and/or DoF dataset
- Create Class DofInfo to store dataset level information
- Start using CHANGELOG as CHANGELOG.md
- Start using README as README.md
- Start using REQUIREMENTS as requirements.txt
- Project licence: MIT
- Project status: beta
