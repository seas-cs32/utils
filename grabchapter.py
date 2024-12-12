### utils/grabchapter.py
"""
This script works within the cs50.dev world and grabs
the files for the specified chapter. If you wanted the
files in Chapter 4, you'd run this script as follows:

$ python3 grabchapter.py 4

It will grab the chapter's files from the book's GitHub
repository for Chapter 4, place them in a subdirectory
of the user's home directory called `chap04`.
"""

import os
import subprocess
import sys
import zipfile

def main():
    # Check usage and grab the chapter number
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 grabchapter.py CHAP_NUM")

    # Verify that it is a good chapter number
    try:
        chap_str = sys.argv[1]
        chap_num = int(chap_str)
        if chap_num < 1 or chap_num > 18:
            sys.exit("ERROR: chapter number must be between 1 and 18")
    except ValueError:
            sys.exit("ERROR: input parameter should be an integer between 1 and 18")

    # Start alerting the user to our progress
    print(f"STARTING grabchapter.py ...")

    # Create URL of github repo, the chapter's directory name, and
    # the zip file's filename.
    url = 'https://github.com/seas-cs32/'
    if chap_num < 10:
        chap_str = 'chap' + '0' + chap_str
    else:
        chap_str = 'chap' + chap_str
        url = url + '0' + chap_str
    url = url + chap_str + '/archive/refs/heads/main.zip'
    fname = os.path.basename(url)

    # Figure out the absolute path of the user's codespaces directory
    workspaces_path = '/workspaces'

    # ... first check that `workspaces_path` exists
    if not os.path.exists(workspaces_path) or not os.path.isdir(workspaces_path):
        sys.exit(f"ERROR: {workspaces_path} doesn't exist")

    # ... next list all non-hidden directories within workspaces_path
    subdirs = [
        name for name in os.listdir(workspaces_path)
        if os.path.isdir(os.path.join(workspaces_path, name)) and name[0] != '.'
    ]

    # ... then verify that there is exactly one directory within workspaces_path
    if len(subdirs) != 1:
        sys.exit(f"ERROR: too many ({len(subdirs)}) directories in {workspaces_path}")

    user_codespaces_dir = os.path.join(workspaces_path, subdirs[0])

    # Jump to the user's codespaces directory, where we'll place
    # the chapter's directory and files.
    try:
        os.chdir(user_codespaces_dir)
    except Exception as e:
        sys.exit(f"ERROR changing directory: {e}")

    # Download the chapter's files (quietly)
    try:
        command = ['wget', url]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        sys.exit(f"ERROR executing wget command: {e}")

    # Alert the user to our progress
    print(f"... Changed directory to: {user_codespaces_dir}")
    print(f"... Zip file downloaded from: {url}")

    # Unzip the downloaded file
    try:
        # Open the zip file
        with zipfile.ZipFile(fname, 'r') as zip_ref:
            # Extract contents to the current directory
            zip_ref.extractall()
    except zipfile.BadZipFile:
        sys.exit(f"ERROR: {fname} is not a valid ZIP file")
    except Exception as e:
        sys.exit(f"Error unzipping {fname}: {e}")

    # Alert the user to our new progress
    print(f"... Unzipped {fname}")

    # Remove the downloaded zip file
    try:
        os.remove(fname)
    except Exception as e:
        sys.exit(f"ERROR removing file {fname}: {e}")

    # Alert the user to the fact we're successfully done
    print(f"... Removed {fname}")

    # Rename the chapter directory to remove the "-main" suffix
    try:
        os.rename(chap_str + '-main', chap_str)
    except FileNotFoundError:
        sys.exit(f"ERROR: the directory `{chap_str + '-main'}` does not exist")
    except FileExistsError:
        sys.exit(f"ERROR: a directory or file named `{chap_str}` already exists")
    except Exception as e:
        sys.exit(f"ERROR: {e}")

    # Alert the user to the fact we're successfully done
    print(f"... Renamed {chap_str}-main to {chap_str}")
    print(f"grabchapter.py COMPLETE")
    print()
    print(f"To run a script in {chap_str}, make sure to put yourself")
    print(f"in that directory by executing: cd {user_codespaces_dir}/{chap_str}")
    print()

if __name__ == '__main__':
    main()
