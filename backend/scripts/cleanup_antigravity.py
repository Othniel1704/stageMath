#!/usr/bin/env python3
"""
Cleanup Script for Antigravity System
Removes temporary files and old CVs to free up disk space
"""

import os
import glob
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

class AntigravityCleaner:
    def __init__(self, temp_dir: str = None, max_age_days: int = 7):
        self.temp_dir = temp_dir or os.path.join(os.path.expanduser("~"), "Documents", "stageMatch_temp")
        self.max_age_days = max_age_days
        self.cutoff_date = datetime.now() - timedelta(days=max_age_days)

    def find_temp_files(self) -> List[str]:
        """Find all temporary files in the temp directory"""
        if not os.path.exists(self.temp_dir):
            return []

        patterns = [
            os.path.join(self.temp_dir, "stageMatch_*.pdf"),
            os.path.join(self.temp_dir, "stageMatch_*.txt"),
            os.path.join(self.temp_dir, "*.tmp"),
        ]

        temp_files = []
        for pattern in patterns:
            temp_files.extend(glob.glob(pattern))

        return temp_files

    def find_old_files(self, files: List[str]) -> List[Tuple[str, datetime]]:
        """Filter files older than cutoff date"""
        old_files = []
        for file_path in files:
            try:
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_date < self.cutoff_date:
                    old_files.append((file_path, file_date))
            except OSError:
                # File might have been deleted or inaccessible
                continue

        return old_files

    def calculate_space_saved(self, files: List[str]) -> int:
        """Calculate total size of files to be deleted"""
        total_size = 0
        for file_path in files:
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                continue
        return total_size

    def cleanup_temp_files(self, dry_run: bool = False) -> Tuple[int, int]:
        """
        Clean up temporary files
        Returns: (files_deleted, space_saved_bytes)
        """
        temp_files = self.find_temp_files()
        old_files = self.find_old_files(temp_files)
        files_to_delete = [f[0] for f in old_files]

        if not files_to_delete:
            print("🧹 No old temporary files to clean up")
            return 0, 0

        space_saved = self.calculate_space_saved(files_to_delete)

        if dry_run:
            print(f"🧹 DRY RUN: Would delete {len(files_to_delete)} files")
            print(f"   💾 Space that would be saved: {self.format_bytes(space_saved)}")
            for file_path, file_date in old_files:
                print(f"   📄 {os.path.basename(file_path)} (created: {file_date.strftime('%Y-%m-%d %H:%M')})")
            return 0, 0

        # Perform actual cleanup
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"🗑️  Deleted: {os.path.basename(file_path)}")
            except OSError as e:
                print(f"❌ Failed to delete {file_path}: {e}")

        print(f"🧹 Cleanup complete: {deleted_count} files deleted")
        print(f"   💾 Space saved: {self.format_bytes(space_saved)}")

        return deleted_count, space_saved

    def cleanup_empty_dirs(self, dry_run: bool = False) -> int:
        """Remove empty directories in temp folder"""
        if not os.path.exists(self.temp_dir):
            return 0

        empty_dirs = []
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            if not dirs and not files:
                empty_dirs.append(root)

        if not empty_dirs:
            print("📁 No empty directories to clean up")
            return 0

        if dry_run:
            print(f"📁 DRY RUN: Would remove {len(empty_dirs)} empty directories")
            for dir_path in empty_dirs:
                print(f"   📂 {dir_path}")
            return 0

        # Remove empty directories
        removed_count = 0
        for dir_path in empty_dirs:
            try:
                os.rmdir(dir_path)
                removed_count += 1
                print(f"🗂️  Removed empty dir: {dir_path}")
            except OSError as e:
                print(f"❌ Failed to remove directory {dir_path}: {e}")

        print(f"📁 Empty directories cleanup: {removed_count} removed")
        return removed_count

    def get_temp_dir_stats(self) -> Dict[str, any]:
        """Get statistics about the temp directory"""
        if not os.path.exists(self.temp_dir):
            return {"exists": False}

        temp_files = self.find_temp_files()
        total_size = self.calculate_space_saved(temp_files)
        old_files = self.find_old_files(temp_files)

        return {
            "exists": True,
            "path": self.temp_dir,
            "total_files": len(temp_files),
            "old_files": len(old_files),
            "total_size_bytes": total_size,
            "total_size_human": self.format_bytes(total_size),
            "max_age_days": self.max_age_days
        }

    @staticmethod
    def format_bytes(bytes_size: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return ".1f"
            bytes_size /= 1024.0
        return ".1f"

    def run_full_cleanup(self, dry_run: bool = False):
        """Run complete cleanup process"""
        print("🧹 Starting Antigravity Cleanup Process")
        print("=" * 50)

        # Show current stats
        stats = self.get_temp_dir_stats()
        if not stats["exists"]:
            print(f"📁 Temp directory doesn't exist: {self.temp_dir}")
            return

        print("📊 Current Temp Directory Stats:")
        print(f"   📂 Path: {stats['path']}")
        print(f"   📄 Total files: {stats['total_files']}")
        print(f"   📅 Old files (> {stats['max_age_days']} days): {stats['old_files']}")
        print(f"   💾 Total size: {stats['total_size_human']}")
        print()

        # Cleanup temp files
        files_deleted, space_saved = self.cleanup_temp_files(dry_run)
        print()

        # Cleanup empty directories
        dirs_removed = self.cleanup_empty_dirs(dry_run)
        print()

        if not dry_run:
            print("🎉 Cleanup Process Complete!")
            print(f"   🗑️  Files deleted: {files_deleted}")
            print(f"   📁 Directories removed: {dirs_removed}")
            print(f"   💾 Space saved: {self.format_bytes(space_saved)}")
        else:
            print("🔍 Dry run complete - no files were actually deleted")

        print("=" * 50)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup Antigravity temporary files")
    parser.add_argument("--temp-dir", help="Temporary directory path")
    parser.add_argument("--max-age", type=int, default=7, help="Maximum age in days (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--stats-only", action="store_true", help="Only show statistics, don't clean up")

    args = parser.parse_args()

    cleaner = AntigravityCleaner(
        temp_dir=args.temp_dir,
        max_age_days=args.max_age
    )

    if args.stats_only:
        stats = cleaner.get_temp_dir_stats()
        print("📊 Temp Directory Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        cleaner.run_full_cleanup(dry_run=args.dry_run)


if __name__ == "__main__":
    main()