"""
Synchronization manager for cloud backup and restore
"""
import requests
import json
from datetime import datetime
from config import BACKUP_ENDPOINT, RESTORE_ENDPOINT, SYNC_TIMEOUT, MAX_RETRY_ATTEMPTS
from utils import format_datetime


class SyncManager:
    def __init__(self, db_handler):
        self.db = db_handler
        self.timeout = SYNC_TIMEOUT
        self.max_retries = MAX_RETRY_ATTEMPTS
    
    def check_network_connectivity(self):
        """Check if network is available"""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def backup_to_cloud(self):
        """
        Backup local data to cloud via API
        Returns (success, message)
        """
        if not self.check_network_connectivity():
            return False, "No internet connection"
        
        try:
            # Get all data to backup
            data = self.db.export_all_data()
            
            # Send to API
            response = self._send_request_with_retry(
                'POST',
                BACKUP_ENDPOINT,
                json=data
            )
            
            if response and response.status_code == 200:
                # Mark all transactions as synced
                trans_ids = [t['id'] for t in data['transactions']]
                if trans_ids:
                    self.db.mark_transactions_synced(trans_ids)
                
                # Update sync metadata
                self.db.update_sync_metadata('success', 'Backup completed successfully')
                return True, "Backup completed successfully"
            else:
                error_msg = f"Backup failed: {response.status_code if response else 'No response'}"
                self.db.update_sync_metadata('failed', error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            self.db.update_sync_metadata('failed', error_msg)
            return False, error_msg
    
    def restore_from_cloud(self):
        """
        Restore data from cloud via API
        Returns (success, message)
        """
        if not self.check_network_connectivity():
            return False, "No internet connection"
        
        try:
            # Get data from API
            response = self._send_request_with_retry(
                'GET',
                RESTORE_ENDPOINT
            )
            
            if response and response.status_code == 200:
                data = response.json()
                
                # Import data to local database
                self.db.import_data(data)
                
                # Update sync metadata
                self.db.update_sync_metadata('success', 'Restore completed successfully')
                return True, "Restore completed successfully"
            else:
                error_msg = f"Restore failed: {response.status_code if response else 'No response'}"
                self.db.update_sync_metadata('failed', error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Restore error: {str(e)}"
            self.db.update_sync_metadata('failed', error_msg)
            return False, error_msg
    
    def sync_incremental(self):
        """
        Sync only unsynced transactions (incremental backup)
        Returns (success, message)
        """
        if not self.check_network_connectivity():
            return False, "No internet connection"
        
        try:
            # Get unsynced transactions
            unsynced = self.db.get_unsynced_transactions()
            
            if not unsynced:
                return True, "Nothing to sync"
            
            # Prepare data
            data = {
                "transactions": unsynced,
                "budgets": [],
                "categories": []
            }
            
            # Send to API
            response = self._send_request_with_retry(
                'POST',
                BACKUP_ENDPOINT,
                json=data
            )
            
            if response and response.status_code == 200:
                # Mark transactions as synced
                trans_ids = [t['id'] for t in unsynced]
                self.db.mark_transactions_synced(trans_ids)
                
                # Update sync metadata
                self.db.update_sync_metadata('success', f'Synced {len(unsynced)} transactions')
                return True, f"Synced {len(unsynced)} transactions"
            else:
                error_msg = f"Sync failed: {response.status_code if response else 'No response'}"
                self.db.update_sync_metadata('failed', error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Sync error: {str(e)}"
            self.db.update_sync_metadata('failed', error_msg)
            return False, error_msg
    
    def _send_request_with_retry(self, method, url, **kwargs):
        """Send HTTP request with retry logic"""
        kwargs['timeout'] = self.timeout
        
        for attempt in range(self.max_retries):
            try:
                if method == 'GET':
                    response = requests.get(url, **kwargs)
                elif method == 'POST':
                    response = requests.post(url, **kwargs)
                else:
                    return None
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise
                continue
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                continue
        
        return None
    
    def get_sync_status(self):
        """Get current sync status"""
        metadata = self.db.get_sync_metadata()
        if not metadata:
            return {
                'last_sync': 'Never',
                'status': 'never',
                'message': 'Not synced yet',
                'unsynced_count': len(self.db.get_unsynced_transactions())
            }
        
        return {
            'last_sync': metadata['last_sync'],
            'status': metadata['sync_status'],
            'message': metadata['sync_message'],
            'unsynced_count': len(self.db.get_unsynced_transactions())
        }
