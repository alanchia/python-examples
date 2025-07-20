import os
import subprocess
from multiprocessing import Process, Queue  # Use Process for manual control and Queue for communication

# Function to run an SSH command with CPU affinity
def run_ssh(cmd, cpu_ids, queue):
    # Set CPU affinity so this process runs only on the specified CPU cores
    os.sched_setaffinity(0, set(cpu_ids))  # 0 = current process, set() = list of allowed CPUs

    # Define SSH connection details
    identity_file = os.path.expanduser('~/.ssh/id_rsa')  # Use full path to identity file
    user_id = 'root'                                     # SSH user
    host = 'myhost.com'                                  # Remote host (updated)

    # Construct the SSH command
    ssh_command = ['ssh', '-i', identity_file, '-l', user_id, host, cmd]

    try:
        # Execute the SSH command and capture its output
        result = subprocess.check_output(ssh_command, stderr=subprocess.STDOUT, text=True)
        queue.put((cmd, result.strip()))  # Send the command and result back via queue
    except subprocess.CalledProcessError as e:
        # In case of error, send the error message instead
        queue.put((cmd, f"Error: {e.output.strip()}"))

if __name__ == '__main__':
    # List of commands to run on the same host
    commands = [
        'echo "Task 1 done"',  # Simple echo
        'uname -a',            # Kernel/system info
        'date',                # Current date/time
        'uptime'               # System uptime
    ]

    # Define CPU core groups for each process
    # These are sets of CPU cores the process is allowed to run on
    cpu_affinities = [
        [0, 1],
        [2, 3],
        [0, 2],
        [1, 3]
    ]

    queue = Queue()       # Shared queue for collecting results
    processes = []        # To track all spawned processes

    # Start one process per command, each with its CPU affinity
    for cmd, cpu_ids in zip(commands, cpu_affinities):
        p = Process(target=run_ssh, args=(cmd, cpu_ids, queue))  # Create the process
        p.start()                                                # Start it
        processes.append(p)                                      # Keep a reference

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Retrieve and print all results from the queue
    while not queue.empty():
        cmd, output = queue.get()
        print(f"$ {cmd}")
        print(
