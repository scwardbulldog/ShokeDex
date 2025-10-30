"""
Database migration management for ShokeDex
Handles schema version tracking and migrations
"""

from typing import List, Callable
from .database import Database


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: int, description: str, upgrade: Callable, downgrade: Callable = None):
        """
        Initialize migration
        
        Args:
            version: Migration version number
            description: Description of migration
            upgrade: Function to apply migration
            downgrade: Optional function to revert migration
        """
        self.version = version
        self.description = description
        self.upgrade = upgrade
        self.downgrade = downgrade


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db: Database):
        """
        Initialize migration manager
        
        Args:
            db: Database instance
        """
        self.db = db
        self.migrations: List[Migration] = []
        
    def register_migration(self, migration: Migration):
        """
        Register a migration
        
        Args:
            migration: Migration to register
        """
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
        
    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of pending migrations
        
        Returns:
            List of migrations that haven't been applied
        """
        current_version = self.db.get_schema_version()
        return [m for m in self.migrations if m.version > current_version]
        
    def apply_migration(self, migration: Migration):
        """
        Apply a single migration
        
        Args:
            migration: Migration to apply
        """
        print(f"Applying migration {migration.version}: {migration.description}")
        
        try:
            migration.upgrade(self.db)
            
            # Record migration in schema_version table
            self.db.execute("""
                INSERT INTO schema_version (version, description)
                VALUES (?, ?)
            """, (migration.version, migration.description))
            
            self.db.commit()
            print(f"Migration {migration.version} applied successfully")
            
        except Exception as e:
            print(f"Error applying migration {migration.version}: {e}")
            raise
            
    def apply_all_pending(self):
        """Apply all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
            
        print(f"Found {len(pending)} pending migration(s)")
        
        for migration in pending:
            self.apply_migration(migration)
            
        print("All migrations applied successfully")
        
    def rollback_migration(self, migration: Migration):
        """
        Rollback a single migration
        
        Args:
            migration: Migration to rollback
        """
        if not migration.downgrade:
            raise RuntimeError(f"Migration {migration.version} has no downgrade function")
            
        print(f"Rolling back migration {migration.version}: {migration.description}")
        
        try:
            migration.downgrade(self.db)
            
            # Remove migration from schema_version table
            self.db.execute("""
                DELETE FROM schema_version WHERE version = ?
            """, (migration.version,))
            
            self.db.commit()
            print(f"Migration {migration.version} rolled back successfully")
            
        except Exception as e:
            print(f"Error rolling back migration {migration.version}: {e}")
            raise


# Example migration for future use
def _example_migration_v2_upgrade(db: Database):
    """Example migration: Add new column to pokemon table"""
    cursor = db.conn.cursor()
    cursor.execute("""
        ALTER TABLE pokemon ADD COLUMN example_field TEXT
    """)


def _example_migration_v2_downgrade(db: Database):
    """Example migration rollback"""
    # Note: SQLite doesn't support DROP COLUMN easily
    # Would need to recreate table without the column
    pass


# Register example migration (commented out - for documentation)
# example_migration = Migration(
#     version=2,
#     description="Add example_field to pokemon table",
#     upgrade=_example_migration_v2_upgrade,
#     downgrade=_example_migration_v2_downgrade
# )
