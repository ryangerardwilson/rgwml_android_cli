#!/usr/bin/env python3
import subprocess
import os
import argparse
import shutil
import time
import tempfile
from pathlib import Path


"""
LATEST GRADLE VERSION: https://gradle.org/releases/
LATEST FLUTTER VERSION: https://docs.flutter.dev/release/archive. That said, its best to trust the snap store's judgment on the most stable version of flutter.
LATEST OPEN JDK VERSION: https://openjdk.org/. Note that Andorid versions need to be compatible with their corresponding OpenJDK Verson. Eventhough OpenJDK 22 is out, Andorid 14 (API 34) is compatible with OpenJDK 17. See: https://developer.android.com/build/jdks
LATEST ANDORID STUDIO COMMAND LINE TOOLS: https://developer.android.com/studio?gad_source=1&gclid=EAIaIQobChMIroWiw6y-hwMVChGDAx1DRStAEAAYASAAEgIXH_D_BwE&gclsrc=aw.ds (at the bottom of the page)
"""

def run_command(command):
    """Run a shell command and handle errors."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    
    if process.returncode != 0:
        #print(f"Command error: {error.strip()}")
        if "already installed" in error or "has no updates available" in error:
            return output.strip(), error.strip()
        else:
            exit(1)
    return output.strip(), error.strip()

def install():

    def setup_flutter_android():
        """Setup Flutter and Android Studio environment."""
        # Step (a) & (b): Update/Install Android Studio and Flutter from the snap store
        print("Installing/updating Android Studio...")
        output, error = run_command("sudo snap install android-studio --classic")
        #print(f"Command output: {output}")
        if "already installed" in error:
            print("Android Studio is already installed.")
            output, error = run_command("sudo snap refresh android-studio")
            #print(f"Command output: {output}")
            if "no updates available" in error:
                print("Android Studio has no updates available.")

        print("Installing/updating Flutter...")
        output, error = run_command("sudo snap install flutter --classic")
        #print(f"Command output: {output}")
        if "already installed" in error:
            print("Flutter is already installed.")
            output, error = run_command("sudo snap refresh flutter")
            #print(f"Command output: {output}")
            if "no updates available" in error:
                print("Flutter has no updates available.")

        # Step (c): Update Flutter config
        print("Configuring Flutter with Android SDK...")
        output, error = run_command("flutter config --android-sdk /home/rgw/Android/Sdk")
        print(f"Command output: {output}")

        # Step (d): Update .bashrc with necessary environment variables if not already present
        print("Updating .bashrc with necessary environment variables...")
        bashrc_path = os.path.expanduser("~/.bashrc")
        lines_to_add = [
            "export ANDROID_HOME=/home/rgw/Android/Sdk",
            "export PATH=$PATH:$ANDROID_HOME/emulator",
            "export PATH=$PATH:$ANDROID_HOME/tools",
            "export PATH=$PATH:$ANDROID_HOME/tools/bin",
            "export PATH=$PATH:$ANDROID_HOME/platform-tools"
        ]

        with open(bashrc_path, "r+") as bashrc:
            content = bashrc.read()
            for line in lines_to_add:
                if line not in content:
                    bashrc.write(f"\n{line}")

        print(".bashrc updated successfully.")

        # Step (e): Prompt user to update Android Studio settings
        input("Please open Android Studio, go to 'More actions' >> 'SDK Tools', "
              "and select 'Android SDK Command Line Tools (latest)' AND 'Android Emulator'. "
              "Press Enter when you have done this...")

        # Step (f): Run Flutter Doctor to accept Android licenses
        print("Running Flutter Doctor to accept Android licenses...")
        run_command("flutter doctor --android-licenses")

        # Step (g): Run Flutter Doctor to check setup
        print("Running Flutter Doctor to check the setup...")
        run_command("flutter doctor -v")

    setup_flutter_android()

def main():
    parser = argparse.ArgumentParser(description="Install or Uninstall Android SDK, Gradle, Flutter, OpenJDK, and manage Flutter apps.")
    parser.add_argument('--install', action='store_true', help='Install the tools')

    args = parser.parse_args()

    if args.install:
        install()
    else:
        print("Please specify --install")

if __name__ == "__main__":
    main()

