"""
Backup Screen - Cloud Sync and Restore
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from config import COLORS
from utils import get_time_ago
import threading


class BackupScreen(Screen):
    def __init__(self, db_handler, sync_manager, **kwargs):
        super().__init__(**kwargs)
        self.db = db_handler
        self.sync = sync_manager
        self.name = 'backup'
        self.sync_in_progress = False
        self.build_ui()
    
    def build_ui(self):
        """Build the backup UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=5)
        content.bind(minimum_height=content.setter('height'))
        
        # Sync status
        self.status_section = BoxLayout(orientation='vertical', size_hint_y=None)
        self.update_status_section()
        content.add_widget(self.status_section)
        
        # Action buttons
        actions = self.create_action_buttons()
        content.add_widget(actions)
        
        # Info section
        info = self.create_info_section()
        content.add_widget(info)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Bottom navigation
        nav = self.create_navigation()
        main_layout.add_widget(nav)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=60, padding=10)
        
        with layout.canvas.before:
            Color(*COLORS['primary'])
            self.header_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        title = Label(
            text='Backup & Restore',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        
        return layout
    
    def update_status_section(self):
        """Update sync status section"""
        self.status_section.clear_widgets()
        self.status_section.height = 200
        
        # Status card
        card = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=180)
        
        with card.canvas.before:
            Color(*COLORS['card'])
            card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
        card.bind(pos=lambda instance, value: setattr(card_rect, 'pos', value),
                  size=lambda instance, value: setattr(card_rect, 'size', value))
        
        # Get sync status
        status = self.sync.get_sync_status()
        
        # Status icon and text
        status_text = status['status'].upper()
        if status['status'] == 'success':
            status_color = COLORS['success']
            status_icon = '✓'
        elif status['status'] == 'failed':
            status_color = COLORS['danger']
            status_icon = '✗'
        else:
            status_color = COLORS['text_light']
            status_icon = '○'
        
        status_label = Label(
            text=f"{status_icon} {status_text}",
            font_size='24sp',
            bold=True,
            color=status_color,
            size_hint_y=None,
            height=40
        )
        card.add_widget(status_label)
        
        # Last sync time
        last_sync_text = get_time_ago(status['last_sync']) if status['last_sync'] else 'Never'
        last_sync_label = Label(
            text=f"Last sync: {last_sync_text}",
            font_size='14sp',
            color=COLORS['text'],
            size_hint_y=None,
            height=30
        )
        card.add_widget(last_sync_label)
        
        # Sync message
        message_label = Label(
            text=status['message'],
            font_size='14sp',
            color=COLORS['text_light'],
            size_hint_y=None,
            height=30
        )
        card.add_widget(message_label)
        
        # Unsynced count
        unsynced_label = Label(
            text=f"Unsynced transactions: {status['unsynced_count']}",
            font_size='14sp',
            bold=True,
            color=COLORS['warning'] if status['unsynced_count'] > 0 else COLORS['success'],
            size_hint_y=None,
            height=30
        )
        card.add_widget(unsynced_label)
        
        # Network status
        network_status = "Connected" if self.sync.check_network_connectivity() else "Offline"
        network_color = COLORS['success'] if network_status == "Connected" else COLORS['danger']
        
        network_label = Label(
            text=f"Network: {network_status}",
            font_size='14sp',
            color=network_color,
            size_hint_y=None,
            height=30
        )
        card.add_widget(network_label)
        
        self.status_section.add_widget(card)
    
    def create_action_buttons(self):
        """Create action buttons"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200)
        
        # Backup button
        backup_btn = Button(
            text='Backup to Cloud',
            size_hint_y=None,
            height=60,
            background_color=COLORS['primary'],
            font_size='16sp',
            on_press=self.start_backup
        )
        section.add_widget(backup_btn)
        
        # Restore button
        restore_btn = Button(
            text='Restore from Cloud',
            size_hint_y=None,
            height=60,
            background_color=COLORS['secondary'],
            font_size='16sp',
            on_press=self.confirm_restore
        )
        section.add_widget(restore_btn)
        
        # Sync button (incremental)
        sync_btn = Button(
            text='Sync Unsynced Transactions',
            size_hint_y=None,
            height=60,
            background_color=COLORS['accent'],
            font_size='16sp',
            on_press=self.start_sync
        )
        section.add_widget(sync_btn)
        
        return section
    
    def create_info_section(self):
        """Create info section"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200, padding=10)
        
        with section.canvas.before:
            Color(*COLORS['background'])
            section_rect = RoundedRectangle(pos=section.pos, size=section.size, radius=[10])
        section.bind(pos=lambda instance, value: setattr(section_rect, 'pos', value),
                     size=lambda instance, value: setattr(section_rect, 'size', value))
        
        title = Label(
            text='About Backup & Sync',
            font_size='16sp',
            bold=True,
            color=COLORS['text'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        info_text = """• Backup: Upload all data to cloud
• Restore: Download and merge cloud data
• Sync: Upload only new transactions
• Data is stored securely on MySQL server
• Internet connection required"""
        
        info_label = Label(
            text=info_text,
            font_size='13sp',
            color=COLORS['text_light'],
            halign='left',
            valign='top'
        )
        info_label.bind(size=info_label.setter('text_size'))
        section.add_widget(info_label)
        
        return section
    
    def start_backup(self, instance):
        """Start backup process"""
        if self.sync_in_progress:
            self.show_message('Sync in Progress', 'Please wait for current operation to complete')
            return
        
        self.sync_in_progress = True
        self.show_loading('Backing up to cloud...')
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self.backup_thread)
        thread.start()
    
    def backup_thread(self):
        """Backup thread"""
        success, message = self.sync.backup_to_cloud()
        Clock.schedule_once(lambda dt: self.backup_complete(success, message))
    
    def backup_complete(self, success, message):
        """Backup complete callback"""
        self.sync_in_progress = False
        self.close_loading()
        
        if success:
            self.show_message('Backup Successful', message)
        else:
            self.show_message('Backup Failed', message)
        
        self.update_status_section()
    
    def confirm_restore(self, instance):
        """Confirm restore operation"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        warning = Label(
            text='This will merge cloud data with local data. Continue?',
            halign='center'
        )
        warning.bind(size=warning.setter('text_size'))
        content.add_widget(warning)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        yes_btn = Button(
            text='Yes, Restore',
            background_color=COLORS['success'],
            on_press=lambda x: self.start_restore(popup)
        )
        
        no_btn = Button(
            text='Cancel',
            background_color=COLORS['text_light'],
            on_press=lambda x: popup.dismiss()
        )
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirm Restore',
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def start_restore(self, confirm_popup):
        """Start restore process"""
        confirm_popup.dismiss()
        
        if self.sync_in_progress:
            self.show_message('Sync in Progress', 'Please wait for current operation to complete')
            return
        
        self.sync_in_progress = True
        self.show_loading('Restoring from cloud...')
        
        # Run in thread
        thread = threading.Thread(target=self.restore_thread)
        thread.start()
    
    def restore_thread(self):
        """Restore thread"""
        success, message = self.sync.restore_from_cloud()
        Clock.schedule_once(lambda dt: self.restore_complete(success, message))
    
    def restore_complete(self, success, message):
        """Restore complete callback"""
        self.sync_in_progress = False
        self.close_loading()
        
        if success:
            self.show_message('Restore Successful', message)
        else:
            self.show_message('Restore Failed', message)
        
        self.update_status_section()
    
    def start_sync(self, instance):
        """Start incremental sync"""
        if self.sync_in_progress:
            self.show_message('Sync in Progress', 'Please wait for current operation to complete')
            return
        
        self.sync_in_progress = True
        self.show_loading('Syncing transactions...')
        
        # Run in thread
        thread = threading.Thread(target=self.sync_thread)
        thread.start()
    
    def sync_thread(self):
        """Sync thread"""
        success, message = self.sync.sync_incremental()
        Clock.schedule_once(lambda dt: self.sync_complete(success, message))
    
    def sync_complete(self, success, message):
        """Sync complete callback"""
        self.sync_in_progress = False
        self.close_loading()
        
        if success:
            self.show_message('Sync Successful', message)
        else:
            self.show_message('Sync Failed', message)
        
        self.update_status_section()
    
    def show_loading(self, message):
        """Show loading popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(text=message, font_size='16sp'))
        
        self.loading_popup = Popup(
            title='Please Wait',
            content=content,
            size_hint=(0.7, 0.2),
            auto_dismiss=False
        )
        self.loading_popup.open()
    
    def close_loading(self):
        """Close loading popup"""
        if hasattr(self, 'loading_popup'):
            self.loading_popup.dismiss()
    
    def show_message(self, title, message):
        """Show message popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        msg_label = Label(text=message, halign='center')
        msg_label.bind(size=msg_label.setter('text_size'))
        content.add_widget(msg_label)
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            background_color=COLORS['primary'],
            on_press=lambda x: popup.dismiss()
        )
        content.add_widget(btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def create_navigation(self):
        """Create bottom navigation"""
        nav = GridLayout(cols=4, size_hint_y=None, height=60, spacing=5, padding=5)
        
        with nav.canvas.before:
            Color(*COLORS['card'])
            nav_rect = Rectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda instance, value: setattr(nav_rect, 'pos', value),
                 size=lambda instance, value: setattr(nav_rect, 'size', value))
        
        dashboard_btn = Button(
            text='Dashboard',
            background_normal='',
            background_color=COLORS['text_light'],
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        )
        nav.add_widget(dashboard_btn)
        
        trans_btn = Button(
            text='Transactions',
            background_normal='',
            background_color=COLORS['text_light'],
            on_press=lambda x: setattr(self.manager, 'current', 'transactions')
        )
        nav.add_widget(trans_btn)
        
        metrics_btn = Button(
            text='Metrics',
            background_normal='',
            background_color=COLORS['text_light'],
            on_press=lambda x: setattr(self.manager, 'current', 'metrics')
        )
        nav.add_widget(metrics_btn)
        
        backup_btn = Button(
            text='Backup',
            background_color=COLORS['primary'],
            on_press=lambda x: self.manager.current == 'backup'
        )
        nav.add_widget(backup_btn)
        
        return nav
    
    def update_rect(self, instance, value):
        """Update rectangle position/size"""
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.update_status_section()
