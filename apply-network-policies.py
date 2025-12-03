#!/usr/bin/env python3
"""
Apply Network Policies Script - Python Version
Cross-platform script to apply and manage Kubernetes network policies
"""

import subprocess
import sys
import os
from pathlib import Path

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

def run_command(command, check=True, capture_output=True):
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
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_color(f"❌ Error: {e}", Colors.RED)
            if e.stderr:
                print(e.stderr)
        return False

def check_policies_directory():
    """Check if network-policies directory exists"""
    if not os.path.exists("network-policies"):
        print_color("⚠️  network-policies directory not found!", Colors.RED)
        print_color("Creating network-policies directory...", Colors.YELLOW)
        os.makedirs("network-policies")
        print_color("Please create policy files in the network-policies directory", Colors.YELLOW)
        return False
    return True

def list_policies():
    """List available policy files"""
    policy_dir = Path("network-policies")
    yaml_files = list(policy_dir.glob("*.yaml"))
    
    if not yaml_files:
        print_color("⚠️  No policy files found in network-policies/", Colors.YELLOW)
        return []
    
    print_color("Available policies:", Colors.BLUE)
    for policy_file in sorted(yaml_files):
        print_color(f"  - {policy_file.name}", Colors.YELLOW)
    return yaml_files

def display_menu():
    """Display the policy application menu"""
    print()
    print_color("Options:", Colors.CYAN)
    print("  1. Apply all policies")
    print("  2. Apply deny-all first (testing)")
    print("  3. Apply allow policies only")
    print("  4. Apply Cilium L7 policies")
    print("  5. Remove all policies")
    print()

def apply_all_policies():
    """Apply all network policies"""
    print()
    print_color("Applying all network policies...", Colors.BLUE)
    if run_command("kubectl apply -f network-policies/", capture_output=False):
        print_color("✅ All policies applied", Colors.GREEN)
    else:
        print_color("❌ Failed to apply policies", Colors.RED)

def apply_deny_all():
    """Apply deny-all policy"""
    print()
    print_color("Applying deny-all policy...", Colors.BLUE)
    if run_command("kubectl apply -f network-policies/01-deny-all.yaml", capture_output=False):
        print_color("✅ Deny-all policy applied", Colors.GREEN)
        print_color("⚠️  All traffic is now blocked!", Colors.YELLOW)
        print_color("Apply allow policies to enable specific traffic", Colors.YELLOW)
    else:
        print_color("❌ Failed to apply deny-all policy", Colors.RED)

def apply_allow_policies():
    """Apply allow policies"""
    print()
    print_color("Applying allow policies...", Colors.BLUE)
    if run_command("kubectl apply -f network-policies/02-allow-football-app.yaml", capture_output=False):
        print_color("✅ Allow policies applied", Colors.GREEN)
    else:
        print_color("❌ Failed to apply allow policies", Colors.RED)

def apply_cilium_l7_policies():
    """Apply Cilium L7 policies"""
    print()
    print_color("Applying Cilium L7 policies...", Colors.BLUE)
    if run_command("kubectl apply -f network-policies/03-cilium-l7-policy.yaml", capture_output=False):
        print_color("✅ Cilium L7 policies applied", Colors.GREEN)
    else:
        print_color("❌ Failed to apply Cilium L7 policies", Colors.RED)

def remove_all_policies():
    """Remove all network policies"""
    print()
    print_color("Removing all network policies...", Colors.BLUE)
    run_command("kubectl delete networkpolicies --all", check=False, capture_output=False)
    run_command("kubectl delete ciliumnetworkpolicies --all", check=False, capture_output=False)
    print_color("✅ All policies removed", Colors.GREEN)

def show_current_policies():
    """Show currently applied policies"""
    print()
    print_color("Current network policies:", Colors.CYAN)
    run_command("kubectl get networkpolicies", check=False, capture_output=False)
    print()
    run_command("kubectl get ciliumnetworkpolicies", check=False, capture_output=False)

def main():
    print_header("📋 Applying Network Policies")

    # Check if network-policies directory exists
    if not check_policies_directory():
        sys.exit(1)

    # List available policies
    policies = list_policies()
    if not policies:
        sys.exit(1)

    # Display menu
    display_menu()

    # Get user choice
    try:
        choice = input("Enter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Operation cancelled", Colors.YELLOW)
        sys.exit(0)

    # Process choice
    if choice == "1":
        apply_all_policies()
    elif choice == "2":
        apply_deny_all()
    elif choice == "3":
        apply_allow_policies()
    elif choice == "4":
        apply_cilium_l7_policies()
    elif choice == "5":
        remove_all_policies()
    else:
        print_color("Invalid choice", Colors.RED)
        sys.exit(1)

    # Show current policies
    show_current_policies()

    # Next steps
    print()
    print_color("Test policies with: python test-network-policies.py", Colors.YELLOW)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Operation cancelled by user", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print()
        print_color(f"❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)