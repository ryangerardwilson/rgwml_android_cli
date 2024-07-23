#!/usr/bin/env python3
import subprocess
import os
import argparse
import shutil
import time

# Static variables for URLs and version numbers
CMDLINE_TOOLS_URL = 'https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip'
CMDLINE_TOOLS_ZIP = os.path.expanduser('~/cmdline-tools.zip')

GRADLE_VERSION = '7.2'
GRADLE_URL = f'https://services.gradle.org/distributions/gradle-{GRADLE_VERSION}-bin.zip'
GRADLE_ZIP = f'/tmp/gradle-{GRADLE_VERSION}-bin.zip'

FLUTTER_VERSION = '3.22.0'
FLUTTER_URL = f'https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_{FLUTTER_VERSION}-stable.tar.xz'
FLUTTER_TAR = os.path.expanduser('~/flutter_linux.tar.xz')

OPENJDK_VERSION = '11'


# Static variables for emulator configuration
SDK_DIR = os.path.expanduser('~/Android/Sdk')
EMULATOR_DEVICE = 'pixel'
ANDROID_VERSION = '30'
SYSTEM_IMAGE = f"system-images;android-{ANDROID_VERSION};google_apis;x86_64"
AVD_NAME = 'my_avd'


def run_command(command, check=True):
    """Run a shell command and handle errors."""
    try:
        return subprocess.run(command, shell=True, executable="/bin/bash", text=True, capture_output=True, check=check)
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Command failed: {e}")
            exit(1)
        return e


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
    uninstall_cmdline_tools()
    print("Uninstalling Gradle...")
    uninstall_gradle()
    print("Uninstalling Flutter...")
    uninstall_flutter()
    print("Uninstalling OpenJDK...")
    uninstall_openjdk()
    print("Uninstallation complete!")

def install():
    """Install Android SDK tools, packages, Gradle, Flutter, and OpenJDK."""
    def download_and_setup_cmdline_tools():
        """Download and set up the command line tools for Android SDK."""
        android_home = os.path.expanduser('~/Android/Sdk')
        cmdline_tools_dir = os.path.join(android_home, 'cmdline-tools')
        latest_dir = os.path.join(cmdline_tools_dir, 'latest')

        # Ensure the directory structure exists
        os.makedirs(cmdline_tools_dir, exist_ok=True)

        # Download and extract command line tools
        run_command(f'wget -O {CMDLINE_TOOLS_ZIP} {CMDLINE_TOOLS_URL}')
        run_command(f'unzip -o {CMDLINE_TOOLS_ZIP} -d {cmdline_tools_dir}')
        run_command(f'mv -v {cmdline_tools_dir}/cmdline-tools {latest_dir}')

        # Cleanup zip file
        os.remove(CMDLINE_TOOLS_ZIP)

        # Set environment variables
        os.environ['ANDROID_HOME'] = android_home
        os.environ['PATH'] += f':{os.path.join(latest_dir, "bin")}:{os.path.join(android_home, "platform-tools")}:$PATH'

        # Update .bashrc or .zshrc
        with open(os.path.expanduser('~/.bashrc'), 'a') as f:
            f.write(f'\nexport ANDROID_HOME={android_home}')
            f.write(f'\nexport PATH=$PATH:{os.path.join(latest_dir, "bin")}:{os.path.join(android_home, "platform-tools")}\n')

    def install_required_packages():
        """Install required packages using the new sdkmanager and download Gradle."""
        android_home = os.path.expanduser('~/Android/Sdk')
        sdkmanager_path = os.path.join(android_home, 'cmdline-tools/latest/bin/sdkmanager')

        # Install platform-tools, emulator, and system image
        run_command(f'{sdkmanager_path} --install "platform-tools" "emulator" "system-images;android-30;google_apis;x86_64"')

        # Download and set up Gradle
        gradle_dir = f'/opt/gradle/gradle-{GRADLE_VERSION}'
        run_command(f'sudo mkdir -p /opt/gradle')
        run_command(f'wget -O {GRADLE_ZIP} {GRADLE_URL}')
        run_command(f'sudo unzip -o -d /opt/gradle {GRADLE_ZIP}')

        # Cleanup zip file
        os.remove(GRADLE_ZIP)

        # Update .bashrc or .zshrc for Gradle
        with open(os.path.expanduser('~/.bashrc'), 'a') as f:
            f.write(f'\nexport PATH=$PATH:{gradle_dir}/bin\n')

    def install_flutter():
        """Download and setup Flutter SDK."""
        flutter_base_dir = os.path.expanduser('~/flutter')

        run_command(f'wget -O {FLUTTER_TAR} {FLUTTER_URL}')
        if os.path.exists(flutter_base_dir):
            shutil.rmtree(flutter_base_dir)
        os.makedirs(flutter_base_dir, exist_ok=True)
        run_command(f'tar -xf {FLUTTER_TAR} -C {flutter_base_dir} --strip-components=1')

        # Cleanup tar file
        os.remove(FLUTTER_TAR)

        # Update .bashrc or .zshrc for Flutter
        with open(os.path.expanduser('~/.bashrc'), 'a') as f:
            f.write(f'\nexport PATH=$PATH:{flutter_base_dir}/bin\n')

    def install_openjdk():
        """Install OpenJDK."""
        run_command(f'sudo apt-get update')
        run_command(f'sudo apt-get install -y openjdk-{OPENJDK_VERSION}-jdk')
        print(f"OpenJDK {OPENJDK_VERSION} installed.")

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
    print("source ~/.bashrc")

