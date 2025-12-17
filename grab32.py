### utils/grab32.py
"""
This script works within the cs50.dev world and grabs three kinds
of files:
  1. the CS32 GitHub repo files for a book chapter;
  2. the .devcontainer.json file for configuring the codespace;
  3. the files for a programming problem set kept in cs32-public.

If you wanted the book files for Chapter 4, you'd run this script
as follows:

$ python3 grab32.py chap04

The input parameter (i.e., `chap04` in this example) should match the
name of a public CS32 GitHub repo.  The script will place the chapter's
files from the book's GitHub repository in a subdirectory of the user's
current codespace.  The subdirectory is given the same name as the
GitHub repo (i.e., `chap04` in the example).

If a subdirectory of the same name already exists in the current
codespace, this script assumes that the user wants a new clean copy
of the repo's files.  It will name the clean copy `REPO_clean` (e.g.,
`chap04_clean`).

It also grabs the CS32 `.devcontainer.json` file and replaces the CS50
version with our CS32 version. We depend upon the student to force a
full rebuild the the codespaces container. This is done by:

  * pressing "Command + Shift + P” (if on macOS) or “Ctrl + Shift + P”
    (if on Windows);
  * search for “Codespaces: Rebuild Container”;
  * press Enter on the keyboard.

Make sure that the students select the Full Rebuild (not Rebuild) option
to perform a codespace rebuild.

This script does this setup work if you run it with this special parameter:

$ python3 grab32.py cs32-setup

Finally, it can grab CS32 pset directories that we've hidden in the
cs32-public Google drive. To grab these zipped directories, you specify
the pset you want:

$ python3 grab32.py pset1

The input parameter (i.e., `pset1` in this example) should match the
name of a zip file in cs32-public.  The script will wget the zip file
using the proper incantation for grabbing files from Google Drive,
unzip the file, and remove the downloaded zip file.

If a subdirectory of the same name already exists in the current
codespace, this script assumes that the user wants a new clean copy
of the pset's files.  It will name the clean copy `PSET_clean` (e.g.,
`pset1_clean`).

Author: Mike Smith (with reference help from GPT-4o)
Date: January 2025
"""

import os
import re
import shutil
import subprocess
import sys
import zipfile

# Global constants and configuration parameters
ORG_URL = 'https://github.com/seas-cs32/'
MAIN_ZIP_PATH = '/archive/refs/heads/main.zip'
CODESPACES_ROOT = '/workspaces'
SETUP_REPO = 'template'

# FILE_IDs of the pset zip files in cs32-public. The FILE_ID of
# a shareable Google Drive URL is here:
# https://drive.google.com/file/d/FILE_ID/view?usp=sharing
PSETS = {
    'pset1': '17jx0YjyoKPbaLsfaPsuFrKjpZm05tfDc',
    'pset2': '1RXwyEuSp-nomfzvtv28cSO9KQZZT8TCa',
    'pset3': '17SEp67vLgMytPuyuHNNnZxF5pPRYctVV',
    'pset4': '1-oOHOW9m7RGyuVUmRM-LyLrFnDUtZEEM',
    'pset5': '1jYYeNKa6fAdtnQ4kiIUSCj-j8U7SLSmP',
}


def determine_working_dir():
    """Finds and returns the root directory of the user's codespace"""
    # Grab the current directory path
    cwd = os.getcwd()

    # If cwd is the root directory of a codespace, use it
    p = CODESPACES_ROOT + r'/\d+'
    if re.fullmatch(p, cwd):
        return cwd

    # If we get here, we're not in a codespace root directory so we'll
    # try to discover where it is and cd there. This begins by checking
    # that CODESPACES_ROOT exists.
    if not os.path.exists(CODESPACES_ROOT) or not os.path.isdir(CODESPACES_ROOT):
        sys.exit(f"ERROR: {CODESPACES_ROOT} doesn't exist")

    # Now list all non-hidden directories within CODESPACES_ROOT
    subdirs = [
        name for name in os.listdir(CODESPACES_ROOT)
        if os.path.isdir(os.path.join(CODESPACES_ROOT, name)) and name[0] != '.'
    ]

    # We know what to do if there is exactly one directory within CODESPACES_ROOT
    if len(subdirs) == 1:
        codespace_path = os.path.join(CODESPACES_ROOT, subdirs[0])

        # Jump to the root of the user's codespace directory
        try:
            os.chdir(codespace_path)
        except Exception as e:
            sys.exit(f"ERROR changing directory: {e}")

        return codespace_path

    # We need the user's help to find the right place to put the repo
    print('ERROR: Failed to find the root directory of your codespace.')
    print('ERROR: Please cd there and rerun this script.')
    sys.exit()


def my_rename(frompath, topath):
    """Rename a file or directory path from `frompath` to `topath`"""
    try:
        os.rename(frompath, topath)
    except FileNotFoundError:
        sys.exit(f"ERROR: the directory `{frompath}` does not exist")
    except FileExistsError:
        sys.exit(f"ERROR: a directory or file named `{topath}` already exists")
    except Exception as e:
        sys.exit(f"ERROR: {e}")


