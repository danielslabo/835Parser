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

### Strip835GUI.py

Run as a direct python program via shell. Offers a GUI for a user to specify the source directory and also the output dircetory. Allows a user to specify the file pattern to use as well. Uses associated ico and png files.

### Strip835Files.py

Run as a direct python program via shell. Assumes the 835 files are in the same directory the program is located and ran from. Would need to modify the file pattern in the program here diretly. Outputs to same directory. This
version is out of date and no longer updated.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[APACHE 2.0](https://choosealicense.com/licenses/apache-2.0/)
=======
