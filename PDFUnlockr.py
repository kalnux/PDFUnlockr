import argparse
import json
import os
from pdf_cracker import crack_pdf, save_session

def load_session():
    if os.path.exists('session_data.json'):
        try:
            with open('session_data.json', 'r') as file:
                session_data = json.load(file)
                
                if session_data is None:
                    print("Error: session_data.json is empty or unreadable.")
                    return None
                
                pdf_path = session_data.get("pdf_path")
                wordlist_path = session_data.get("wordlist_path")
                
                if pdf_path is None or wordlist_path is None:
                    print("Error: session data is missing required file paths.")
                    return None
                
                if os.path.exists(pdf_path) and os.path.exists(wordlist_path):
                    return session_data
                else:
                    print("Error: One or more files in the saved session could not be found.")
                    return None
        except json.JSONDecodeError:
            print("Error: session_data.json is corrupted and cannot be read as JSON.")
            return None
    else:
        print("No saved session found.")
        return None

def main():
    print("===============================================")
    print("              🗝️  PDFUnlockr 🗝️")
    print("                  by Kalnux")
    print("    Unlock encrypted PDF files with ease")
    print("===============================================\n")
    parser = argparse.ArgumentParser(
        description="PDFUnlockr - Unlock encrypted PDF files using a dictionary attack. This tool is intended for use on PDF files you own or have permission to access."
    )

    parser.add_argument("-f", "--file", help="Path to the encrypted PDF file (required)", required='-r' not in os.sys.argv)
    parser.add_argument("-w", "--wordlist", help="Path to the wordlist file (required)", required='-r' not in os.sys.argv)
    parser.add_argument("--owner-password", action="store_true", help="Attempt to unlock the PDF with the owner password")
    parser.add_argument("--user-password", action="store_true", help="Attempt to unlock the PDF with the user password")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume from the last saved session (overrides file and wordlist requirements)")
    parser.add_argument("--num-workers", type=int, default=4, help="Number of worker processes to use for faster cracking (default: 4)")
    parser.add_argument("--batch-size", type=int, default=2000, help="Batch size for password attempts, affecting memory usage and performance (default: 2000)")

    args = parser.parse_args()
    
    if args.resume:
        session_data = load_session()
        if session_data is None:
            print("Cannot resume; please ensure the session files are available.")
            return
        args.file = session_data['pdf_path']
        args.wordlist = session_data['wordlist_path']
        start_index = session_data['current_index']
        start_percentage = session_data.get('progress_percentage', 0)
        print(f"Resuming from line {start_index} ({start_percentage:.2f}% complete).")
    else:
        start_index = 0
        start_percentage = 0

    if not args.resume:
        if not args.file or not args.wordlist:
            parser.error("the following arguments are required: -f or --file, -w or --wordlist")
        
        if args.owner_password and args.user_password:
            print("Please specify only one type of password to unlock (--owner-password or --user-password).")
            return
        elif not args.owner_password and not args.user_password:
            print("Please specify a password type (--owner-password or --user-password).")
            return

    try:
        with open(args.wordlist, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The wordlist file '{args.wordlist}' could not be found.")
        return

    password_type = "owner" if args.owner_password else "user"

    success = crack_pdf(
        args.file, 
        wordlist, 
        password_type, 
        start_index=start_index, 
        num_workers=args.num_workers, 
        batch_size=args.batch_size, 
        wordlist_path=args.wordlist,  # Explicitly pass the wordlist path
        start_percentage=start_percentage  # Pass the starting percentage for better tracking
    )
    
    if not success:
        print("Failed to unlock the PDF. Password not found in the wordlist.")

if __name__ == "__main__":
    main()
