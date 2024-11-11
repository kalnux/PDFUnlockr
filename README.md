# PDFUnlockr

**PDFUnlockr** is a command-line tool for unlocking encrypted PDF files by attempting to crack user or owner passwords through a customizable and efficient multi-process dictionary-based approach. This tool is ideal for security researchers and professionals needing to recover access to PDF documents with lost passwords.

## Features

- **User or Owner Password Cracking**: Unlock PDFs by either user or owner password based on the user's choice.
- **Session Resumption**: Resume the cracking process from the last saved session, minimizing redundant work and saving progress.
- **Customizable Multi-Processing**: Define the number of worker processes to optimize CPU usage and batch sizes, ensuring smooth performance across different hardware setups.
- **Progress Tracking and Reporting**: Detailed progress with time estimation, speed, and completion tracking using the Rich library.
- **System-Based Optimal Settings**: Automatically suggests optimal CPU and memory configurations for faster cracking.
- **Wordlist-Based Cracking**: Load and use a custom wordlist to attempt various password combinations efficiently.
- **Error Handling**: Robust error handling for missing or inaccessible files, corrupted sessions, and unsupported configurations.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PDFUnlockr.git
cd PDFUnlockr

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python PDFUnlockr.py -f <pdf_file> -w <wordlist_file> [OPTIONS]
```

### Options
- **-h, --help**: Show the help message and exit.
- **-f, --file**: Path to the encrypted PDF file (required).
- **-w, --wordlist**: Path to the wordlist file (required).
- **--owner-password**: Attempt to unlock the owner password (specify either this or `--user-password`).
- **--user-password**: Attempt to unlock the user password (specify either this or `--owner-password`).
- **-r, --resume**: Resume from the last saved session.
- **--num-workers**: Number of worker processes to use (default: 4).
- **--batch-size**: Batch size for password attempts (default: 2000).

### Example Commands

- **Basic Cracking**:
  ```bash
  python PDFUnlockr.py -f encrypted.pdf -w wordlist.txt --user-password
  ```

- **Resuming a Previous Session**:
  ```bash
  python PDFUnlockr.py -r
  ```

- **Custom Worker and Batch Size**:
  ```bash
  python PDFUnlockr.py -f encrypted.pdf -w wordlist.txt --owner-password --num-workers 8 --batch-size 5000
  ```

## Session Management

PDFUnlockr saves session data in `session_data.json` for seamless resumption. Ensure the specified PDF and wordlist paths are accessible for successful resumption.

## System Requirements

- **Python 3.6+**
- **pikepdf**: For handling PDF password unlocking.
- **rich**: For enhanced console output and progress tracking.
- **psutil**: For system information and resource monitoring.

Install dependencies via the provided `requirements.txt` file.

## License

This project is licensed under the MIT License. See `LICENSE` for more information.
