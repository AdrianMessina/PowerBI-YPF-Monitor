"""
Migration Script: Convert YPF BI Monitor apps to cloud-ready version
Automatically updates apps to use pbip_loader instead of text_input

Usage:
    python scripts/migrate_to_cloud.py [--dry-run] [--app APP_NAME]

Options:
    --dry-run       Show what would be changed without modifying files
    --app APP_NAME  Only migrate specific app (e.g., powerbi_analyzer)

Examples:
    python scripts/migrate_to_cloud.py --dry-run          # Preview all changes
    python scripts/migrate_to_cloud.py                     # Migrate all apps
    python scripts/migrate_to_cloud.py --app dax_optimizer # Migrate only DAX Optimizer
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse
import shutil
from datetime import datetime


class CloudMigrator:
    """Migrates YPF BI Monitor apps to cloud-ready version"""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.dry_run = dry_run
        self.backup_dir = project_root / "backups" / f"pre_cloud_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def migrate_all(self) -> Dict[str, bool]:
        """Migrate all apps to cloud-ready version"""
        apps_to_migrate = [
            'powerbi_analyzer.py',
            'documentation_generator.py',
            'dax_optimizer.py',
            'layout_organizer.py',
            'bi_bot.py'
        ]

        results = {}
        for app_file in apps_to_migrate:
            app_path = self.apps_dir / app_file
            if app_path.exists():
                print(f"\n{'='*60}")
                print(f"📦 Migrating: {app_file}")
                print(f"{'='*60}")
                success = self.migrate_app(app_path)
                results[app_file] = success
            else:
                print(f"⚠️  Skipping {app_file} (not found)")
                results[app_file] = False

        return results

    def migrate_app(self, app_path: Path) -> bool:
        """Migrate a single app to cloud-ready version"""
        try:
            # Read original content
            with open(app_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Create backup
            if not self.dry_run:
                self._create_backup(app_path, original_content)

            # Apply transformations
            new_content = original_content

            # 1. Add import for pbip_loader
            new_content = self._add_import(new_content)

            # 2. Replace text_input with load_pbip_cloud_ready
            new_content, replacements = self._replace_text_input(new_content)

            # 3. Remove old path validation logic
            new_content = self._remove_path_validation(new_content)

            # Show changes
            if replacements > 0:
                print(f"✅ Found {replacements} text_input pattern(s) to replace")
                self._show_diff(original_content, new_content, app_path.name)

                if not self.dry_run:
                    # Write new content
                    with open(app_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Migration completed: {app_path.name}")
                else:
                    print(f"🔍 DRY RUN: No changes written to {app_path.name}")

                return True
            else:
                print(f"ℹ️  No text_input patterns found in {app_path.name}")
                return False

        except Exception as e:
            print(f"❌ Error migrating {app_path.name}: {str(e)}")
            return False

    def _add_import(self, content: str) -> str:
        """Add import for pbip_loader if not present"""
        if 'from shared.pbip_loader import' in content:
            print("  ✓ Import already present")
            return content

        # Find where to insert import (after existing imports)
        import_pattern = r'(import streamlit as st\n)'
        replacement = r'\1from shared.pbip_loader import load_pbip_cloud_ready\n'

        new_content = re.sub(import_pattern, replacement, content, count=1)

        if new_content != content:
            print("  ✓ Added import: from shared.pbip_loader import load_pbip_cloud_ready")
        else:
            # Try alternative insertion point
            import_pattern = r'(from pathlib import Path\n)'
            new_content = re.sub(import_pattern, replacement, content, count=1)
            if new_content != content:
                print("  ✓ Added import: from shared.pbip_loader import load_pbip_cloud_ready")

        return new_content

    def _replace_text_input(self, content: str) -> Tuple[str, int]:
        """Replace st.text_input for PBIP path with load_pbip_cloud_ready"""

        # Pattern 1: Simple text_input with "ruta" or "path" in label
        pattern1 = r'pbip_path\s*=\s*st\.text_input\s*\(\s*["\'].*?(?:ruta|path).*?["\'].*?\)'

        # Pattern 2: More complex text_input with multiple parameters
        pattern2 = r'pbip_path\s*=\s*st\.text_input\([^)]+(?:placeholder|value)[^)]+\)'

        replacements = 0
        new_content = content

        # Try pattern 1
        matches = list(re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL))
        if matches:
            print(f"  ✓ Found {len(matches)} simple text_input pattern(s)")
            for match in matches:
                old_code = match.group(0)
                # Generate unique key based on app name
                new_code = 'pbip_path = load_pbip_cloud_ready(key="pbip_upload", persistent_storage=True)'
                new_content = new_content.replace(old_code, new_code, 1)
                replacements += 1
                print(f"    • Replaced: {old_code[:50]}...")

        # Try pattern 2 if pattern 1 didn't match
        if not matches:
            matches = list(re.finditer(pattern2, content, re.IGNORECASE | re.DOTALL))
            if matches:
                print(f"  ✓ Found {len(matches)} complex text_input pattern(s)")
                for match in matches:
                    old_code = match.group(0)
                    new_code = 'pbip_path = load_pbip_cloud_ready(key="pbip_upload", persistent_storage=True)'
                    new_content = new_content.replace(old_code, new_code, 1)
                    replacements += 1
                    print(f"    • Replaced: {old_code[:50]}...")

        return new_content, replacements

    def _remove_path_validation(self, content: str) -> str:
        """Remove old path validation logic (Path.exists() checks)"""

        # Pattern: if pbip_path and not Path(pbip_path).exists():
        pattern = r'if\s+pbip_path\s+and\s+not\s+Path\(pbip_path\)\.exists\(\):.*?(?=\n(?:if|def|\w+\s*=))'

        new_content = re.sub(pattern, '', content, flags=re.DOTALL)

        if new_content != content:
            print("  ✓ Removed old path validation logic")

        return new_content

    def _create_backup(self, app_path: Path, content: str):
        """Create backup of original file"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / app_path.name

        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  💾 Backup created: {backup_path}")

    def _show_diff(self, old_content: str, new_content: str, filename: str):
        """Show simplified diff of changes"""
        print(f"\n  📝 Changes in {filename}:")
        print(f"  {'-'*56}")

        # Find the changed lines
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')

        for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines), 1):
            if old_line != new_line:
                if 'pbip_path' in old_line or 'pbip_path' in new_line:
                    print(f"  Line {i}:")
                    if old_line.strip():
                        print(f"    - {old_line.strip()}")
                    if new_line.strip():
                        print(f"    + {new_line.strip()}")

    def generate_migration_report(self, results: Dict[str, bool]):
        """Generate migration report"""
        print(f"\n{'='*60}")
        print("📊 MIGRATION REPORT")
        print(f"{'='*60}")

        successful = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"\nTotal apps processed: {total}")
        print(f"Successfully migrated: {successful}")
        print(f"Skipped/Failed: {total - successful}")

        print("\nDetails:")
        for app, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {app}")

        if not self.dry_run:
            print(f"\n💾 Backups saved to: {self.backup_dir}")
            print("\nTo restore backups:")
            print(f"  cp {self.backup_dir}/*.py apps/")
        else:
            print("\n🔍 DRY RUN: No files were modified")
            print("Remove --dry-run flag to apply changes")

        print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate YPF BI Monitor apps to cloud-ready version'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--app',
        type=str,
        help='Only migrate specific app (e.g., powerbi_analyzer)'
    )

    args = parser.parse_args()

    # Get project root (assuming script is in scripts/ folder)
    project_root = Path(__file__).parent.parent

    print("🚀 YPF BI Monitor - Cloud Migration Tool")
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print()

    migrator = CloudMigrator(project_root, dry_run=args.dry_run)

    if args.app:
        # Migrate single app
        app_file = args.app if args.app.endswith('.py') else f"{args.app}.py"
        app_path = project_root / "apps" / app_file

        if not app_path.exists():
            print(f"❌ App not found: {app_path}")
            sys.exit(1)

        print(f"Migrating single app: {app_file}")
        success = migrator.migrate_app(app_path)
        results = {app_file: success}
    else:
        # Migrate all apps
        print("Migrating all apps...")
        results = migrator.migrate_all()

    # Generate report
    migrator.generate_migration_report(results)

    # Exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
