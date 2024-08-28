import subprocess
import sys

def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'setup/requirements.txt'])
        print("All packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages. Error: {e}")

if __name__ == '__main__':
    install_requirements()