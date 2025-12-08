#!/usr/bin/env python3
"""
Install Prometheus - Cross-Platform Script
Downloads and installs Prometheus with Node Exporter configuration
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

def get_prometheus_download_url():
    """Get the correct Prometheus download URL for the OS"""
    VERSION = "2.48.0"
    system = platform.system()
    
    if system == "Windows":
        return f"https://github.com/prometheus/prometheus/releases/download/v{VERSION}/prometheus-{VERSION}.windows-amd64.zip", "zip"
    elif system == "Linux":
        return f"https://github.com/prometheus/prometheus/releases/download/v{VERSION}/prometheus-{VERSION}.linux-amd64.tar.gz", "tar"
    elif system == "Darwin":  # macOS
        return f"https://github.com/prometheus/prometheus/releases/download/v{VERSION}/prometheus-{VERSION}.darwin-amd64.tar.gz", "tar"
    else:
        raise Exception(f"Unsupported operating system: {system}")

def get_install_directory():
    """Get installation directory based on OS"""
    system = platform.system()
    
    if system == "Windows":
        return Path("C:/prometheus")
    else:
        home = Path.home()
        return home / "prometheus"

def download_file(url, dest):
    """Download file with progress"""
    print_color(f"Downloading from: {url}", Colors.BLUE)
    
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

def find_node_exporter():
    """Try to find Node Exporter on the system"""
    print_color("Checking for Node Exporter...", Colors.BLUE)
    
    # Common locations
    possible_locations = [
        "node_exporter",
        "/usr/local/bin/node_exporter",
        "/usr/bin/node_exporter",
        "C:\\node_exporter\\node_exporter.exe",
        str(Path.home() / "node_exporter" / "node_exporter.exe"),
    ]
    
    # Check if running
    try:
        result = subprocess.run(
            "curl -s http://localhost:9100/metrics",
            shell=True,
            capture_output=True,
            text=True
        )
        if "node_" in result.stdout:
            print_color("✅ Node Exporter is running on port 9100", Colors.GREEN)
            return True
    except:
        pass
    
    print_color("⚠️  Node Exporter not detected on port 9100", Colors.YELLOW)
    print_color("Make sure Node Exporter is running before starting Prometheus", Colors.YELLOW)
    return False

def create_prometheus_config(install_dir):
    """Create prometheus.yml with Node Exporter configuration"""
    print_color("Creating prometheus.yml configuration...", Colors.BLUE)
    
    config = """# Prometheus Configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'football-app-monitor'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: []

# Load rules once and periodically evaluate them
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus'

  # Node Exporter
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          instance: 'localhost'
          environment: 'development'

  # Football App (if running in Kubernetes)
  # - job_name: 'football-app'
  #   kubernetes_sd_configs:
  #     - role: pod
  #   relabel_configs:
  #     - source_labels: [__meta_kubernetes_pod_label_app]
  #       action: keep
  #       regex: football-intro-app
"""
    
    config_path = install_dir / "prometheus.yml"
    
    try:
        with open(config_path, 'w') as f:
            f.write(config)
        print_color(f"✅ Configuration created at: {config_path}", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"❌ Failed to create config: {e}", Colors.RED)
        return False

def main():
    print_header("📥 Installing Prometheus")
    
    # Get download URL and install directory
    try:
        download_url, archive_type = get_prometheus_download_url()
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
    
    # Download Prometheus
    temp_dir = Path.home() / "temp_prometheus"
    temp_dir.mkdir(exist_ok=True)
    
    archive_name = f"prometheus.{archive_type}"
    archive_path = temp_dir / archive_name
    
    if not download_file(download_url, archive_path):
        sys.exit(1)
    print()
    
    # Extract archive
    if not extract_archive(archive_path, temp_dir, archive_type):
        sys.exit(1)
    print()
    
    # Find extracted folder and move files
    print_color("Installing Prometheus files...", Colors.BLUE)
    
    extracted_folders = [d for d in temp_dir.iterdir() if d.is_dir() and d.name.startswith("prometheus-")]
    
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
    
    # Check for Node Exporter
    find_node_exporter()
    print()
    
    # Create configuration
    create_prometheus_config(install_dir)
    print()
    
    # Final instructions
    print_header("✅ Prometheus Installation Complete!")
    
    print_color(f"Prometheus installed at: {install_dir}", Colors.YELLOW)
    print()
    print_color("Next steps:", Colors.CYAN)
    print(f"1. Start Node Exporter (if not already running)")
    print(f"2. Start Prometheus:")
    
    if platform.system() == "Windows":
        print(f"   cd {install_dir}")
        print(f"   .\\prometheus.exe")
    else:
        print(f"   cd {install_dir}")
        print(f"   ./prometheus")
    
    print()
    print(f"3. Access Prometheus at: http://localhost:9090")
    print(f"4. Check targets at: http://localhost:9090/targets")
    print()
    print_color("To install Grafana, run:", Colors.CYAN)
    print("   python install-grafana.py")
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