def create_shell_script(script_path, script_content):
    """Create a shell script with the given content."""
    with open(script_path, 'w') as file:
        file.write(script_content)
    os.chmod(script_path, 0o755)

def create_flutter_app(app_name):
    """Create a new Flutter app and add custom shell scripts."""
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


def run_emulator():
    print("Running emulator...")

    # Kill all active emulators
    kill_emulators()
    
    # Clear cache
    clear_cache()
    
    # Ensure system image is installed
    sdkmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/sdkmanager')
    print(f"Installing system image: {SYSTEM_IMAGE}")
    result = subprocess.run([sdkmanager_path, '--install', SYSTEM_IMAGE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("System image installed.")
    else:
        print("Failed to install system image.")
        return

    # Create AVD
    avdmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/avdmanager')
    print(f"Creating AVD: {AVD_NAME}")
    subprocess.run([avdmanager_path, 'create', 'avd', '-n', AVD_NAME, '-k', SYSTEM_IMAGE, '--device', EMULATOR_DEVICE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Start Emulator
    emulator_path = os.path.join(SDK_DIR, 'emulator/emulator')
    print(f"Starting emulator: {AVD_NAME}")
    subprocess.Popen([emulator_path, '-avd', AVD_NAME])

    # Allow time for the emulator to start
    time.sleep(30)
    print("Emulator should be running now.")

def run_new_emulator():
    print("Running new (maiden) emulator...")

    # Kill all active emulators
    kill_emulators()
    
    # Clear cache
    clear_cache()
    
    # Ensure system image is installed
    sdkmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/sdkmanager')
    print(f"Installing system image: {SYSTEM_IMAGE}")
    result = subprocess.run([sdkmanager_path, '--install', SYSTEM_IMAGE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("System image installed.")
    else:
        print("Failed to install system image.")
        return

    # Create new (maiden) AVD
    new_avd_name = AVD_NAME + "_new"
    avdmanager_path = os.path.join(SDK_DIR, 'cmdline-tools/latest/bin/avdmanager')
    print(f"Creating new AVD: {new_avd_name}")
    subprocess.run([avdmanager_path, 'create', 'avd', '-n', new_avd_name, '-k', SYSTEM_IMAGE, '--device', EMULATOR_DEVICE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Start New Emulator
    emulator_path = os.path.join(SDK_DIR, 'emulator/emulator')
    print(f"Starting new emulator: {new_avd_name}")
    subprocess.Popen([emulator_path, '-avd', new_avd_name])

    # Allow time for the emulator to start
    time.sleep(30)
    print("New emulator should be running now.")

def main():
    parser = argparse.ArgumentParser(description="Install or Uninstall Android SDK, Gradle, Flutter, OpenJDK, and manage Flutter apps.")
    parser.add_argument('--install', action='store_true', help='Install the tools')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the tools')
    parser.add_argument('--create', type=str, metavar='APP_NAME', help='Create a new Flutter app with the specified name')
    parser.add_argument('--emulator', action='store_true', help='Run an Android emulator')
    parser.add_argument('--new', action='store_true', help='Run a fresh new Android emulator')

    args = parser.parse_args()

    if args.install:
        install()
    elif args.uninstall:
        uninstall()
    elif args.create:
        create_flutter_app(args.create)
    elif args.emulator and args.new:
        run_new_emulator()
    elif args.emulator:
        run_emulator()
    else:
        print("Please specify --install, --uninstall, --create APP_NAME, or --emulator")


if __name__ == "__main__":
    main()
