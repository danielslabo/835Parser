# 835Parser
Parse 835 files to quickly pull file content for cross referencing. Program outputs a file containing rows for each CLP and PLB segment found within the parsed files.

Rows of data contain the following columns:
- FILENAME
- TRN02
- TRN03
- PAYER
- PAYEE
- NPI
- CLAIM (CLP 01)
- CLP02
- PLB_DATA (the whole PLB segment's data)

## Current Version [3.0.0] - 2021-08-14
### Added
- Thread processing so GUI doesn't freeze while running
- Progress bar

### Changed
- Decomposed parsing 835s into several methods
- Fixed typos and reworded comments

## Installation
TODO

## Usage
### Strip835GUI.py
Run as a direct python program via shell. Offers a GUI for a user to specify the source directory and also the output dircetory. Allows a user to specify the file pattern to use as well. Uses associated ico and png files.

### Strip835Files.py
Run as a direct python program via shell. Assumes the 835 files are in the same directory the program is located and ran from. Would need to modify the file pattern in the program here diretly. Outputs to same directory. This
version is out of date and no longer updated.

### Strip835.exe
TBD

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[APACHE 2.0](https://choosealicense.com/licenses/apache-2.0/)
=======