# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
