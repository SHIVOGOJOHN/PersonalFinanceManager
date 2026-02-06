"""
Transactions Screen - Add, Edit, Delete Transactions
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from datetime import datetime
from config import COLORS
from utils import format_currency, format_date, validate_amount, validate_date


class TransactionsScreen(Screen):
    def __init__(self, db_handler, **kwargs):
        super().__init__(**kwargs)
        self.db = db_handler
        self.name = 'transactions'
        self.current_transaction = None
        self.build_ui()
    
    def build_ui(self):
        """Build the transactions UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Add transaction button
        add_btn = Button(
            text='+ Add Transaction',
            size_hint_y=None,
            height=50,
            background_color=COLORS['primary'],
            on_press=self.show_add_transaction_popup
        )
        main_layout.add_widget(add_btn)
        
        # Transactions list
        self.trans_list_container = BoxLayout(orientation='vertical')
        self.refresh_transactions_list()
        main_layout.add_widget(self.trans_list_container)
        
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
            text='Transactions',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        
        return layout
    
    def refresh_transactions_list(self):
        """Refresh the transactions list"""
        self.trans_list_container.clear_widgets()
        
        scroll = ScrollView()
        trans_list = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, padding=5)
        trans_list.bind(minimum_height=trans_list.setter('height'))
        
        transactions = self.db.get_all_transactions()
        
        if not transactions:
            no_data = Label(
                text='No transactions yet. Tap "Add Transaction" to get started!',
                color=COLORS['text_light'],
                size_hint_y=None,
                height=60
            )
            trans_list.add_widget(no_data)
        else:
            for trans in transactions:
                trans_item = self.create_transaction_item(trans)
                trans_list.add_widget(trans_item)
        
        scroll.add_widget(trans_list)
        self.trans_list_container.add_widget(scroll)
    
    def create_transaction_item(self, trans):
        """Create a transaction list item"""
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, padding=10, spacing=10)
        
        with item.canvas.before:
            Color(*COLORS['card'])
            item_rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[5])
        item.bind(pos=lambda instance, value: setattr(item_rect, 'pos', value),
                  size=lambda instance, value: setattr(item_rect, 'size', value))
        
        # Left side - details
        left = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        category_label = Label(
            text=trans['category'],
            font_size='16sp',
            bold=True,
            color=COLORS['text'],
            halign='left',
            valign='middle'
        )
        category_label.bind(size=category_label.setter('text_size'))
        
        desc_label = Label(
            text=trans.get('description', 'No description'),
            font_size='12sp',
            color=COLORS['text_light'],
            halign='left',
            valign='middle'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        date_label = Label(
            text=trans['date'],
            font_size='12sp',
            color=COLORS['text_light'],
            halign='left',
            valign='middle'
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        left.add_widget(category_label)
        left.add_widget(desc_label)
        left.add_widget(date_label)
        
        # Middle - amount
        amount_color = COLORS['success'] if trans['type'] == 'income' else COLORS['danger']
        amount_text = f"+{format_currency(trans['amount'])}" if trans['type'] == 'income' else f"-{format_currency(trans['amount'])}"
        
        amount_label = Label(
            text=amount_text,
            font_size='18sp',
            bold=True,
            color=amount_color,
            size_hint_x=0.25
        )
        
        # Right side - actions
        actions = BoxLayout(orientation='vertical', size_hint_x=0.15, spacing=5)
        
        edit_btn = Button(
            text='Edit',
            size_hint_y=0.5,
            background_color=COLORS['secondary'],
            on_press=lambda x: self.show_edit_transaction_popup(trans)
        )
        
        delete_btn = Button(
            text='Del',
            size_hint_y=0.5,
            background_color=COLORS['danger'],
            on_press=lambda x: self.confirm_delete(trans['id'])
        )
        
        actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        
        item.add_widget(left)
        item.add_widget(amount_label)
        item.add_widget(actions)
        
        return item
    
    def show_add_transaction_popup(self, instance):
        """Show popup to add new transaction"""
        self.current_transaction = None
        self.show_transaction_form_popup('Add Transaction')
    
    def show_edit_transaction_popup(self, trans):
        """Show popup to edit transaction"""
        self.current_transaction = trans
        self.show_transaction_form_popup('Edit Transaction')
    
    def show_transaction_form_popup(self, title):
        """Show transaction form popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Type selector
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        type_layout.add_widget(Label(text='Type:', size_hint_x=0.3))
        type_spinner = Spinner(
            text=self.current_transaction['type'].capitalize() if self.current_transaction else 'Expense',
            values=('Income', 'Expense'),
            size_hint_x=0.7
        )
        type_layout.add_widget(type_spinner)
        content.add_widget(type_layout)
        
        # Category selector
        cat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        cat_layout.add_widget(Label(text='Category:', size_hint_x=0.3))
        
        # Get categories based on type
        categories = self.db.get_categories('expense')
        cat_names = [cat['name'] for cat in categories]
        
        cat_spinner = Spinner(
            text=self.current_transaction['category'] if self.current_transaction else cat_names[0] if cat_names else 'Other',
            values=cat_names,
            size_hint_x=0.7
        )
        cat_layout.add_widget(cat_spinner)
        content.add_widget(cat_layout)
        
        # Update categories when type changes
        def update_categories(spinner, text):
            cat_type = 'income' if text.lower() == 'income' else 'expense'
            categories = self.db.get_categories(cat_type)
            cat_names = [cat['name'] for cat in categories]
            cat_spinner.values = cat_names
            if cat_names:
                cat_spinner.text = cat_names[0]
        
        type_spinner.bind(text=update_categories)
        
        # Amount input
        amount_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        amount_layout.add_widget(Label(text='Amount:', size_hint_x=0.3))
        amount_input = TextInput(
            text=str(self.current_transaction['amount']) if self.current_transaction else '',
            multiline=False,
            input_filter='float',
            size_hint_x=0.7
        )
        amount_layout.add_widget(amount_input)
        content.add_widget(amount_layout)
        
        # Date input
        date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        date_layout.add_widget(Label(text='Date:', size_hint_x=0.3))
        date_input = TextInput(
            text=self.current_transaction['date'] if self.current_transaction else format_date(datetime.now()),
            multiline=False,
            size_hint_x=0.7
        )
        date_layout.add_widget(date_input)
        content.add_widget(date_layout)
        
        # Description input
        desc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)
        desc_layout.add_widget(Label(text='Description:', size_hint_x=0.3))
        desc_input = TextInput(
            text=self.current_transaction.get('description', '') if self.current_transaction else '',
            multiline=True,
            size_hint_x=0.7
        )
        desc_layout.add_widget(desc_input)
        content.add_widget(desc_layout)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        save_btn = Button(
            text='Save',
            background_color=COLORS['success'],
            on_press=lambda x: self.save_transaction(
                type_spinner.text.lower(),
                cat_spinner.text,
                amount_input.text,
                date_input.text,
                desc_input.text,
                popup
            )
        )
        
        cancel_btn = Button(
            text='Cancel',
            background_color=COLORS['text_light'],
            on_press=lambda x: popup.dismiss()
        )
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.7)
        )
        popup.open()
    
    def save_transaction(self, trans_type, category, amount, date, description, popup):
        """Save transaction"""
        # Validate amount
        amount_val, error = validate_amount(amount)
        if error:
            self.show_error(error)
            return
        
        # Validate date
        valid, error = validate_date(date)
        if not valid:
            self.show_error(error)
            return
        
        try:
            if self.current_transaction:
                # Update existing
                self.db.update_transaction(
                    self.current_transaction['id'],
                    date=date,
                    category=category,
                    trans_type=trans_type,
                    amount=amount_val,
                    description=description
                )
            else:
                # Add new
                self.db.add_transaction(
                    date=date,
                    category=category,
                    trans_type=trans_type,
                    amount=amount_val,
                    description=description
                )
            
            popup.dismiss()
            self.refresh_transactions_list()
            
        except Exception as e:
            self.show_error(f"Error saving transaction: {str(e)}")
    
    def confirm_delete(self, trans_id):
        """Confirm deletion"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text='Are you sure you want to delete this transaction?'))
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        yes_btn = Button(
            text='Yes, Delete',
            background_color=COLORS['danger'],
            on_press=lambda x: self.delete_transaction(trans_id, popup)
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
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def delete_transaction(self, trans_id, popup):
        """Delete transaction"""
        try:
            self.db.delete_transaction(trans_id)
            popup.dismiss()
            self.refresh_transactions_list()
        except Exception as e:
            self.show_error(f"Error deleting transaction: {str(e)}")
    
    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=50,
            on_press=lambda x: popup.dismiss()
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='Error',
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
            background_color=COLORS['primary'],
            on_press=lambda x: self.manager.current == 'transactions'
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
            background_normal='',
            background_color=COLORS['text_light'],
            on_press=lambda x: setattr(self.manager, 'current', 'backup')
        )
        nav.add_widget(backup_btn)
        
        return nav
    
    def update_rect(self, instance, value):
        """Update rectangle position/size"""
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh_transactions_list()