def main():
    # Check usage and grab the repo name
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 grab32.py REPO")

    repo = sys.argv[1]

    # Defaults to chap grabs
    SETUP = False
    PSET = False

    # Check validity of input parameter
    if repo == 'cs32-setup':
        # Special case
        SETUP = True
        repo = SETUP_REPO
    elif repo[:len('pset')] == 'pset':
        PSET = True
        # Check for a valid pset number
        if not re.fullmatch(r'pset[1-5]', repo):
            sys.exit(f"ERROR: {repo} is not a valid; did you mistype it?")
    else:
        # Check for and gracefully handle bad parameters
        if re.fullmatch(r'chap[01][1-8]', repo) or repo == 'chap09' or repo == 'chap10':
            pass
        else:
            sys.exit(f"ERROR: {repo} is not a valid; did you mistype it?")

    # Start alerting the user to our progress
    print(f"STARTING grab32.py ...")

    # Make sure the script is in a codespaces directory
    codespace_path = determine_working_dir()
    print(f"... Working in directory: {codespace_path}")

    # Create URL to ...
    if PSET:
        # ... a zipfile in cs32-public
        url = f'https://drive.google.com/uc?export=download&id={PSETS[repo]}'
        zip_fname = f'{repo}.zip'
    else:
        # Create URL to a zipfile of the specified github repo
        url = ORG_URL + repo + MAIN_ZIP_PATH
        zip_fname = os.path.basename(url)

    if PSET:
        # Unzip in a temp directory since no -main on the zipped directory
        TMP_DIR = '.tmp_cs32'

        # Create the temp directory
        try:
            os.makedirs(TMP_DIR, exist_ok=True)
            print(f"... directory '{TMP_DIR}' created successfully")
        except OSError as error:
            sys.exit(f"ERROR creating directory {TMP_DIR}: {error}")

        # Jump into the temp directory for the unzip
        try:
            os.chdir(TMP_DIR)
            print(f"... jumped into '{TMP_DIR}'")
        except Exception as e:
            sys.exit(f"ERROR changing into directory {TMP_DIR}: {e}")

    # Download the repo's files (quietly)
    try:
        if PSET:
            command = ['wget', '--no-check-certificate', url, '-O', zip_fname]
        else:
            command = ['wget', url]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        sys.exit(f"ERROR executing wget command: {e}")
    print(f"... Zip file downloaded from: {url}")

    # Unzip the downloaded file
    try:
        # Open the zip file
        with zipfile.ZipFile(zip_fname, 'r') as zip_ref:
            # Extract contents to the current directory
            zip_ref.extractall()
    except zipfile.BadZipFile:
        sys.exit(f"ERROR: {zip_fname} is not a valid ZIP file")
    except Exception as e:
        sys.exit(f"Error unzipping {zip_fname}: {e}")
    print(f"... Unzipped {zip_fname}")

    # Remove the downloaded zip file
    try:
        os.remove(zip_fname)
    except Exception as e:
        sys.exit(f"ERROR removing file {zip_fname}: {e}")
    print(f"... Removed {zip_fname}")

    if PSET:
        if os.path.exists(f'../{repo}'):
            # Rename as a clean copy of repo
            my_rename(repo, f'../{repo}_clean')
            print(f"... Renamed {TMP_DIR}/{repo} to {repo}_clean")
        else:
            # Straightforward rename
            my_rename(repo, f'../{repo}')
            print(f"... Renamed {TMP_DIR}/{repo} to {repo}")

        # Jump back to the user's home directory
        try:
            os.chdir('..')
            print(f"... jumped back into home directory")
        except Exception as e:
            sys.exit(f"ERROR changing into directory '..': {e}")

    else:
        # Rename the repo directory to remove the "-main" suffix,
        # but how we do this depends on whether the user is downloading
        # the repo for the first time or as another clean copy.
        if os.path.exists(repo):
            # Rename as a clean copy of repo
            my_rename(repo + '-main', repo + '_clean')
            print(f"... Renamed {repo}-main to {repo}_clean")
        else:
            # Straightforward rename
            my_rename(repo + '-main', repo)
            print(f"... Renamed {repo}-main to {repo}")

    # Clean up if running cs32-setup
    if SETUP:
        # Replace CS50 .devcontainer.json with our CS32 one
        src = f'{repo}/.devcontainer.json'
        dst = '.devcontainer.json'
        try:
            shutil.move(src, dst)
            print(f"... Moved {src} to {dst}")
        except FileNotFoundError:
            sys.exit(f"ERROR moving {src}, file not found")
        except Exception as e:
            sys.exit(f"ERROR occurred while moving {src}: {e}")

        # Remove the SETUP_REPO directory
        try:
            shutil.rmtree(repo)
            print(f"... Removed {repo}")
        except FileNotFoundError:
            sys.exit(f"ERROR removing {repo}, directory not found")
        except Exception as e:
            sys.exit(f"ERROR occurred while removing {repo}: {e}")

    # Alert the user to the fact we're done
    print(f"grab32.py COMPLETE")
    print()
    if not SETUP:
        print(f"To run a script in {repo}, make sure to put yourself")
        print(f"in that directory by executing: cd {codespace_path}/{repo}")
        print()

if __name__ == '__main__':
    main()
