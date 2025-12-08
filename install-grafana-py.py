#!/usr/bin/env python3
"""
Install Grafana - Cross-Platform Script
Downloads and installs Grafana
"""

import subprocess
import sys
import os
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    print()

def get_grafana_download_url():
    """Get the correct Grafana download URL for the OS"""
    VERSION = "10.2.3"
    system = platform.system()
    
    if system == "Windows":
        return f"https://dl.grafana.com/oss/release/grafana-{VERSION}.windows-amd64.zip", "zip"
    elif system == "Linux":
        return f"https://dl.grafana.com/oss/release/grafana-{VERSION}.linux-amd64.tar.gz", "tar"
    elif system == "Darwin":  # macOS
        return f"https://dl.grafana.com/oss/release/grafana-{VERSION}.darwin-amd64.tar.gz", "tar"
    else:
        raise Exception(f"Unsupported operating system: {system}")

def get_install_directory():
    """Get installation directory based on OS"""
    system = platform.system()
    
    if system == "Windows":
        return Path("C:/grafana")
    else:
        home = Path.home()
        return home / "grafana"

def download_file(url, dest):
    """Download file with progress"""
    print_color(f"Downloading from: {url}", Colors.BLUE)
    print_color("This may take a few minutes...", Colors.YELLOW)
    
    try:
        urllib.request.urlretrieve(url, dest)
        print_color("✅ Download complete", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"❌ Download failed: {e}", Colors.RED)
        return False

def extract_archive(archive_path, extract_to, archive_type):
    """Extract zip or tar.gz archive"""
    print_color("Extracting archive...", Colors.BLUE)
    
    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        else:  # tar
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        
        print_color("✅ Extraction complete", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"❌ Extraction failed: {e}", Colors.RED)
        return False

def main():
    print_header("📥 Installing Grafana")
    
    # Get download URL and install directory
    try:
        download_url, archive_type = get_grafana_download_url()
        install_dir = get_install_directory()
    except Exception as e:
        print_color(f"❌ {e}", Colors.RED)
        sys.exit(1)
    
    print_color(f"Installation directory: {install_dir}", Colors.YELLOW)
    print()
    
    # Create installation directory
    print_color("Creating installation directory...", Colors.BLUE)
    install_dir.mkdir(parents=True, exist_ok=True)
    print_color(f"✅ Directory created: {install_dir}", Colors.GREEN)
    print()
    
    # Download Grafana
    temp_dir = Path.home() / "temp_grafana"
    temp_dir.mkdir(exist_ok=True)
    
    archive_name = f"grafana.{archive_type}"
    archive_path = temp_dir / archive_name
    
    if not download_file(download_url, archive_path):
        sys.exit(1)
    print()
    
    # Extract archive
    if not extract_archive(archive_path, temp_dir, archive_type):
        sys.exit(1)
    print()
    
    # Find extracted folder and move files
    print_color("Installing Grafana files...", Colors.BLUE)
    
    extracted_folders = [d for d in temp_dir.iterdir() if d.is_dir() and d.name.startswith("grafana-")]
    
    if not extracted_folders:
        print_color("❌ Could not find extracted files", Colors.RED)
        sys.exit(1)
    
    extracted_folder = extracted_folders[0]
    
    # Move files to install directory
    for item in extracted_folder.iterdir():
        dest = install_dir / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(install_dir))
    
    print_color("✅ Files installed", Colors.GREEN)
    print()
    
    # Cleanup
    print_color("Cleaning up temporary files...", Colors.BLUE)
    shutil.rmtree(temp_dir)
    print_color("✅ Cleanup complete", Colors.GREEN)
    print()
    
    # Final instructions
    print_header("✅ Grafana Installation Complete!")
    
    print_color(f"Grafana installed at: {install_dir}", Colors.YELLOW)
    print()
    print_color("Next steps:", Colors.CYAN)
    print(f"1. Start Grafana:")
    
    if platform.system() == "Windows":
        print(f"   cd {install_dir}\\bin")
        print(f"   .\\grafana-server.exe")
    else:
        print(f"   cd {install_dir}/bin")
        print(f"   ./grafana-server")
    
    print()
    print(f"2. Access Grafana at: http://localhost:3000")
    print(f"   Default login: admin / admin")
    print()
    print_color("3. Add Prometheus data source:", Colors.CYAN)
    print("   - Click 'Add your first data source'")
    print("   - Select 'Prometheus'")
    print("   - URL: http://localhost:9090")
    print("   - Click 'Save & Test'")
    print()
    print_color("Or run the automated setup script:", Colors.CYAN)
    print("   python setup-monitoring.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Installation cancelled", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Installation failed: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
