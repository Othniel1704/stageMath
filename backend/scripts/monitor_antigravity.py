#!/usr/bin/env python3
"""
Monitoring Script for Antigravity System
Tracks performance metrics and system health
"""

import os
import time
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json

class AntigravityMonitor:
    def __init__(self, base_url: str = "http://localhost:8000", log_file: str = "logs/antigravity_monitor.log"):
        self.base_url = base_url
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

    def check_server_health(self) -> Dict[str, Any]:
        """Check if the FastAPI server is running and responsive"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            return {"status": "down", "error": str(e)}

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "disk_free_gb": psutil.disk_usage('/').free / (1024**3)
        }

    def get_temp_dir_stats(self) -> Dict[str, Any]:
        """Get statistics about temporary files"""
        temp_dir = Path.home() / "Documents" / "stageMatch_temp"
        if not temp_dir.exists():
            return {"exists": False}

        total_size = 0
        file_count = 0
        old_files_count = 0
        cutoff = datetime.now() - timedelta(days=7)

        for file_path in temp_dir.rglob("*"):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size

                try:
                    file_date = datetime.fromtimestamp(file_path.stat().st_ctime)
                    if file_date < cutoff:
                        old_files_count += 1
                except OSError:
                    continue

        return {
            "exists": True,
            "path": str(temp_dir),
            "file_count": file_count,
            "old_files_count": old_files_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024**2)
        }

    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test key API endpoints (without authentication for monitoring)"""
        endpoints = [
            ("/", "root"),
            ("/docs", "docs"),
            ("/openapi.json", "openapi")
        ]

        results = {}
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time

                results[name] = {
                    "status": "ok" if response.status_code == 200 else "error",
                    "status_code": response.status_code,
                    "response_time": response_time
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive monitoring report"""
        self.log("Generating monitoring report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "server_health": self.check_server_health(),
            "system_metrics": self.get_system_metrics(),
            "temp_dir_stats": self.get_temp_dir_stats(),
            "api_endpoints": self.test_api_endpoints()
        }

        return report

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save monitoring report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/antigravity_report_{timestamp}.json"

        report_path = Path(filename)
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"Report saved to {report_path}")

    def check_alerts(self, report: Dict[str, Any]) -> List[str]:
        """Check for alert conditions"""
        alerts = []

        # Server health alerts
        if report["server_health"]["status"] != "healthy":
            alerts.append(f"🚨 SERVER DOWN: {report['server_health'].get('error', 'Unknown error')}")

        # System resource alerts
        metrics = report["system_metrics"]
        if metrics["memory_percent"] > 90:
            alerts.append(".1f"        if metrics["cpu_percent"] > 95:
            alerts.append(".1f"        if metrics["disk_usage_percent"] > 95:
            alerts.append(".1f"
        # Temp directory alerts
        temp_stats = report["temp_dir_stats"]
        if temp_stats.get("exists") and temp_stats.get("old_files_count", 0) > 100:
            alerts.append(f"🧹 HIGH TEMP FILES: {temp_stats['old_files_count']} old files need cleanup")

        return alerts

    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        self.log("Starting monitoring cycle...")

        # Generate report
        report = self.generate_report()

        # Check for alerts
        alerts = self.check_alerts(report)
        for alert in alerts:
            self.log(alert, "ALERT")

        # Save report
        self.save_report(report)

        # Log summary
        health = report["server_health"]["status"]
        cpu = report["system_metrics"]["cpu_percent"]
        memory = report["system_metrics"]["memory_percent"]

        self.log(f"Monitoring cycle complete - Server: {health}, CPU: {cpu:.1f}%, Memory: {memory:.1f}%")

        return report

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Antigravity system health")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--log-file", default="logs/antigravity_monitor.log", help="Log file path")
    parser.add_argument("--report-file", help="Save report to specific file")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default: 5 minutes)")

    args = parser.parse_args()

    monitor = AntigravityMonitor(args.url, args.log_file)

    if args.continuous:
        monitor.log(f"Starting continuous monitoring (interval: {args.interval}s)")
        try:
            while True:
                monitor.run_monitoring_cycle()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            monitor.log("Monitoring stopped by user")
    else:
        # Single monitoring cycle
        report = monitor.run_monitoring_cycle()

        if args.report_file:
            monitor.save_report(report, args.report_file)

        # Print summary to console
        print("\n📊 Monitoring Summary:")
        print(f"   🌐 Server: {report['server_health']['status']}")
        print(".1f"        print(".1f"        print(f"   💾 Disk: {report['system_metrics']['disk_usage_percent']:.1f}%")
        print(f"   📁 Temp files: {report['temp_dir_stats'].get('file_count', 0)}")

if __name__ == "__main__":
    main()