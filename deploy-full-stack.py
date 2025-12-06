#!/usr/bin/env python3
"""
Deploy Full Stack - Python Version
Deploy Football App with BOTH Cilium network policies AND Prometheus monitoring
"""

import subprocess
import sys
import time
import os

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

def check_cluster_exists():
    """Check if Kind cluster exists"""
    try:
        result = subprocess.run(
            "kind get clusters",
            shell=True,
            capture_output=True,
            text=True
        )
        return "football-app-cluster" in result.stdout
    except:
        return False

def check_cilium_exists():
    """Check if Cilium is installed"""
    try:
        result = subprocess.run(
            "kubectl get pods -n kube-system -l k8s-app=cilium",
            shell=True,
            capture_output=True,
            text=True
        )
        return "cilium" in result.stdout
    except:
        return False

def check_monitoring_exists():
    """Check if monitoring is installed"""
    try:
        result = subprocess.run(
            "kubectl get namespace monitoring",
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def main():
    print_header("🚀 Deploy Full Stack: App + Cilium + Monitoring")

    # Check cluster status
    print_color("Checking existing setup...", Colors.BLUE)
    
    has_cluster = check_cluster_exists()
    has_cilium = check_cilium_exists() if has_cluster else False
    has_monitoring = check_monitoring_exists() if has_cluster else False
    
    print()
    print_color("Current Status:", Colors.CYAN)
    print(f"  Cluster:    {'✅ Exists' if has_cluster else '❌ Not found'}")
    print(f"  Cilium:     {'✅ Installed' if has_cilium else '❌ Not installed'}")
    print(f"  Monitoring: {'✅ Installed' if has_monitoring else '❌ Not installed'}")
    print()

    # Step 1: Setup Cilium if needed
    if not has_cluster or not has_cilium:
        print_step(1, "Setting up Cilium cluster...")
        print_color("Running: python setup-cilium.py", Colors.YELLOW)
        
        if not run_command("python setup-cilium.py", capture_output=False):
            print_color("❌ Cilium setup failed", Colors.RED)
            sys.exit(1)
        
        print_color("✅ Cilium cluster ready", Colors.GREEN)
    else:
        print_step(1, "Cilium cluster already exists")
        print_color("✅ Skipping Cilium setup", Colors.GREEN)

    # Step 2: Setup Monitoring if needed
    if not has_monitoring:
        print_step(2, "Setting up Prometheus & Grafana...")
        print_color("Running: python setup-monitoring.py", Colors.YELLOW)
        
        if not run_command("python setup-monitoring.py", capture_output=False):
            print_color("❌ Monitoring setup failed", Colors.RED)
            sys.exit(1)
        
        print_color("✅ Monitoring stack ready", Colors.GREEN)
    else:
        print_step(2, "Monitoring stack already exists")
        print_color("✅ Skipping monitoring setup", Colors.GREEN)

    # Step 3: Build Docker image with metrics support
    print_step(3, "Building Docker image with metrics...")
    
    dockerfile = "Dockerfile.metrics" if os.path.exists("Dockerfile.metrics") else "Dockerfile"
    build_cmd = f"docker build -f {dockerfile} -t football-intro-app:local ."
    
    if not run_command(build_cmd, capture_output=False):
        print_color("❌ Failed to build image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image built", Colors.GREEN)

    # Step 4: Load image into Kind cluster
    print_step(4, "Loading image into Kind cluster...")
    if not run_command("kind load docker-image football-intro-app:local --name football-app-cluster", 
                      capture_output=False):
        print_color("❌ Failed to load image", Colors.RED)
        sys.exit(1)
    print_color("✅ Image loaded", Colors.GREEN)

    # Step 5: Deploy application with metrics
    print_step(5, "Deploying application...")
    
    deployment_file = "k8s/deployment-with-metrics.yaml" if os.path.exists("k8s/deployment-with-metrics.yaml") else "k8s/deployment.yaml"
    
    if not run_command(f"kubectl apply -f {deployment_file}"):
        print_color("❌ Failed to deploy application", Colors.RED)
        sys.exit(1)
    
    if not run_command("kubectl apply -f k8s/service.yaml"):
        print_color("❌ Failed to deploy service", Colors.RED)
        sys.exit(1)
    
    print_color("✅ Application deployed", Colors.GREEN)

    # Step 6: Deploy ServiceMonitor
    print_step(6, "Configuring Prometheus monitoring...")
    
    if os.path.exists("monitoring/servicemonitor.yaml"):
        run_command("kubectl apply -f monitoring/servicemonitor.yaml", check=False)
        print_color("✅ ServiceMonitor configured", Colors.GREEN)
    else:
        print_color("⚠️  ServiceMonitor file not found, skipping...", Colors.YELLOW)

    # Step 7: Wait for pods
    print_step(7, "Waiting for application pods...")
    time.sleep(10)
    
    timeout = 120
    elapsed = 0
    while elapsed < timeout:
        try:
            result = subprocess.run(
                "kubectl get pods -l app=football-intro-app -o jsonpath='{.items[*].status.containerStatuses[*].ready}'",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "true" in result.stdout:
                print_color("✅ Application pods are ready", Colors.GREEN)
                break
        except:
            pass
        
        print_color(f"Waiting... ({elapsed} seconds)", Colors.YELLOW)
        time.sleep(5)
        elapsed += 5

    # Step 8: Show status
    print_step(8, "Deployment status...")
    print()
    print_color("Application Pods:", Colors.CYAN)
    run_command("kubectl get pods -l app=football-intro-app", capture_output=False)
    
    print()
    print_color("All Services:", Colors.CYAN)
    run_command("kubectl get svc --all-namespaces | grep -E 'football|prometheus|grafana'", 
                check=False, capture_output=False)

    # Final instructions
    print_header("✅ Full Stack Deployment Complete!")
    
    print_color("🎯 What's Deployed:", Colors.CYAN)
    print("  ✅ Cilium Network Plugin")
    print("  ✅ Prometheus Metrics Collection")
    print("  ✅ Grafana Dashboards")
    print("  ✅ Football Introduction App with Metrics")
    print()
    
    print_color("📊 Access Your Services:", Colors.YELLOW)
    print()
    print("Option A - Use quick access script:")
    print("  python access-monitoring.py")
    print()
    print("Option B - Manual port-forwards:")
    print("  # Application")
    print("  kubectl port-forward service/football-intro-app-service 8080:80")
    print()
    print("  # Prometheus")
    print("  kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090")
    print()
    print("  # Grafana (admin/admin)")
    print("  kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80")
    print()
    
    print_color("🔐 Apply Network Policies:", Colors.YELLOW)
    print("  python apply-network-policies.py")
    print("  python test-network-policies.py")
    print()
    
    print_color("📈 Import Grafana Dashboard:", Colors.YELLOW)
    print("  1. Access Grafana: http://localhost:3000")
    print("  2. Login: admin / admin")
    print("  3. Dashboards > Import")
    print("  4. Upload: monitoring/football-app-dashboard.json")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Deployment interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)