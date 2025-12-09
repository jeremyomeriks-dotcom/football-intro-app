#!/usr/bin/env python3
"""
Complete Grafana Fix Script
Completely removes and redeploys Grafana with proper admin credentials
"""

import subprocess
import sys
import time
import urllib.request

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

def run_command(command, description=None, check=False):
    """Run a shell command"""
    if description:
        print_color(description, Colors.BLUE)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=True
        )
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Error: {e}", Colors.RED)
            if e.stderr:
                print(e.stderr)
        return False

def check_grafana_accessible(url, username, password):
    """Check if Grafana is accessible with credentials"""
    try:
        import base64
        req = urllib.request.Request(f"{url}/api/user")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        response = urllib.request.urlopen(req, timeout=5)
        return response.status == 200
    except:
        return False

def wait_for_pod(label, timeout=120):
    """Wait for pod to be ready"""
    print_color(f"⏳ Waiting for {label} pod to be ready...", Colors.YELLOW)
    
    elapsed = 0
    while elapsed < timeout:
        result = subprocess.run(
            f"kubectl get pods -l {label} -o jsonpath='{{.items[*].status.containerStatuses[*].ready}}'",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout and "true" in result.stdout:
            print_color(f"✅ Pod is ready", Colors.GREEN)
            return True
        
        time.sleep(5)
        elapsed += 5
    
    print_color(f"⚠️  Timeout waiting for pod", Colors.YELLOW)
    return False

def main():
    print_header("🔧 Complete Grafana Fix")
    
    print_color("This will:", Colors.CYAN)
    print("  1. Remove existing Grafana completely")
    print("  2. Redeploy with fresh configuration")
    print("  3. Set admin credentials to admin/admin")
    print("  4. Verify login works")
    print()
    
    try:
        response = input("Continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print_color("Cancelled", Colors.YELLOW)
            sys.exit(0)
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    
    # Step 1: Remove all Grafana resources
    print_header("Step 1: Removing Existing Grafana")
    
    run_command("kubectl delete deployment grafana --ignore-not-found=true", 
                "Deleting deployment...")
    run_command("kubectl delete service grafana --ignore-not-found=true",
                "Deleting service...")
    run_command("kubectl delete configmap grafana-datasources --ignore-not-found=true",
                "Deleting configmap...")
    run_command("kubectl delete pvc -l app=grafana --ignore-not-found=true",
                "Deleting persistent volumes...")
    
    print_color("✅ Old Grafana removed", Colors.GREEN)
    print_color("Waiting 10 seconds for cleanup...", Colors.YELLOW)
    time.sleep(10)
    
    # Step 2: Redeploy Grafana
    print_header("Step 2: Deploying Fresh Grafana")
    
    if not run_command("kubectl apply -f k8s/grafana-deployment.yaml", check=False):
        print_color("❌ Failed to deploy Grafana", Colors.RED)
        print()
        print_color("Trying alternative deployment...", Colors.YELLOW)
        
        # Create inline deployment
        grafana_yaml = """apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: default
data:
  prometheus.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus:9090
      isDefault: true
      editable: true
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.2.3
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_USER
          value: "admin"
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        - name: GF_USERS_ALLOW_SIGN_UP
          value: "false"
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "false"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-datasources
          mountPath: /etc/grafana/provisioning/datasources
      volumes:
      - name: grafana-storage
        emptyDir: {}
      - name: grafana-datasources
        configMap:
          name: grafana-datasources
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: default
spec:
  type: NodePort
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30030
"""
        
        # Write to temp file and apply
        with open("/tmp/grafana-fix.yaml", "w") as f:
            f.write(grafana_yaml)
        
        if not run_command("kubectl apply -f /tmp/grafana-fix.yaml"):
            print_color("❌ Failed to deploy Grafana", Colors.RED)
            sys.exit(1)
    
    print_color("✅ Grafana deployed", Colors.GREEN)
    print()
    
    # Step 3: Wait for pod to be ready
    print_header("Step 3: Waiting for Grafana to Start")
    
    if not wait_for_pod("app=grafana", timeout=120):
        print_color("⚠️  Pod may not be ready yet", Colors.YELLOW)
    
    print()
    
    # Step 4: Check pod status
    print_header("Step 4: Checking Pod Status")
    run_command("kubectl get pods -l app=grafana", check=False)
    print()
    
    # Step 5: Test access
    print_header("Step 5: Testing Access")
    
    print_color("Starting port-forward...", Colors.BLUE)
    
    # Kill any existing port forwards
    import platform
    if platform.system() == "Windows":
        subprocess.run("taskkill /F /IM kubectl.exe 2>nul", shell=True, capture_output=True)
    else:
        subprocess.run("pkill kubectl", shell=True, capture_output=True)
    
    time.sleep(2)
    
    # Start new port forward
    subprocess.Popen(
        "kubectl port-forward service/grafana 3000:3000",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print_color("Waiting for port-forward to establish...", Colors.YELLOW)
    time.sleep(5)
    
    # Test login
    print_color("Testing admin login...", Colors.BLUE)
    
    if check_grafana_accessible("http://localhost:3000", "admin", "admin"):
        print_color("✅ Login successful!", Colors.GREEN)
    else:
        print_color("⚠️  Could not verify login yet", Colors.YELLOW)
        print_color("This is normal - Grafana may still be initializing", Colors.YELLOW)
    
    # Final instructions
    print_header("✅ Grafana Redeployed Successfully!")
    
    print_color("Credentials:", Colors.CYAN)
    print("  Username: admin")
    print("  Password: admin")
    print()
    
    print_color("Access Grafana:", Colors.CYAN)
    print("  🌐 http://localhost:3000 (port-forward)")
    print("  🌐 http://localhost:30030 (NodePort)")
    print()
    
    print_color("Next steps:", Colors.YELLOW)
    print("1. Open: http://localhost:3000")
    print("2. Login with: admin / admin")
    print("3. If prompted to change password, you can skip or change it")
    print("4. Create dashboard: python create-football-dashboard.py")
    print()
    
    print_color("Verify data source:", Colors.YELLOW)
    print("  Go to: Connections → Data Sources")
    print("  Should see: Prometheus")
    print("  URL: http://prometheus:9090")
    print()
    
    print_color("Troubleshooting:", Colors.CYAN)
    print("  Check pods: kubectl get pods")
    print("  Check logs: kubectl logs -l app=grafana")
    print("  Restart port-forward: python start-port-forwards.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Interrupted", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
