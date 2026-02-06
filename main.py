"""
Personal Finance Manager - Main Application
A Kivy-based personal finance management app with cloud backup
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

# Import database and business logic
from database import DatabaseHandler
from metrics import MetricsCalculator
from sync_manager import SyncManager

# Import screens
from screens.dashboard import DashboardScreen
from screens.transactions import TransactionsScreen
from screens.metrics import MetricsScreen
from screens.backup import BackupScreen

# Set window size for desktop testing (comment out for mobile)
Window.size = (400, 700)


class FinanceManagerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Personal Finance Manager'
        
        # Initialize core components
        self.db = DatabaseHandler()
        self.metrics = MetricsCalculator(self.db)
        self.sync = SyncManager(self.db)
    
    def build(self):
        """Build the application"""
        # Create screen manager
        sm = ScreenManager(transition=NoTransition())
        
        # Add screens
        sm.add_widget(DashboardScreen(self.db, self.metrics, name='dashboard'))
        sm.add_widget(TransactionsScreen(self.db, name='transactions'))
        sm.add_widget(MetricsScreen(self.db, self.metrics, name='metrics'))
        sm.add_widget(BackupScreen(self.db, self.sync, name='backup'))
        
        # Set initial screen
        sm.current = 'dashboard'
        
        return sm
    
    def on_start(self):
        """Called when the app starts"""
        print("Personal Finance Manager started successfully!")
        print(f"Database initialized at: {self.db.db_path}")
    
    def on_stop(self):
        """Called when the app is closing"""
        print("Personal Finance Manager closing...")
        return True


if __name__ == '__main__':
    FinanceManagerApp().run()
