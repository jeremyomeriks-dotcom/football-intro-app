#!/usr/bin/env python3
"""
Create Football App Dashboard in Grafana
Automatically creates a custom dashboard with Football App metrics
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

def send_to_grafana(dashboard):
    """Send dashboard to Grafana API"""
    grafana_url = "http://localhost:30030/api/dashboards/db"
    username = "admin"
    password = "admin"
    
    try:
        # Create request
        data = json.dumps(dashboard).encode('utf-8')
        req = urllib.request.Request(
            grafana_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Add basic auth
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        
        # Send request
        response = urllib.request.urlopen(req)
        
        if response.status == 200:
            result = json.loads(response.read().decode())
            return True, result.get('url', '')
        
        return False, ""
        
    except Exception as e:
        return False, str(e)

def main():
    print_header("📊 Creating Football App Dashboard in Grafana")
    
    print_color("Creating dashboard configuration...", Colors.BLUE)
    dashboard = create_dashboard()
    print_color("✅ Dashboard configuration created", Colors.GREEN)
    print()
    
    print_color("Sending to Grafana...", Colors.BLUE)
    success, url_or_error = send_to_grafana(dashboard)
    
    if success:
        print_color("✅ Dashboard created successfully!", Colors.GREEN)
        print()
        print_color("Access your dashboard:", Colors.CYAN)
        print(f"  http://localhost:30030{url_or_error}")
        print()
        print_color("Or navigate manually:", Colors.YELLOW)
        print("  1. Open: http://localhost:30030")
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
    else:
        print_color(f"❌ Failed to create dashboard: {url_or_error}", Colors.RED)
        print()
        print_color("Manual steps:", Colors.YELLOW)
        print("1. Make sure Grafana is running: http://localhost:30030")
        print("2. Check Prometheus data source is configured")
        print("3. Create dashboard manually with these queries:")
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