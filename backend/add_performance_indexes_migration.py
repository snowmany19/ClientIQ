# backend/add_performance_indexes_migration.py
# Performance optimization migration for ContractGuard.ai

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import get_settings

def add_performance_indexes():
    """Add performance indexes to improve query performance."""
    settings = get_settings()
    
    # Database connection parameters
    db_params = {
        'host': settings.database_host,
        'port': settings.database_port,
        'database': settings.database_name,
        'user': settings.database_user,
        'password': settings.database_password
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔍 Adding performance indexes to ContractGuard.ai database...")
        
        # Contract-related indexes
        contract_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_workspace_id ON contract_records(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_owner_user_id ON contract_records(owner_user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_category ON contract_records(category)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_status ON contract_records(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_created_at ON contract_records(created_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_effective_date ON contract_records(effective_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_term_end ON contract_records(term_end)"
        ]
        
        # User-related indexes
        user_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_workspace_id ON users(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription_status ON users(subscription_status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_plan_id ON users(plan_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at)"
        ]
        
        # Workspace-related indexes
        workspace_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_company_name ON workspaces(company_name)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_industry ON workspaces(industry)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_created_at ON workspaces(created_at)"
        ]
        
        # File storage indexes
        file_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_workspace_id ON file_storage(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_contract_id ON file_storage(contract_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_uploaded_by ON file_storage(uploaded_by)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_created_at ON file_storage(created_at)"
        ]
        
        # Analytics and notification indexes
        analytics_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_workspace_id ON analytics_events(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_user_id ON analytics_events(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_timestamp ON analytics_events(timestamp)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_workspace_id ON notifications(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)"
        ]
        
        # Communication and session indexes
        communication_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_workspace_id ON communication_logs(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_user_id ON communication_logs(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_contract_id ON communication_logs(contract_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_communication_type ON communication_logs(communication_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_sent_at ON communication_logs(sent_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_is_active ON user_sessions(is_active)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at)"
        ]
        
        # Performance metrics indexes
        performance_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_metric_name ON performance_metrics(metric_name)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_workspace_id ON performance_metrics(workspace_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)"
        ]
        
        # Two-factor authentication indexes
        twofa_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_2fa_user_id ON two_factor_codes(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_2fa_expires_at ON two_factor_codes(expires_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_2fa_used ON two_factor_codes(used)"
        ]
        
        # Email template indexes
        template_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_templates_name ON email_templates(name)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_templates_is_active ON email_templates(is_active)"
        ]
        
        # Combined indexes for common query patterns
        combined_indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_workspace_status ON contract_records(workspace_id, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_workspace_category ON contract_records(workspace_id, category)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_owner_status ON contract_records(owner_user_id, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_workspace_role ON users(workspace_id, role)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_files_workspace_contract ON file_storage(workspace_id, contract_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_workspace_type ON analytics_events(workspace_id, event_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)"
        ]
        
        # All indexes to create
        all_indexes = (
            contract_indexes + 
            user_indexes + 
            workspace_indexes + 
            file_indexes + 
            analytics_indexes + 
            communication_indexes + 
            performance_indexes + 
            twofa_indexes + 
            template_indexes + 
            combined_indexes
        )
        
        # Execute index creation
        for i, index_sql in enumerate(all_indexes, 1):
            try:
                print(f"Creating index {i}/{len(all_indexes)}...")
                cursor.execute(index_sql)
                print(f"✅ Index created successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not create index: {e}")
                continue
        
        print(f"\n🎉 Performance indexes added successfully!")
        print(f"Total indexes processed: {len(all_indexes)}")
        
        # Verify indexes were created
        cursor.execute("""
            SELECT schemaname, tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname
        """)
        
        created_indexes = cursor.fetchall()
        print(f"\n📊 Created indexes:")
        for schema, table, index in created_indexes:
            print(f"  - {index} on {table}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error adding performance indexes: {e}")
        if 'conn' in locals():
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    add_performance_indexes() 