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


# Static variables for URLs and version numbers
CMDLINE_TOOLS_URL = 'https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip'
CMDLINE_TOOLS_ZIP = os.path.expanduser('~/Downloads/commandlinetools.zip')

GRADLE_VERSION = '8.9'

FLUTTER_VERSION_CHANNEL = 'stable'
OPENJDK_VERSION = '17'

# Static variables for emulator configuration
SDK_DIR = os.path.expanduser('~/Android/Sdk')
EMULATOR_DEVICE = 'pixel'
ANDROID_VERSION = '30'
SYSTEM_IMAGE = f"system-images;android-{ANDROID_VERSION};google_apis;x86_64"
AVD_NAME = 'my_avd'

def run_command(command):
    """Run a shell command and stream the output."""
    print(f"Running command: {command}", flush=True)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline().decode('utf-8')
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True)
    rc = process.poll()
    return rc

def run_command_explicit(command):
    """Run a system command and print its output."""
    print(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    process.wait()
    return process.returncode == 0


def uninstall():
    """Uninstall existing Android SDK tools, Gradle, Flutter, and OpenJDK."""
    def uninstall_cmdline_tools():
        """Uninstall existing command line tools for Android SDK."""
        android_home = os.path.expanduser('~/Android/Sdk')
        cmdline_tools_dir = os.path.join(android_home, 'cmdline-tools')

        if os.path.exists(cmdline_tools_dir):
            shutil.rmtree(cmdline_tools_dir)
            print(f"Removed directory: {cmdline_tools_dir}")
        else:
            print("No previous command-line tools installation found.")

    def uninstall_gradle():
        """Uninstall Gradle by removing the installation directory."""
        gradle_base_dir = '/opt/gradle'
        if os.path.exists(gradle_base_dir):
            run_command(f'sudo rm -rf {gradle_base_dir}')
            print(f"Removed directory: {gradle_base_dir}")
        else:
            print("No previous Gradle installation found.")

    def uninstall_flutter():
        """Uninstall Flutter SDK by removing the installation directory."""
        flutter_base_dir = os.path.expanduser('~/flutter')
        if os.path.exists(flutter_base_dir):
            shutil.rmtree(flutter_base_dir)
            print(f"Removed directory: {flutter_base_dir}")
        else:
            print("No previous Flutter installation found.")

    def uninstall_openjdk():
        """Uninstall OpenJDK."""
        run_command(f'sudo apt-get remove -y openjdk-{OPENJDK_VERSION}-jdk')
        run_command('sudo apt-get autoremove -y')
        print(f"OpenJDK {OPENJDK_VERSION} uninstalled.")

    print("Uninstalling command-line tools...")
    #uninstall_cmdline_tools()
    print("Uninstalling Gradle...")
    uninstall_gradle()
    print("Uninstalling Flutter...")
    uninstall_flutter()
    print("Uninstalling OpenJDK...")
    uninstall_openjdk()
    print("Uninstallation complete!")

def install():
    """Install Android SDK tools, packages, Gradle, Flutter, and OpenJDK."""

    def clean_and_setup_path():
        """Clean and setup the PATH environment variable."""
        paths_to_add = [
            f'{SDK_DIR}/cmdline-tools/latest/bin',
            f'{SDK_DIR}/platform-tools',
            '/usr/bin/gradle',  # Gradle binary location when installed via apt
            f'{os.path.expanduser("~")}/flutter/bin'
        ]

        path_entry = ':'.join(paths_to_add)

        start_tag = '### START AUTO-PATH ###'
        end_tag = '### END AUTO-PATH ###'
        auto_path_content = f'{start_tag}\nexport PATH=$PATH:{path_entry}\n{end_tag}\n'

        bashrc_path = os.path.expanduser('~/.bashrc')
        with open(bashrc_path, 'r+') as f:
            content = f.read()

            # Find the section marked by the comment tags
            start_index = content.find(start_tag)
            end_index = content.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                # If tags not found, append at the end
                f.seek(0, os.SEEK_END)
                f.write(auto_path_content)
            else:
                # Replace the existing section between tags
                end_index += len(end_tag)
                before_section = content[:start_index]
                after_section = content[end_index:].lstrip()
                new_content = f'{before_section}{auto_path_content}{after_section}'
                f.seek(0)
                f.write(new_content)
                f.truncate()

        # Manually source the updated .bashrc to apply changes immediately
        os.system('source ~/.bashrc')

        # Print path for debugging
        new_path = os.popen('echo $PATH').read().strip()
        print(f"Current PATH: {new_path}", flush=True)

    def set_java_home():
        java_home_path = f"/usr/lib/jvm/java-{OPENJDK_VERSION}-openjdk-amd64"
        os.environ['JAVA_HOME'] = java_home_path

        start_tag = '### START JAVA HOME ###'
        end_tag = '### END JAVA HOME ###'
        java_home_content = f'{start_tag}\nexport JAVA_HOME={java_home_path}\n{end_tag}\n'

        bashrc_path = os.path.expanduser('~/.bashrc')
        with open(bashrc_path, 'r+') as f:
            content = f.read()

            # Find the section marked by the comment tags
            start_index = content.find(start_tag)
            end_index = content.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                # If tags not found, append at the end
                f.seek(0, os.SEEK_END)
                f.write(java_home_content)
            else:
                # Replace the existing section between tags
                end_index += len(end_tag)
                before_section = content[:start_index]
                after_section = content[end_index:].lstrip()
                new_content = f'{before_section}{java_home_content}{after_section}'
                f.seek(0)
                f.write(new_content)
                f.truncate()

    def install_required_packages():
        """Install required packages using apt and setup environment."""
        set_java_home()
        os.system('source ~/.bashrc')

        # Install required packages via apt
        os.system('sudo apt update')
        os.system(f'sudo apt install -y openjdk-{OPENJDK_VERSION}-jdk')  # Ensure this matches the OPENJDK_VERSION
        os.system('sudo apt install -y gradle')

        android_home = SDK_DIR
        sdkmanager_path = os.path.join(android_home, 'cmdline-tools/latest/bin/sdkmanager')

        # Install platform-tools, emulator, and system image
        os.system(f'{sdkmanager_path} --install "platform-tools" "emulator" "system-images;android-30;google_apis;x86_64"')

        # Clean and set up PATH
        clean_and_setup_path()


    # Define other functions (uninstall, install_openjdk, etc.) and call them.
    def uninstall_old_jdk():
        """Uninstall old JDK versions."""
        run_command('sudo apt-get remove --purge -y openjdk-* || true')

    def install_openjdk():
        """Install OpenJDK."""
        print("Updating package lists...")
        run_command('sudo apt-get update')

        print("Uninstalling old JDK versions...")
        uninstall_old_jdk()

        print(f"Installing OpenJDK {OPENJDK_VERSION}...")
        run_command(f'sudo apt-get install -y openjdk-{OPENJDK_VERSION}-jdk')
        print(f"OpenJDK {OPENJDK_VERSION} installed.")

        # Set the default Java version
        java_home_path = f"/usr/lib/jvm/java-{OPENJDK_VERSION}-openjdk-amd64"
        java_path = f"{java_home_path}/bin/java"
        javac_path = f"{java_home_path}/bin/javac"

        run_command(f'sudo update-alternatives --install /usr/bin/java java {java_path} 1')
        run_command(f'sudo update-alternatives --set java {java_path}')

        run_command(f'sudo update-alternatives --install /usr/bin/javac javac {javac_path} 1')
        run_command(f'sudo update-alternatives --set javac {javac_path}')

        # Verify the Java version
        run_command("java -version")

        # Set JAVA_HOME in .bashrc
        bashrc_path = os.path.expanduser('~/.bashrc')
        start_tag = '### START JAVA HOME ###'
        end_tag = '### END JAVA HOME ###'
        java_home_content = f'{start_tag}\nexport JAVA_HOME={java_home_path}\n{end_tag}\n'

        with open(bashrc_path, 'r+') as f:
            content = f.read()

            # Find the section marked by the comment tags
            start_index = content.find(start_tag)
            end_index = content.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                # If tags not found, append at the end
                f.seek(0, os.SEEK_END)
                f.write(java_home_content)
            else:
                # Replace the existing section between tags
                end_index += len(end_tag)
                before_section = content[:start_index]
                after_section = content[end_index:].lstrip()
                new_content = f'{before_section}{java_home_content}{after_section}'
                f.seek(0)
                f.write(new_content)
                f.truncate()

        # Inform the user to update the environment variables
        print("Installation complete! Please restart your terminal or run the following command to update the environment variables:")
        print("source ~/.bashrc")


    def download_and_setup_cmdline_tools():
        """Download and set up the command line tools for Android SDK."""
        android_home = SDK_DIR
        cmdline_tools_dir = os.path.join(android_home, 'cmdline-tools')
        latest_dir = os.path.join(cmdline_tools_dir, 'latest')
        cmdline_tools_bin = os.path.join(latest_dir, 'bin')

        # Ensure the directory structure exists
        os.makedirs(cmdline_tools_dir, exist_ok=True)

        # Check if the command line tools zip file already exists
        if not os.path.exists(CMDLINE_TOOLS_ZIP):
            print("Downloading command line tools using curl...", flush=True)
            run_command(f'curl -L -o {CMDLINE_TOOLS_ZIP} {CMDLINE_TOOLS_URL}')
        else:
            print("Command line tools zip file already exists. Skipping download.", flush=True)

        # Extract command line tools to a temporary directory
        if not os.path.exists(cmdline_tools_bin):
            print("Extracting command line tools...", flush=True)
            with tempfile.TemporaryDirectory() as temp_dir:
                run_command(f'unzip -o {CMDLINE_TOOLS_ZIP} -d {temp_dir}')

                # Move the extracted cmdline-tools directory to its final location
                extracted_cmdline_tools_dir = os.path.join(temp_dir, 'cmdline-tools')
                if not os.path.exists(extracted_cmdline_tools_dir):
                    print("Extraction failed. Ensure the zip contains 'cmdline-tools' directory.")
                    return

                if os.path.exists(latest_dir):
                    shutil.rmtree(latest_dir)
                shutil.move(extracted_cmdline_tools_dir, latest_dir)
        else:
            print("Command-line tools already set up. Skipping extraction.", flush=True)

        # Verify that sdkmanager exists
        sdkmanager_path = os.path.join(latest_dir, 'bin', 'sdkmanager')
        if not os.path.exists(sdkmanager_path):
            print(f"sdkmanager not found at {sdkmanager_path}")
            return

        # Set environment variables
        os.environ['ANDROID_HOME'] = android_home
        os.environ['PATH'] += f':{cmdline_tools_bin}:{os.path.join(android_home, "platform-tools")}'

        # Update .bashrc or .zshrc
        bashrc_path = os.path.expanduser('~/.bashrc')
        start_tag = '### START CMDLINE TOOLS ###'
        end_tag = '### END CMDLINE TOOLS ###'
        tools_content = (
            f'{start_tag}\n'
            f'export ANDROID_HOME={android_home}\n'
            f'export PATH={cmdline_tools_bin}:{os.path.join(android_home, "platform-tools")}:$PATH\n'
            f'{end_tag}\n'
        )

        with open(bashrc_path, 'r+') as f:
            content = f.read()

            # Find the section marked by the comment tags
            start_index = content.find(start_tag)
            end_index = content.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                # If tags not found, append at the end
                f.seek(0, os.SEEK_END)
                f.write(tools_content)
            else:
                # Replace the existing section between tags
                end_index += len(end_tag)
                before_tools = content[:start_index]
                after_tools = content[end_index:]

                new_content = f'{before_tools}{tools_content}{after_tools}'
                f.seek(0)
                f.write(new_content)
                f.truncate()

    def install_flutter():
        """Install Flutter SDK using Snap and update PATH environment variable."""
        # Check if Flutter is already installed and uninstall it
        print("Checking if Flutter is already installed...")
        result = run_command('snap list | grep flutter')
        if result:
            print("Existing Flutter installation found. Removing it...")
            run_command('sudo snap remove flutter')
            print("Existing Flutter installation removed.")

        # Install Flutter via Snap with the specified channel
        print(f"Installing Flutter {FLUTTER_VERSION_CHANNEL} via Snap...")
        run_command(f'sudo snap install flutter --classic --channel={FLUTTER_VERSION_CHANNEL}')

        # Update .bashrc to include Flutter in PATH (Snap typically handles this)
        bashrc_path = os.path.expanduser('~/.bashrc')
        start_tag = '### START FLUTTER PATH ###'
        end_tag = '### END FLUTTER PATH ###'
        flutter_path_entry = 'export PATH=$PATH:/snap/bin'

        flutter_content = (
            f'{start_tag}\n'
            f'{flutter_path_entry}\n'
            f'{end_tag}\n'
        )

        with open(bashrc_path, 'r+') as f:
            content = f.read()

            # Find the section marked by the comment tags
            start_index = content.find(start_tag)
            end_index = content.find(end_tag, start_index)

            if start_index == -1 or end_index == -1:
                # If tags not found, append at the end
                f.seek(0, os.SEEK_END)
                f.write(flutter_content)
            else:
                # Replace the existing section between tags
                end_index += len(end_tag)
                before_flutter = content[:start_index]
                after_flutter = content[end_index:].lstrip()

                new_content = f'{before_flutter}{flutter_content}{after_flutter}'
                f.seek(0)
                f.write(new_content)
                f.truncate()

        # Inform the user to update the environment variables



    print("Removing previous installations before fresh install...")
    uninstall()
    print("Setting up OpenJDK...")
    install_openjdk()
    print("Setting up command-line tools...")
    download_and_setup_cmdline_tools()
    print("Installing required packages...")
    install_required_packages()
    print("Setting up Flutter SDK...")
    install_flutter()
    print("Setup complete! Please run the following command to update the environment variables:\n")
    #print("source ~/.bashrc")
    run_command_explicit("java -version")
    run_command("flutter --version")
    run_command("gradle --version")

def create_flutter_app(app_name):
    """Create a new Flutter app and add custom shell scripts."""

    def create_shell_script(script_path, script_content):
        """Create a shell script with the given content."""
        with open(script_path, 'w') as file:
            file.write(script_content)
        os.chmod(script_path, 0o755)


    # Paths and environment
    flutter_path = os.path.expanduser('~/flutter/bin')
    android_home = os.path.expanduser('~/Android/Sdk')
    os.environ['PATH'] += f':{flutter_path}:{os.path.join(android_home, "emulator")}:{os.path.join(android_home, "platform-tools")}'

    # Create Flutter app
    run_command(f'flutter create {app_name}')
    print(f"Flutter app '{app_name}' created.")

    # Define the scripts
    upload_script_content = r"""#!/bin/bash

# Define variables
PROJECT_DIR="$(pwd)"
APK_PATH="$PROJECT_DIR/build/app/outputs/flutter-apk/app-release.apk"
BUCKET_NAME="test_apk_bucket"
APK_FILENAME="app-release.apk"
VERSION_FILE="VERSION.json"
VERSION_FILE_PATH="gs://$BUCKET_NAME/$VERSION_FILE"
TEMP_VERSION_FILE="$PROJECT_DIR/$VERSION_FILE"

# Ensure the script exits on any error
set -e

# Build the APK
echo "Building the APK..."
flutter build apk --release

# Check if APK build was successful
if [ ! -f "$APK_PATH" ]; then
    echo "APK build failed. Exiting."
    exit 1
fi

# Download the existing VERSION.json file
echo "Downloading existing $VERSION_FILE from Google Cloud Storage..."
if gsutil cp "$VERSION_FILE_PATH" "$TEMP_VERSION_FILE"; then
  echo "VERSION.json downloaded successfully."
else
  echo "{\\"version\\": \\"1.0.0\\", \\"apk_url\\": \\"https://storage.googleapis.com/$BUCKET_NAME/$APK_FILENAME\\"}" > "$TEMP_VERSION_FILE"
fi

# Extract and increment the version number from VERSION.json
echo "Incrementing version number..."
if jq -r '.version' "$TEMP_VERSION_FILE" > /dev/null 2>&1; then
    CURRENT_VERSION=$(jq -r '.version' "$TEMP_VERSION_FILE" | awk -F. -v OFS=. '{$NF += 1 ; print}')
else
    CURRENT_VERSION="1.0.0"
fi

APK_URL="https://storage.googleapis.com/$BUCKET_NAME/$APK_FILENAME"

# Create a new VERSION.json with the incremented version number
jq ".version = \\"$CURRENT_VERSION\\" | .apk_url = \\"$APK_URL\\"" "$TEMP_VERSION_FILE" > "$TEMP_VERSION_FILE.tmp" && mv "$TEMP_VERSION_FILE.tmp" "$TEMP_VERSION_FILE"

# Upload the new APK
echo "Uploading the APK to Google Cloud Storage..."
gsutil cp "$APK_PATH" "gs://$BUCKET_NAME/$APK_FILENAME"

# Upload the updated VERSION.json
echo "Uploading updated $VERSION_FILE to Google Cloud Storage..."
gsutil cp "$TEMP_VERSION_FILE" "$VERSION_FILE_PATH"

# Clean up temporary files
rm "$TEMP_VERSION_FILE"

echo "Upload completed successfully. Version updated to $CURRENT_VERSION."
"""

    upgrade_script_content = r"""#!/bin/bash

# Define variables for the project directory
PROJECT_DIR="$(pwd)"
TMP_DIR="${PROJECT_DIR}/temp_backup"
LOCAL_PACKAGE_PATH="/home/rgw/Apps/rgwml_fl"  # Adjust the path as needed

# Step 1: Ensure we start from a clean state
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

# Backup the lib folder, upload.sh, and pubspec.yaml
if [ -d "$PROJECT_DIR/lib" ]; then
  cp -r "$PROJECT_DIR/lib" "$TMP_DIR/lib"
fi
cp "$PROJECT_DIR/upload.sh" "$TMP_DIR/upload.sh"
cp "$PROJECT_DIR/pubspec.yaml" "$TMP_DIR/pubspec.yaml"

# Remove all files and directories in the current project directory except the script itself and uploads.sh
find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 ! -name $(basename "$0") ! -name upload.sh -exec rm -rf {} \;

# Step 2: Create a new Flutter project in the current directory
echo "Creating a new Flutter project..."
flutter create .  # Create the project in the current directory

# Check if the project creation was successful
if [ $? -ne 0 ]; then
    echo "Failed to create a new Flutter project. Exiting."
    if [ -d "$TMP_DIR/lib" ]; then
      mv "$TMP_DIR/lib" "$PROJECT_DIR/lib"  # Restore lib folder if it existed
    fi
    mv "$TMP_DIR/upload.sh" "$PROJECT_DIR/upload.sh"  # Restore upload.sh
    mv "$TMP_DIR/pubspec.yaml" "$PROJECT_DIR/pubspec.yaml"  # Restore pubspec.yaml
    rm -rf "$TMP_DIR"  # Clean up temporary directory
    exit 1
fi

# Step 3: Restore the lib folder if it existed
if [ -d "$TMP_DIR/lib" ]; then
  echo "Restoring the lib folder..."
  rm -rf "$PROJECT_DIR/lib"
  mv "$TMP_DIR/lib" "$PROJECT_DIR/lib"
fi

# Restore upload.sh
echo "Restoring upload.sh..."
mv "$TMP_DIR/upload.sh" "$PROJECT_DIR/upload.sh"
chmod +x "$PROJECT_DIR/upload.sh"  # Ensure upload.sh remains executable

# Step 4: Add the local rgwml_fl package to pubspec.yaml if it's missing
echo "Adding local rgwml_fl package as a dependency..."
awk '/^dependencies:/ {print; print "  rgwml_fl:\\n    path: '"$LOCAL_PACKAGE_PATH"'"; next}1' "$PROJECT_DIR/pubspec.yaml" > "$PROJECT_DIR/pubspec_temp.yaml"
mv "$PROJECT_DIR/pubspec_temp.yaml" "$PROJECT_DIR/pubspec.yaml"

# Step 5: Run flutter pub get to install all dependencies
echo "Installing dependencies in the new project..."
flutter pub get

# Step 6: Clean up the temporary directory
rm -rf "$TMP_DIR"

# Step 7: Success message and next steps
echo "New Flutter project setup complete at $PROJECT_DIR."
echo "You can now manually adjust any additional configurations or settings as required."

# End of script
"""

    # Paths to the scripts
    app_path = os.path.join(os.getcwd(), app_name)
    upload_script_path = os.path.join(app_path, 'upload.sh')
    upgrade_script_path = os.path.join(app_path, 'flutter_framework_upgrade.sh')

    # Create the scripts
    create_shell_script(upload_script_path, upload_script_content)
    create_shell_script(upgrade_script_path, upgrade_script_content)

    print("Custom scripts 'upload.sh' and 'flutter_framework_upgrade.sh' have been added to the project root.")

def run_emulator():

    def kill_emulators():
        print("Killing all active emulators...")
        result = subprocess.run(['pkill', '-f', 'emulator -avd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("All emulators killed.")
        else:
            print("No emulators to kill or error occurred.")


    def clear_cache():
        print("Clearing the Android SDK manager cache...")
        cache_dir = os.path.expanduser('~/.android/cache')
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("Cache cleared.")
        else:
            print("Cache directory does not exist. No action required.")

    def dynamically_get_java_home():
        """Dynamically get the JAVA_HOME path for the specified JDK version."""
        java_paths = subprocess.getoutput("sudo update-alternatives --list java").splitlines()
        for path in java_paths:
            if f"java-{OPENJDK_VERSION}-openjdk-amd64" in path:
                return os.path.dirname(os.path.dirname(path))
        return None

    def setup_java_environment():
        # Ensure the correct JDK is installed
        #install_openjdk()

        # Dynamically set JAVA_HOME
        java_home = dynamically_get_java_home()
        if java_home and os.path.exists(java_home):
            os.environ["JAVA_HOME"] = java_home
            os.environ["PATH"] = f"{java_home}/bin:" + os.environ["PATH"]
            print(f"JAVA_HOME set to {java_home}")
        else:
            print(f"Error: JAVA_HOME path does not exist: {java_home}")


    print("Running emulator...")

    setup_java_environment()
    # Kill all active emulators
    kill_emulators()

    # Clear cache
    clear_cache()

    # Ensure system image is installed
    sdkmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/sdkmanager')
    if not os.path.exists(sdkmanager_path):
        print(f"sdkmanager not found at {sdkmanager_path}")
        download_and_setup_cmdline_tools()  # Attempt to set up the SDK manager again

    print(f"Installing system image: {SYSTEM_IMAGE}")
    result = subprocess.run([sdkmanager_path, '--install', SYSTEM_IMAGE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("System image installed.")
    else:
        print(f"Failed to install system image. Error: {result.stderr.decode().strip()}")
        return

    # Create AVD
    avdmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/avdmanager')
    if not os.path.exists(avdmanager_path):
        print(f"avdmanager not found at {avdmanager_path}")
        return

    avd_name = "test_AVD"
    result = subprocess.run([avdmanager_path, 'create', 'avd', '-n', avd_name, '-k', SYSTEM_IMAGE, '--device', 'pixel', '--force'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("AVD created.")
    else:
        print(f"Failed to create AVD. Error: {result.stderr.decode().strip()}")
        return

    # Start Emulator
    emulator_path = os.path.join(SDK_DIR, 'emulator/emulator')
    if not os.path.exists(emulator_path):
        print(f"emulator not found at {emulator_path}")
        return

    print(f"Starting emulator: {avd_name}")
    subprocess.Popen([emulator_path, '-avd', avd_name])

    # Allow time for the emulator to start
    time.sleep(30)
    print("Emulator should be running now.")

def main():
    parser = argparse.ArgumentParser(description="Install or Uninstall Android SDK, Gradle, Flutter, OpenJDK, and manage Flutter apps.")
    parser.add_argument('--install', action='store_true', help='Install the tools')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the tools')
    parser.add_argument('--create', type=str, metavar='APP_NAME', help='Create a new Flutter app with the specified name')
    parser.add_argument('--emulator', action='store_true', help='Run an Android emulator')

    args = parser.parse_args()

    if args.install:
        install()
    elif args.uninstall:
        uninstall()
    elif args.create:
        create_flutter_app(args.create)
    elif args.emulator:
        run_emulator()
    else:
        print("Please specify --install, --uninstall, --create APP_NAME, or --emulator")

if __name__ == "__main__":
    main()

