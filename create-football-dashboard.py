[file name]: create-football-dashboard.py
[file content begin]
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
            ],
            "links": [
                {
                    "icon": "external link",
                    "tags": [],
                    "targetBlank": True,
                    "title": "App Metrics Dashboard",
                    "tooltip": "View simple metrics dashboard in the app",
                    "type": "link",
                    "url": "http://localhost:8080/metrics-dashboard"
                },
                {
                    "icon": "external link",
                    "tags": [],
                    "targetBlank": True,
                    "title": "Raw Metrics",
                    "tooltip": "View raw Prometheus metrics",
                    "type": "link",
                    "url": "http://localhost:8080/app-metrics"
                },
                {
                    "icon": "external link",
                    "tags": [],
                    "targetBlank": True,
                    "title": "Main Application",
                    "tooltip": "Return to main football application",
                    "type": "link",
                    "url": "http://localhost:8080"
                }
            ]
        },
        "overwrite": True,
        "message": "Created by Football App Monitoring Script"
    }
    
    return dashboard

# ... rest of the file remains the same ...

    print_color("Dashboard shows:", Colors.CYAN)
    print("  • HTTP Request Rate")
    print("  • Active Connections")
    print("  • Total Requests")
    print("  • Active Pods")
    print("  • Current Request Rate")
    print("  • Pod Status Table")
    print()
    print_color("Access all monitoring tools:", Colors.CYAN)
    print("  🏈 Football App:        http://localhost:8080")
    print("  📊 App Metrics Page:    http://localhost:8080/metrics-dashboard")
    print("  📡 Raw Metrics:         http://localhost:8080/app-metrics")
    print("  📈 Prometheus:          http://localhost:9090")
    print("  📋 Grafana:             http://localhost:3000 (admin/admin)")
    print()
    print_color("Generate traffic to see metrics:", Colors.YELLOW)
    print("  # Generate 100 requests")
    print("  for i in {1..100}; do curl -s http://localhost:8080 > /dev/null; done")
    print()
    print_color("View metrics directly in the app:", Colors.YELLOW)
    print("  1. Open: http://localhost:8080/metrics-dashboard")
    print("  2. See real-time metrics from Prometheus")
    print("  3. Auto-refreshes every 10 seconds")
    print()

# ... rest of the file remains the same ...
[file content end]
