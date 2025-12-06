#!/usr/bin/env python3
"""
Setup Prometheus and Grafana Monitoring - Python Version
Install and configure monitoring stack for Football Introduction App
"""

import subprocess
import sys
import time

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

def print_step(step_num, text):
    print()
    print_color(f"📋 Step {step_num}: {text}", Colors.BLUE)

def run_command(command, check=True, capture_output=True):
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

def check_helm():
    """Check if Helm is installed"""
    try:
        subprocess.run("helm version", shell=True, check=True, capture_output=True)
        return True
    except:
        return False

def main():
    print_header("📊 Setting up Prometheus & Grafana Monitoring")

    # Step 1: Check prerequisites
    print_step(1, "Checking prerequisites...")
    
    if not check_helm():
        print_color("❌ Helm is required but not installed", Colors.RED)
        print_color("Install Helm from: https://helm.sh/docs/intro/install/", Colors.YELLOW)
        print()
        print("Quick install:")
        print("  Windows: choco install kubernetes-helm")
        print("  Mac: brew install helm")
        print("  Linux: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
        sys.exit(1)
    print_color("✅ Helm is installed", Colors.GREEN)

    # Step 2: Add Helm repositories
    print_step(2, "Adding Helm repositories...")
    
    print_color("Adding Prometheus community repo...", Colors.BLUE)
    run_command("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    
    print_color("Adding Grafana repo...", Colors.BLUE)
    run_command("helm repo add grafana https://grafana.github.io/helm-charts")
    
    print_color("Updating Helm repos...", Colors.BLUE)
    run_command("helm repo update")
    
    print_color("✅ Helm repositories added", Colors.GREEN)

    # Step 3: Create monitoring namespace
    print_step(3, "Creating monitoring namespace...")
    run_command("kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -")
    print_color("✅ Monitoring namespace created", Colors.GREEN)

    # Step 4: Install Prometheus
    print_step(4, "Installing Prometheus...")
    print_color("This may take 2-3 minutes...", Colors.YELLOW)
    
    prometheus_cmd = """helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --set prometheus.service.type=NodePort \
        --set prometheus.service.nodePort=30090 \
        --set grafana.service.type=NodePort \
        --set grafana.service.nodePort=30091 \
        --set grafana.adminPassword=admin"""
    
    if run_command(prometheus_cmd, check=False, capture_output=False):
        print_color("✅ Prometheus installed successfully", Colors.GREEN)
    else:
        print_color("⚠️  Prometheus installation may have issues", Colors.YELLOW)

    # Step 5: Wait for pods to be ready
    print_step(5, "Waiting for monitoring pods to be ready...")
    print_color("This may take 3-5 minutes...", Colors.YELLOW)
    
    timeout = 300
    elapsed = 0
    
    while elapsed < timeout:
        try:
            result = subprocess.run(
                "kubectl get pods -n monitoring -o jsonpath='{.items[*].status.phase}'",
                shell=True,
                capture_output=True,
                text=True
            )
            
            phases = result.stdout.strip().split()
            if phases and all(phase == "Running" for phase in phases):
                print_color("✅ All monitoring pods are running", Colors.GREEN)
                break
        except:
            pass
        
        print_color(f"Waiting... ({elapsed} seconds)", Colors.YELLOW)
        time.sleep(10)
        elapsed += 10

    # Step 6: Show status
    print_step(6, "Checking deployment status...")
    print()
    print_color("Monitoring Pods:", Colors.CYAN)
    run_command("kubectl get pods -n monitoring", capture_output=False)
    
    print()
    print_color("Services:", Colors.CYAN)
    run_command("kubectl get svc -n monitoring", capture_output=False)

    # Final instructions
    print_header("✅ Monitoring Setup Complete!")
    
    print_color("Access Prometheus:", Colors.YELLOW)
    print("  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090")
    print("  Then open: http://localhost:9090")
    print()
    
    print_color("Access Grafana:", Colors.YELLOW)
    print("  kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80")
    print("  Then open: http://localhost:3000")
    print("  Username: admin")
    print("  Password: admin")
    print()
    
    print_color("Next steps:", Colors.CYAN)
    print("1. Port-forward to access dashboards")
    print("2. Import custom dashboards: python import-dashboards.py")
    print("3. Configure application metrics: python configure-app-metrics.py")
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