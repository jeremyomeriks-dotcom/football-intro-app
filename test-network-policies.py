#!/usr/bin/env python3
"""
Test Network Policies - Python Version
Cross-platform script to test Cilium network policy enforcement
"""

import subprocess
import sys

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

def print_test_header(test_num, description):
    """Print test section header"""
    print()
    print_color("=" * 60, Colors.BLUE)
    print_color(f"Test {test_num}: {description}", Colors.BLUE)
    print_color("=" * 60, Colors.BLUE)

def run_command(command, check=False, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            capture_output=capture_output
        )
        if capture_output and result.stdout:
            print(result.stdout.strip())
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr.strip())
        return False

def get_app_pod():
    """Get the football app pod name"""
    try:
        result = subprocess.run(
            "kubectl get pods -l app=football-intro-app -o jsonpath='{.items[0].metadata.name}'",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None

def test_allowed_connection():
    """Test 1: Test connection from allowed pod"""
    print_test_header(1, "Create allowed test pod and test connection")
    
    cmd = """kubectl run test-allowed --image=nicolaka/netshoot --restart=Never --rm -i -- \
/bin/bash -c "curl -s -o /dev/null -w '%{http_code}' http://football-intro-app-service --connect-timeout 5 || echo 'Connection failed'" """
    
    print_color("Testing connection from allowed pod...", Colors.YELLOW)
    run_command(cmd, check=False, capture_output=False)

def test_blocked_connection():
    """Test 2: Test connection from blocked pod"""
    print_test_header(2, "Create blocked test pod (with label role=blocked)")
    
    cmd = """kubectl run test-blocked --image=nicolaka/netshoot --labels="role=blocked" --restart=Never --rm -i -- \
/bin/bash -c "curl -s -o /dev/null -w '%{http_code}' http://football-intro-app-service --connect-timeout 5 || echo 'Connection blocked'" """
    
    print_color("Testing connection from blocked pod...", Colors.YELLOW)
    run_command(cmd, check=False, capture_output=False)

def show_network_policies():
    """Test 3: Show active network policies"""
    print_test_header(3, "Active Network Policies")
    run_command("kubectl get networkpolicies", check=False, capture_output=False)

def show_cilium_policies():
    """Test 4: Show Cilium network policies"""
    print_test_header(4, "Cilium Network Policies")
    run_command("kubectl get ciliumnetworkpolicies", check=False, capture_output=False)

def show_cilium_endpoints():
    """Test 5: Check Cilium endpoints"""
    print_test_header(5, "Cilium Endpoints")
    run_command("kubectl get ciliumendpoints -n default", check=False, capture_output=False)

def test_cross_namespace():
    """Test 6: Test connectivity from another namespace"""
    print_test_header(6, "Connectivity from another namespace (should fail)")
    
    # Create test namespace
    print_color("Creating test namespace...", Colors.YELLOW)
    run_command("kubectl create namespace test-ns --dry-run=client -o yaml | kubectl apply -f -", 
                check=False, capture_output=True)
    
    # Try to access from different namespace
    cmd = """kubectl run test-other-ns --image=nicolaka/netshoot --namespace=test-ns --restart=Never --rm -i -- \
/bin/bash -c "curl -s -o /dev/null -w '%{http_code}' http://football-intro-app-service.default.svc.cluster.local --connect-timeout 5 || echo 'Connection failed'" """
    
    print_color("Testing cross-namespace connection...", Colors.YELLOW)
    run_command(cmd, check=False, capture_output=False)
    
    # Cleanup test namespace
    print_color("Cleaning up test namespace...", Colors.YELLOW)
    run_command("kubectl delete namespace test-ns --ignore-not-found=true", 
                check=False, capture_output=True)

def print_summary():
    """Print test summary"""
    print_header("✅ Network Policy Tests Complete!")
    
    print_color("Summary:", Colors.YELLOW)
    print("- Test 1: Allowed pod should succeed (200 OK)")
    print("- Test 2: Blocked pod should fail (timeout/connection refused)")
    print("- Test 6: Cross-namespace should be controlled by policy")
    print()
    
    print_color("View policy effects with:", Colors.CYAN)
    print("  kubectl describe networkpolicy")
    print("  kubectl get ciliumnetworkpolicies")
    print()

def main():
    print_header("🧪 Testing Cilium Network Policies")

    # Check if football app pod exists
    app_pod = get_app_pod()
    if not app_pod:
        print_color("❌ Football app pod not found. Deploy the app first.", Colors.RED)
        print_color("Run: python deploy-with-cilium.py", Colors.YELLOW)
        sys.exit(1)
    
    print_color(f"✅ Found app pod: {app_pod}", Colors.GREEN)
    print()

    # Run tests
    try:
        test_allowed_connection()
        test_blocked_connection()
        show_network_policies()
        show_cilium_policies()
        show_cilium_endpoints()
        test_cross_namespace()
        
        # Print summary
        print_summary()
        
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Tests interrupted by user", Colors.YELLOW)
        # Cleanup any remaining test pods
        run_command("kubectl delete pod test-allowed --ignore-not-found=true", check=False, capture_output=True)
        run_command("kubectl delete pod test-blocked --ignore-not-found=true", check=False, capture_output=True)
        run_command("kubectl delete namespace test-ns --ignore-not-found=true", check=False, capture_output=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        
        # Cleanup
        print_color("\nCleaning up test resources...", Colors.YELLOW)
        run_command("kubectl delete pod test-allowed --ignore-not-found=true", check=False, capture_output=True)
        run_command("kubectl delete pod test-blocked --ignore-not-found=true", check=False, capture_output=True)
        run_command("kubectl delete namespace test-ns --ignore-not-found=true", check=False, capture_output=True)
        
        sys.exit(1)