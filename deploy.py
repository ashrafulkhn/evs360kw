
import os
import sys
import logging
import subprocess
import git
from git import Repo
from logger_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

REPO_URL = "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME"  # Replace with your repository URL
BRANCH_NAME = "main"  # Replace with your branch name

def check_and_clone_repo():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if os.path.exists(os.path.join(current_dir, '.git')):
        logger.info("Repository already exists, checking for updates...")
        try:
            repo = Repo(current_dir)
            current = repo.active_branch
            repo.remotes.origin.fetch()
            
            # Check if local is behind remote
            commits_behind = list(repo.iter_commits(f'{current.name}..origin/{current.name}'))
            
            if commits_behind:
                logger.info("Updates found, pulling changes...")
                repo.remotes.origin.pull()
                logger.info("Successfully updated the code")
            else:
                logger.info("Code is up to date")
                
        except Exception as e:
            logger.error(f"Error checking/pulling updates: {str(e)}")
            sys.exit(1)
    else:
        logger.info("Cloning repository...")
        try:
            Repo.clone_from(REPO_URL, current_dir, branch=BRANCH_NAME)
            logger.info("Repository cloned successfully")
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            sys.exit(1)

def run_main():
    logger.info("Starting main.py...")
    try:
        process = subprocess.Popen([sys.executable, 'main.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        _, stderr = process.communicate()
        if stderr:
            logger.error(f"Error from main.py: {stderr}")
            
        return process.poll()
    
    except Exception as e:
        logger.error(f"Error running main.py: {str(e)}")
        return 1

def main():
    check_and_clone_repo()
    sys.exit(run_main())

if __name__ == "__main__":
    main()
