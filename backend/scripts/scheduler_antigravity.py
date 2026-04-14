#!/usr/bin/env python3
"""
Scheduled Tasks for Antigravity System
Automates cleanup and monitoring tasks
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import sys

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.monitor_antigravity import AntigravityMonitor
from scripts.cleanup_antigravity import AntigravityCleaner
from services.job_fetcher import fetch_remotive_jobs, fetch_jsearch_jobs

class AntigravityScheduler:
    def __init__(self, log_file: str = "logs/antigravity_scheduler.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.monitor = AntigravityMonitor()
        self.cleaner = AntigravityCleaner()

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

        if level == "INFO":
            logging.info(message)
        elif level == "WARNING":
            logging.warning(message)
        elif level == "ERROR":
            logging.error(message)

    def run_cleanup(self):
        """Run the cleanup task"""
        self.log("🧹 Starting scheduled cleanup...")
        try:
            files_deleted, space_saved = self.cleaner.cleanup_temp_files()
            dirs_removed = self.cleaner.cleanup_empty_dirs()

            self.log(f"✅ Cleanup complete: {files_deleted} files, {dirs_removed} dirs removed")
        except Exception as e:
            self.log(f"❌ Cleanup failed: {e}", "ERROR")

    def run_scraping(self):
        """Run the automated job sourcing task"""
        self.log("🚀 Starting scheduled job sourcing...")
        try:
            # Source 1: Remotive
            remotive_res = fetch_remotive_jobs(limit=50)
            self.log(f"  - Remotive: {remotive_res.get('inserted', 0)} jobs added")

            # Source 2: JSearch with common queries
            queries = ["stage informatique france", "alternance développeur", "développeur web junior"]
            jsearch_total = 0
            for q in queries:
                res = fetch_jsearch_jobs(query=q, limit=10)
                jsearch_total += res.get('inserted', 0)
            self.log(f"  - JSearch: {jsearch_total} jobs added")

            self.log("✅ Scraping complete")
        except Exception as e:
            self.log(f"❌ Scraping failed: {e}", "ERROR")

    def run_monitoring(self):
        """Run the monitoring task"""
        self.log("📊 Starting scheduled monitoring...")
        try:
            report = self.monitor.run_monitoring_cycle()

            # Check for critical alerts
            alerts = self.monitor.check_alerts(report)
            if alerts:
                for alert in alerts:
                    self.log(alert, "WARNING")
            else:
                self.log("✅ System health check passed")

        except Exception as e:
            self.log(f"❌ Monitoring failed: {e}", "ERROR")

    def run_health_check(self):
        """Quick health check"""
        self.log("🏥 Running health check...")
        try:
            health = self.monitor.check_server_health()
            if health["status"] == "healthy":
                self.log("✅ Server is healthy")
            else:
                self.log(f"⚠️  Server health issue: {health}", "WARNING")
        except Exception as e:
            self.log(f"❌ Health check failed: {e}", "ERROR")

    def backup_logs(self):
        """Backup log files"""
        self.log("💾 Backing up log files...")
        try:
            # Create backup directory
            backup_dir = Path("logs/backup")
            backup_dir.mkdir(exist_ok=True)

            # Backup current logs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for log_file in ["antigravity_monitor.log", "antigravity_scheduler.log"]:
                log_path = Path("logs") / log_file
                if log_path.exists():
                    backup_path = backup_dir / f"{log_file}.{timestamp}"
                    log_path.copy(backup_path)
                    self.log(f"📋 Backed up {log_file}")

            # Clean old backups (keep last 7 days)
            self.cleanup_old_backups(backup_dir)

        except Exception as e:
            self.log(f"❌ Backup failed: {e}", "ERROR")

    def cleanup_old_backups(self, backup_dir: Path, max_age_days: int = 7):
        """Clean up old backup files"""
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)

        old_backups = []
        for backup_file in backup_dir.glob("*.log.*"):
            if backup_file.stat().st_mtime < cutoff:
                old_backups.append(backup_file)

        for old_backup in old_backups:
            old_backup.unlink()
            self.log(f"🗑️  Removed old backup: {old_backup.name}")

        if old_backups:
            self.log(f"🧹 Cleaned up {len(old_backups)} old backup files")

    def setup_schedule(self):
        """Setup the scheduled tasks"""
        self.log("📅 Setting up scheduled tasks...")

        # Health checks every 5 minutes
        schedule.every(5).minutes.do(self.run_health_check)

        # Full monitoring every hour
        schedule.every().hour.do(self.run_monitoring)

        # Cleanup every day at 2 AM
        schedule.every().day.at("02:00").do(self.run_cleanup)

        # Scraping every 6 hours
        schedule.every(6).hours.do(self.run_scraping)

        # Log backup every week
        schedule.every().week.do(self.backup_logs)

        self.log("✅ Scheduled tasks configured:")
        self.log("   🏥 Health check: Every 5 minutes")
        self.log("   📊 Full monitoring: Every hour")
        self.log("   🚀 Job Sourcing: Every 6 hours")
        self.log("   🧹 Cleanup: Daily at 2:00 AM")
        self.log("   💾 Log backup: Weekly")

    def run_scheduler(self):
        """Run the scheduler loop"""
        self.log("🚀 Starting Antigravity Scheduler")
        self.log("=" * 50)

        # Setup tasks
        self.setup_schedule()

        # Run initial tasks
        self.log("🔄 Running initial tasks...")
        self.run_health_check()
        self.run_monitoring()

        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.log("🛑 Scheduler stopped by user")
        except Exception as e:
            self.log(f"❌ Scheduler error: {e}", "ERROR")
            raise

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run scheduled tasks for Antigravity system")
    parser.add_argument("--log-file", default="logs/antigravity_scheduler.log", help="Scheduler log file")
    parser.add_argument("--run-once", action="store_true", help="Run tasks once and exit")

    args = parser.parse_args()

    scheduler = AntigravityScheduler(args.log_file)

    if args.run_once:
        # Run all tasks once
        scheduler.log("🔄 Running all tasks once...")
        scheduler.run_health_check()
        scheduler.run_monitoring()
        scheduler.run_cleanup()
        scheduler.backup_logs()
        scheduler.log("✅ All tasks completed")
    else:
        # Run scheduler continuously
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()