from multiprocessing import Pool
import subprocess

# Function to run a given SSH command and return both the command and its output
def run_ssh(cmd):
    identity_file = '~/.ssh/id_rsa'  # Replace with your actual identity file path
    user_id = 'root'
    host = 'myhost.com'            # Replace with your actual SSH target

    ssh_command = ['ssh', '-i', identity_file, '-l', user_id, host, cmd]

    try:
        result = subprocess.check_output(ssh_command, stderr=subprocess.STDOUT, text=True)
        return (cmd, result.strip())  # Return command and output
    except subprocess.CalledProcessError as e:
        return (cmd, f"Error: {e.output.strip()}")  # Return command and error message

# List of commands to run on the same remote host
commands = [
    'echo "Task 1 done"',
    'uname -a',
    'date',
    'uptime'
]

# Run the commands in parallel using a pool of 4 processes
with Pool(processes=4) as pool:
    results = pool.map(run_ssh, commands)

# Print each command and its output
for cmd, output in results:
    print(f"$ {cmd}")
    print(f'{output}\n\n')

