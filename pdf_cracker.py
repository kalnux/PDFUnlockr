from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
from datetime import timedelta
from multiprocessing import Pool, Manager, cpu_count
import json
import pikepdf
import sys
import time
import psutil
import os

console = Console()

def try_password(pdf_path, password, password_type):
    try:
        if password_type == "user":
            with pikepdf.open(pdf_path, password=password):
                return password
        elif password_type == "owner":
            with pikepdf.open(pdf_path, password=password) as pdf:
                pdf.save("temp_unlocked.pdf")
                return password
    except pikepdf.PasswordError:
        return None

def process_batch(args):
    pdf_path, batch, password_type, progress_dict = args
    local_count = 0
    try:
        for password in batch:
            if try_password(pdf_path, password, password_type):
                return password
            local_count += 1
    except KeyboardInterrupt:
        return None
    progress_dict['completed'] += local_count
    return None

def batched(iterable, size, start=0):
    for i in range(start, len(iterable), size):
        yield i, iterable[i:i + size]

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

def get_optimal_settings():
    cpu_count_value = cpu_count()
    available_memory = psutil.virtual_memory().available / (1024 ** 2)
    optimal_num_workers = cpu_count_value
    optimal_batch_size = int(1000 * (available_memory / 1024))
    return cpu_count_value, available_memory, optimal_num_workers, optimal_batch_size

def crack_pdf(pdf_path, wordlist, password_type, start_index=0, num_workers=None, batch_size=2000, wordlist_path=None, start_percentage=0):
    cpu_count_value, available_memory, recommended_workers, recommended_batch_size = get_optimal_settings()
    
    if num_workers is None:
        num_workers = recommended_workers
    if batch_size is None:
        batch_size = recommended_batch_size

    console.print(f"[bold cyan]System Information:[/bold cyan] [green]CPU Cores:[/green] {cpu_count_value}, [green]Available Memory:[/green] {available_memory:.2f} MB")
    console.print(f"[bold cyan]Optimal Settings:[/bold cyan] Based on your CPU and memory, the optimal settings for best performance are: [green]--num-workers[/green] {recommended_workers} and [green]--batch-size[/green] {recommended_batch_size}")

    total_attempts = len(wordlist)
    manager = Manager()
    progress_dict = manager.dict()
    progress_dict['completed'] = start_index
    found_password = None

    args_list = [
        (pdf_path, batch, password_type, progress_dict)
        for _, batch in batched(wordlist, batch_size, start_index)
    ]

    try:
        with Pool(processes=num_workers) as pool:
            results = pool.imap_unordered(process_batch, args_list)
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="bold blue", bar_width=None, style="white"),
                TextColumn("[progress.percentage]{task.percentage:>6.2f}%"),
                TextColumn("{task.completed}/{task.total}"),
                TimeElapsedColumn(),
                TextColumn("Remaining: {task.fields[remaining]}"),
                TextColumn("{task.fields[rate]} password/s"),
                console=console
            ) as progress:
                task_id = progress.add_task("Progress", total=total_attempts, start=True, rate=0, remaining="Calculating")
                
                start_time = time.time()
                for result in results:
                    if result:
                        found_password = result
                        pool.terminate()
                        break

                    elapsed = time.time() - start_time
                    completed = progress_dict['completed']
                    speed = int(completed / elapsed) if elapsed > 0 else 0
                    remaining_passwords = total_attempts - completed
                    remaining_time = remaining_passwords / speed if speed > 0 else 0
                    formatted_remaining = format_time(remaining_time)

                    progress.update(task_id, completed=completed, rate=speed, remaining=formatted_remaining)
                
            if found_password:
                console.print(f"\n[bold green]Password found: {found_password}[/bold green]")

    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        console.print("\n[bold yellow]Interrupted by user. Exiting.[/bold yellow]")
        
        save_prompt = input("\nSave session (s) | Exit without saving (x): ").strip().lower()
        if save_prompt == 's':
            completed_attempts = progress_dict['completed']
            progress_percentage = (completed_attempts / total_attempts) * 100
            save_session(pdf_path, wordlist_path, completed_attempts, progress_percentage)
            console.print("[bold cyan]Session saved. Exiting.[/bold cyan]")
        else:
            console.print("[bold red]Exiting without saving.[/bold red]")
        sys.exit(0)

    if not found_password:
        console.print("\n[bold red]Failed to unlock the PDF. Password not found in the wordlist.[/bold red]")
    return found_password

def save_session(pdf_path, wordlist_path, current_index, progress_percentage=0):
    session_data = {
        'pdf_path': pdf_path,
        'wordlist_path': wordlist_path,
        'current_index': current_index,
        'progress_percentage': progress_percentage
    }

    if not os.access(".", os.W_OK):
        print("Error: Unable to save session. Write permission is denied in the current directory.")
        return

    try:
        with open('session_data.json', 'w') as file:
            json.dump(session_data, file)
        print(f"\nSession saved at line {current_index} ({progress_percentage:.2f}% complete) in wordlist.")
    except PermissionError:
        print("Error: Unable to save session. Write permission is denied in the current directory.")
