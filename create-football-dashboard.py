#!/usr/bin/env python3
"""
Create Football App Dashboard in Grafana
Automatically creates a custom dashboard with Football App metrics
Works with both NodePort and port-forwarded Grafana
"""

import json
import urllib.request
import base64
import sys

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

def create_dashboard():
    """Create Grafana dashboard via API"""
    
    dashboard = {
        "dashboard": {
            "title": "Football Introduction App Metrics",
            "tags": ["football-app", "nginx", "kubernetes"],
            "timezone": "browser",
            "schemaVersion": 16,
            "version": 0,
            "refresh": "10s",
            "panels": [
                {
                    "id": 1,
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "type": "graph",
                    "title": "HTTP Requests Rate",
                    "targets": [
                        {
                            "expr": "rate(nginx_http_requests_total{job='football-app'}[5m])",
                            "legendFormat": "{{pod_name}}",
                            "refId": "A"
                        }
                    ],
                    "yaxes": [
                        {"format": "reqps", "label": "Requests/sec"},
                        {"format": "short"}
                    ]
                },
                {
                    "id": 2,
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "type": "graph",
                    "title": "Active Connections",
                    "targets": [
                        {
                            "expr": "nginx_connections_active{job='football-app'}",
                            "legendFormat": "{{pod_name}}",
                            "refId": "A"
                        }
                    ],
                    "yaxes": [
                        {"format": "short", "label": "Connections"},
                        {"format": "short"}
                    ]
                },
                {
                    "id": 3,
                    "gridPos": {"h": 8, "w": 8, "x": 0, "y": 8},
                    "type": "stat",
                    "title": "Total Requests",
                    "targets": [
                        {
                            "expr": "sum(nginx_http_requests_total{job='football-app'})",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "graphMode": "area",
                        "colorMode": "value"
                    }
                },
                {
                    "id": 4,
                    "gridPos": {"h": 8, "w": 8, "x": 8, "y": 8},
                    "type": "stat",
                    "title": "Active Pods",
                    "targets": [
                        {
                            "expr": "count(up{job='football-app'} == 1)",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "graphMode": "none",
                        "colorMode": "value"
                    }
                },
                {
                    "id": 5,
                    "gridPos": {"h": 8, "w": 8, "x": 16, "y": 8},
                    "type": "stat",
                    "title": "Requests/sec (Current)",
                    "targets": [
                        {
                            "expr": "sum(rate(nginx_http_requests_total{job='football-app'}[1m]))",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "graphMode": "area",
                        "colorMode": "value"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "reqps"
                        }
                    }
                },
                {
                    "id": 6,
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                    "type": "table",
                    "title": "Pod Status",
                    "targets": [
                        {
                            "expr": "nginx_up{job='football-app'}",
                            "format": "table",
                            "instant": True,
                            "refId": "A"
                        }
                    ],
                    "transformations": [
                        {
                            "id": "organize",
                            "options": {
                                "excludeByName": {
                                    "Time": True,
                                    "__name__": True,
                                    "job": True
                                }
                            }
                        }
                    ]
                }
            ]
        },
        "overwrite": True,
        "message": "Created by Football App Monitoring Script"
    }
    
    return dashboard

def send_to_grafana(dashboard, grafana_url):
    """Send dashboard to Grafana API"""
    api_url = f"{grafana_url}/api/dashboards/db"
    username = "admin"
    password = "admin"
    
    try:
        # Create request
        data = json.dumps(dashboard).encode('utf-8')
        req = urllib.request.Request(
            api_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Add basic auth
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        
        # Send request
        response = urllib.request.urlopen(req, timeout=10)
        
        if response.status == 200:
            result = json.loads(response.read().decode())
            return True, result.get('url', '')
        
        return False, ""
        
    except urllib.error.HTTPError as e:
        if e.code == 409:
            return True, " (dashboard already exists - updated)"
        return False, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Connection Error: {e.reason}"
    except Exception as e:
        return False, str(e)

def check_grafana_accessible(url):
    """Check if Grafana is accessible"""
    try:
        response = urllib.request.urlopen(f"{url}/api/health", timeout=5)
        return response.status == 200
    except:
        return False

def main():
    print_header("📊 Creating Football App Dashboard in Grafana")
    
    # Try different Grafana URLs (port-forward first, then NodePort)
    grafana_urls = [
        ("http://localhost:3000", "Port-forwarded"),
        ("http://localhost:30030", "NodePort"),
    ]
    
    print_color("Detecting Grafana location...", Colors.BLUE)
    
    grafana_url = None
    connection_type = None
    
    for url, conn_type in grafana_urls:
        print_color(f"  Trying {url} ({conn_type})...", Colors.YELLOW)
        if check_grafana_accessible(url):
            print_color(f"  ✅ Found Grafana at {url}", Colors.GREEN)
            grafana_url = url
            connection_type = conn_type
            break
        else:
            print_color(f"  ❌ Not accessible", Colors.RED)
    
    if not grafana_url:
        print()
        print_color("❌ Grafana is not accessible!", Colors.RED)
        print()
        print_color("Please make sure Grafana is running:", Colors.YELLOW)
        print("  1. Check if deployed: kubectl get pods")
        print("  2. Start port-forward: python start-port-forwards.py")
        print("  3. Or manually: kubectl port-forward service/grafana 3000:3000")
        print()
        print_color("Then try this script again", Colors.CYAN)
        sys.exit(1)
    
    print()
    print_color(f"Using Grafana at: {grafana_url} ({connection_type})", Colors.CYAN)
    print()
    
    print_color("Creating dashboard configuration...", Colors.BLUE)
    dashboard = create_dashboard()
    print_color("✅ Dashboard configuration created", Colors.GREEN)
    print()
    
    print_color("Sending to Grafana...", Colors.BLUE)
    success, url_or_error = send_to_grafana(dashboard, grafana_url)
    
    if success:
        print_color("✅ Dashboard created successfully!", Colors.GREEN)
        print()
        print_color("Access your dashboard:", Colors.CYAN)
        if url_or_error and url_or_error.startswith('/'):
            print(f"  {grafana_url}{url_or_error}")
        else:
            print(f"  {grafana_url}/dashboards")
            if url_or_error:
                print_color(f"  Note: {url_or_error}", Colors.YELLOW)
        print()
        print_color("Or navigate manually:", Colors.YELLOW)
        print(f"  1. Open: {grafana_url}")
        print("  2. Go to: Dashboards → Browse")
        print("  3. Find: 'Football Introduction App Metrics'")
        print()
        print_color("Dashboard shows:", Colors.CYAN)
        print("  • HTTP Request Rate")
        print("  • Active Connections")
        print("  • Total Requests")
        print("  • Active Pods")
        print("  • Current Request Rate")
        print("  • Pod Status Table")
        print()
        print_color("Generate traffic to see metrics:", Colors.YELLOW)
        print("  # Generate 100 requests")
        if connection_type == "Port-forwarded":
            print("  for i in {1..100}; do curl -s http://localhost:8080 > /dev/null; done")
        else:
            print("  for i in {1..100}; do curl -s http://localhost:8080 > /dev/null; done")
        print()
    else:
        print_color(f"❌ Failed to create dashboard: {url_or_error}", Colors.RED)
        print()
        print_color("Manual steps:", Colors.YELLOW)
        print(f"1. Open Grafana: {grafana_url}")
        print("2. Login: admin / admin")
        print("3. Check Prometheus data source exists:")
        print("   - Go to: Connections → Data Sources")
        print("   - Should see: Prometheus")
        print("4. Create dashboard manually with these queries:")
        print()
        print_color("Useful queries:", Colors.CYAN)
        print("  rate(nginx_http_requests_total{job='football-app'}[5m])")
        print("  nginx_connections_active{job='football-app'}")
        print("  sum(nginx_http_requests_total{job='football-app'})")
        print()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("\n⚠️  Cancelled", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print()
        print_color(f"❌ Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
