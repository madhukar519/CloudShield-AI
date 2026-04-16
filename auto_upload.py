import subprocess
import os

def run_git_commands():
    commands = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit of CloudShield AI Chatbot"],
        ["git", "branch", "-M", "main"],
        ["git", "remote", "add", "origin", "https://github.com/madhukar519/CloudShield-AI.git"],
        ["git", "push", "-u", "origin", "main"]
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        try:
            # We use shell=True on Windows sometimes helps, but let's try direct first
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error in {cmd[0]}:")
            print(e.stderr)
            if "remote origin already exists" in e.stderr:
                print("Proceeding...")
                continue
            break

if __name__ == "__main__":
    run_git_commands()
