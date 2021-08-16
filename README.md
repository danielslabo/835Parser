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

## Installation

For stand alone usage on Windows, download and unzip the 835FileParser.zip file and run as desired. Otherwise within a python installation run Strip835UI.py.

## Usage

### 835FileParser.exe

For stand alone usage on Windows, download and unzip the 835FileParser.zip file and run as desired.

To Run:

1. Specify the Open location containing files to parse
2. Specify the desired results file output location
3. Optionally, change the default ".835" file pattern to a desired file pattern
    - Files will qualify for parsing if they contain or end with the indicated file pattern

From the Settings menu:

- Toggle whether subsequent program runs append the results to the initial run's results.
- Toggle whether the program should search in subdirectories of the specified open location, for files matching the file pattern

![screenshot1](https://github.com/danielslabo/835Parser/blob/main/img/screenshot1.jpg?raw=true)

### Strip835GUI.py

Run as a direct python program via shell. Offers a GUI for a user to specify the source directory and also the output dircetory. Allows a user to specify the file pattern to use as well. Uses associated ico and png files.

### Strip835Files.py

Run as a direct python program via shell. Assumes the 835 files are in the same directory the program is located and ran from. Would need to modify the file pattern in the program here diretly. Outputs to same directory. This
version is out of date and no longer updated.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

### [APACHE 2.0](https://choosealicense.com/licenses/apache-2.0/)

=======
