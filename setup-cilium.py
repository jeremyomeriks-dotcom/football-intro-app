#!/usr/bin/env python3
"""
Setup Cilium on Kind Cluster - Python Script
Cross-platform script to setup Cilium network policies on Kind
"""

import subprocess
import sys
import time

class Colors:
    """ANSI color codes for terminal output"""
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """Print a header with decorative line"""
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color(text, Colors.CYAN)
    print_color("=" * 60, Colors.CYAN)
    print()

def print_step(step_num, text):
    """Print a step header"""
    print()
    print_color(f"📋 Step {step_num}: {text}", Colors.BLUE)

def run_command(command, description=None, check=True, capture_output=True):
    """Run a shell command and handle errors"""
    if description:
        print_color(description, Colors.BLUE)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=capture_output
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Error: {e}", Colors.RED)
            if e.stderr:
                print(e.stderr)
        return False

def check_command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run(
            f"{command} --version",
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except:
        try:
            subprocess.run(
                f"{command} version",
                shell=True,
                check=True,
                capture_output=True
            )
            return True
        except:
            return False

def check_docker_running():
    """Check if Docker is running"""
    try:
        subprocess.run(
            "docker ps",
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except:
        return False

def cluster_exists(cluster_name):
    """Check if Kind cluster exists"""
    try:
        result = subprocess.run(
            "kind get clusters",
            shell=True,
            capture_output=True,
            text=True
        )
        return cluster_name in result.stdout
    except:
        return False

def main():
    print_header("🔷 Setting up Cilium Network Policies on Kind")

    # Step 1: Check prerequisites
    print_step(1, "Checking prerequisites...")
    
    # Check Docker
    if not check_docker_running():
        print_color("❌ Docker is not running. Please start Docker Desktop.", Colors.RED)
        sys.exit(1)
    print_color("✅ Docker is running", Colors.GREEN)

    # Check kind
    if not check_command_exists("kind"):
        print_color("❌ kind is not installed. Please install it first.", Colors.RED)
        print_color("Install from: https://kind.sigs.k8s.io/docs/user/quick-start/", Colors.YELLOW)
        sys.exit(1)
    print_color("✅ kind is installed", Colors.GREEN)

    # Check kubectl
    if not check_command_exists("kubectl"):
        print_color("❌ kubectl is not installed. Please install it first.", Colors.RED)
        sys.exit(1)
    print_color("✅ kubectl is installed", Colors.GREEN)

    # Step 2: Check for existing cluster
    print_step(2, "Checking for existing cluster...")
    
    if cluster_exists("football-app-cluster"):
        print_color("⚠️  Cluster 'football-app-cluster' already exists", Colors.YELLOW)
        response = input("Do you want to delete and recreate it with Cilium? (y/n): ").lower()
        
        if response == 'y':
            print_color("Deleting existing cluster...", Colors.YELLOW)
            if run_command("kind delete cluster --name football-app-cluster", check=False):
                print_color("✅ Cluster deleted", Colors.GREEN)
            else:
                print_color("⚠️  Error deleting cluster, but continuing...", Colors.YELLOW)
        else:
            print_color("❌ Cannot proceed with existing cluster. Exiting.", Colors.RED)
            sys.exit(1)

    # Step 3: Create Kind cluster with Cilium configuration
    print_step(3, "Creating Kind cluster with Cilium support...")
    print_color("Using: kind-config-cilium.yaml", Colors.YELLOW)
    
    if not run_command("kind create cluster --config kind-config-cilium.yaml", capture_output=False):
        print_color("❌ Failed to create cluster", Colors.RED)
        sys.exit(1)
    print_color("✅ Cluster created successfully", Colors.GREEN)

    # Step 4: Install Cilium
    print_step(4, "Installing Cilium...")
    print_color("Note: Using Helm method for best compatibility", Colors.YELLOW)

    # Check if Helm is installed
    helm_installed = check_command_exists("helm")
    
    if helm_installed:
        print_color("✅ Helm is installed", Colors.GREEN)
        
        # Add Cilium Helm repository
        print_color("Adding Cilium Helm repository...", Colors.BLUE)
        run_command("helm repo add cilium https://helm.cilium.io/", check=False)
        run_command("helm repo update")
        
        # Install Cilium
        print_color("Installing Cilium...", Colors.BLUE)
        cilium_install_cmd = (
            "helm install cilium cilium/cilium --version 1.14.5 "
            "--namespace kube-system "
            "--set kubeProxyReplacement=strict "
            "--set k8sServiceHost=football-app-cluster-control-plane "
            "--set k8sServicePort=6443"
        )
        
        if run_command(cilium_install_cmd, check=False):
            print_color("✅ Cilium installed", Colors.GREEN)
        else:
            print_color("⚠️  Cilium installation may have issues, but continuing...", Colors.YELLOW)
    else:
        print_color("⚠️  Helm not found. Installing Cilium using kubectl...", Colors.YELLOW)
        
        # Install Cilium using kubectl
        print_color("Installing Cilium using kubectl...", Colors.BLUE)
        cilium_url = "https://raw.githubusercontent.com/cilium/cilium/v1.14.5/install/kubernetes/quick-install.yaml"
        
        if run_command(f"kubectl apply -f {cilium_url}", check=False):
            print_color("✅ Cilium installed", Colors.GREEN)
        else:
            print_color("⚠️  Cilium installation may have issues, but continuing...", Colors.YELLOW)

    # Step 5: Wait for Cilium to be ready
    print_step(5, "Waiting for Cilium to be ready...")
    print_color("This may take 2-3 minutes...", Colors.YELLOW)

    timeout = 300
    elapsed = 0
    cilium_ready = False

    while elapsed < timeout:
        try:
            result = subprocess.run(
                "kubectl get pods -n kube-system -l k8s-app=cilium -o jsonpath='{.items[*].status.phase}'",
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            
            if "Running" in result.stdout:
                print_color("✅ Cilium pods are running", Colors.GREEN)
                cilium_ready = True
                break
        except:
            pass
        
        print_color(f"Waiting... ({elapsed} seconds)", Colors.YELLOW)
        time.sleep(10)
        elapsed += 10

    if not cilium_ready:
        print_color("⚠️  Timeout waiting for Cilium, but continuing...", Colors.YELLOW)

    # Check Cilium status
    print()
    print_color("Cilium Pods Status:", Colors.CYAN)
    run_command("kubectl get pods -n kube-system -l k8s-app=cilium", capture_output=False)

    # Final message
    print_header("✅ Cilium Setup Complete!")
    
    print_color("Next steps:", Colors.YELLOW)
    print("1. Deploy your application: python deploy-with-cilium.py")
    print("2. Apply network policies: kubectl apply -f network-policies/")
    print("3. Test policies: python test-network-policies.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Setup interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)