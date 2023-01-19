# Changelog

## v0.0.5 - 19/01/2023
### Added:
1) read results (particles, properties, and grids)
2) add mod calculation to read_currents and read_winds
3) notebook 02
4) add py3.11 to test workflow
5) exclude windows w/ py3.7
6) add pyteseo.export functionality
7) add pyteseo/defaults.json to centralize defaults (names, configs...)
8) add docs/notebooks/03_export_resutls.ipynb
### Changed:
1) cli pyteseo-tests move to pyteseo/tests.__init__.py
### Fixed:
1) added pre-commit with check-yaml, end-of-file-fixer, trailing-whitespace, black, black-jupyter and falke8
<br/><br/>


## v0.0.4 - 11/01/2023
### Added:
1) required version pytest >=7
### Changed:
### Fixed:
1) relative paths to pyteseo installtion for notebooks
<br/><br/>


## v0.0.3 - 11/01/2023
### Added:
1) add google colab for notebooks
### Changed:
1) update python version requirement to 3.7
### Fixed:
1) Compatibility for python versions >=3.7
<br/><br/>


## v0.0.2 - 11/01/2023
### Added:
1) coverage functionality
2) tools configuration in pyproject.toml
3) write currents and winds with io module
4) build and publish in pypi.test
5) build and publish in pypi
6) user able to use tests to validate installation
7) add jupyter notebooks in docs
8) publish docs in github repo page-service
### Changed:
1) upgrade logic for coastlines
2) change structure to add tests as subpackage
3) update doc
4) visibility of the repo to public
### Fixed:
1) None
<br/><br/>


## v0.0.1 - 29/12/2022
### Added:
1) Init repository using flit
2) Initial structure of the package
3) Functions read_grid, read_coastline, write_grid, write_coastline in pyteseo.io.py
4) Testing using pytest
5) Initial documentation using sphynx, myst_parser, autoapi...
6) Logo images for TESEO and pyTESEO
7) First CHANGELOG
### Changed:
1) None
### Fixed:
1) None
<br/><br/>
