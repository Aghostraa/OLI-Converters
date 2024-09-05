# OLI-Converters

## Description

OLI-Converters is a Python-based tool designed to process smart contract data from various Blockscout instances and convert it to the Open Labels Initiative (OLI) format. This project aims to standardize and enrich blockchain contract data, making it more accessible and useful for researchers, developers, and analysts.

## Features

- Fetches contract data from multiple Blockscout APIs
- Processes and standardizes contract information
- Converts data to OLI format
- Supports concurrent processing for improved performance
- Handles various blockchain networks including Optimism, Polygon zkEVM, Arbitrum, and more

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Aghostraa/OLI-Converters.git
   cd OLI-Converters
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your input CSV file with contract addresses and origin keys.

2. Update the `csv_file_path` variable in the `main()` function of `main.py` to point to your input file.

3. Run the main script:
   ```
   python main.py
   ```

4. The script will process the contracts and save the results in `processed_contracts.json`.

## Project Structure

- `main.py`: The main script containing all the logic for fetching, processing, and converting contract data.
- `processed_contracts.json`: Output file containing the processed contract data in OLI format.
- `requirements.txt`: List of Python dependencies required for the project.
- `.gitignore`: Specifies intentionally untracked files to ignore.

## Configuration

The script supports multiple blockchain networks. You can modify the `BLOCKSCOUT_APIS` and `CHAIN_ID_MAP` dictionaries in `main.py` to add or remove supported networks.

## Contributing

Contributions to OLI-Converters are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here, e.g., MIT, GPL, etc.]

## Contact

[Your Name or GitHub username]
GitHub: [@Aghostraa](https://github.com/Aghostraa)

## Acknowledgements

- [Blockscout](https://blockscout.com/) for providing the API services
- [Open Labels Initiative](https://github.com/open-labels) for the standardized format
