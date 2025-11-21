"""
Project Cleanup Script
Identifies and removes unnecessary test, fix, and debug files
"""
import os
import shutil

# Files to keep (core application files)
KEEP_FILES = {
    'app.py',
    'database_config.py',
    'init_database.py',
    'journal.py',
    'admin_blueprint.py',
    'employee_dashboard_bp.py',
    'mentor.py',
    'subscription_admin.py',
    'subscription_models.py',
    'broker_bp.py',
    'multi_broker_system.py',
    'email_service.py',
    'toast_utils.py',
    'token_store.py',
    'gunicorn_config.py',
    'requirements_production.txt',
    'README.md',
    'render.yaml',
    'deploy.sh',
    'nginx.conf',
    '.env.example',
    '.gitignore',
    'client_secret.json',
    'dhan_token.json',
}

# Folders to keep
KEEP_FOLDERS = {
    'static',
    'templates',
    'migrations',
    'uploads',
    'instance',
    'logs',
    '.git',
    '.ebextensions',
}

# Files to remove (test, fix, debug, temp files)
REMOVE_PATTERNS = [
    'test_',
    'fix_',
    'debug_',
    'check_',
    'verify_',
    'temp',
    '_old',
    '_temp',
    'quick_',
    'simple_',
    'run_',
    'setup_',
    'restart_',
    'deploy_db_',
    'broker_connection_fix',
    'broker_production_fixes',
    'broker_url_fix',
    'angel_one_',
    'angel_totp_',
    'add_mtf_',
    'migrate_',
    'init_and_fix',
    'production_fix',
    'production_env_fix',
    'template_checker',
    'admin_test_',
    'create_missing_tables',
]

# Documentation files to remove
REMOVE_DOCS = [
    'BROKER_FIX_SUMMARY.md',
    'CLEANUP_COMPLETED.md',
    'MENTOR_FIX.md',
    'PRODUCTION_FIXES.md',
    'PRODUCTION_DEPLOYMENT_CHECKLIST.md',
    'production_checklist.md',
    'IMPORT_TRADE_IMPLEMENTATION.md',
    'PROJECT_STRUCTURE.md',
]

def should_remove_file(filename):
    """Check if file should be removed"""
    if filename in KEEP_FILES:
        return False
    
    # Check remove patterns
    for pattern in REMOVE_PATTERNS:
        if pattern in filename.lower():
            return True
    
    # Check documentation files
    if filename in REMOVE_DOCS:
        return True
    
    # Remove .env files except .env.example
    if filename.startswith('.env') and filename != '.env.example':
        return True
    
    # Remove Python cache files
    if filename.endswith('.pyc') or filename == 'tempCodeRunnerFile.py':
        return True
    
    return False

def cleanup_project():
    """Clean up project files"""
    removed_files = []
    kept_files = []
    
    print("🧹 Starting project cleanup...\n")
    
    # Get all files in current directory
    for item in os.listdir('.'):
        # Skip folders
        if os.path.isdir(item):
            if item == '__pycache__':
                try:
                    shutil.rmtree(item)
                    print(f"✓ Removed folder: {item}")
                    removed_files.append(item)
                except Exception as e:
                    print(f"✗ Error removing {item}: {e}")
            continue
        
        # Check if file should be removed
        if should_remove_file(item):
            try:
                os.remove(item)
                print(f"✓ Removed: {item}")
                removed_files.append(item)
            except Exception as e:
                print(f"✗ Error removing {item}: {e}")
        else:
            kept_files.append(item)
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   Removed: {len(removed_files)} files")
    print(f"   Kept: {len(kept_files)} files")
    
    print(f"\n📁 Core files kept:")
    for f in sorted(kept_files):
        print(f"   - {f}")
    
    return removed_files, kept_files

if __name__ == '__main__':
    removed, kept = cleanup_project()
    print("\n✅ Cleanup complete!")
