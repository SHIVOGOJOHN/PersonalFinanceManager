"""
Dashboard Screen - Financial Overview
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from config import COLORS
from utils import format_currency, get_current_month_range, get_month_year, parse_date


class DashboardScreen(Screen):
    def __init__(self, db_handler, metrics_calculator, **kwargs):
        super().__init__(**kwargs)
        self.db = db_handler
        self.metrics = metrics_calculator
        self.name = 'dashboard'
        self.build_ui()
    
    def build_ui(self):
        """Build the dashboard UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, padding=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Summary cards
        summary_grid = self.create_summary_cards()
        content.add_widget(summary_grid)
        
        # Recent transactions
        recent_trans = self.create_recent_transactions()
        content.add_widget(recent_trans)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Bottom navigation
        nav = self.create_navigation()
        main_layout.add_widget(nav)
        
        self.add_widget(main_layout)
    
    def create_header(self):
        """Create header with title and month"""
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=[20, 15, 20, 15], spacing=5)
        
        with layout.canvas.before:
            Color(*COLORS['primary'])
            self.header_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        title = Label(
            text='Finance Manager',
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=40,
            halign='left',
            valign='bottom'
        )
        title.bind(size=title.setter('text_size'))
        
        start_date, end_date = get_current_month_range()
        month_label = Label(
            text=get_month_year(parse_date(start_date)),
            font_size='15sp',
            color=(1, 1, 1, 0.9),
            size_hint_y=None,
            height=30,
            halign='left',
            valign='top'
        )
        month_label.bind(size=month_label.setter('text_size'))
        
        layout.add_widget(title)
        layout.add_widget(month_label)
        
        return layout
    
    def create_summary_cards(self):
        """Create summary cards grid"""
        grid = GridLayout(cols=2, spacing=12, size_hint_y=None, height=340)
        
        summary = self.metrics.get_dashboard_summary()
        
        # Income card
        income_card = self.create_card(
            'Income',
            format_currency(summary['income']),
            COLORS['success']
        )
        grid.add_widget(income_card)
        
        # Expense card
        expense_card = self.create_card(
            'Expenses',
            format_currency(summary['expense']),
            COLORS['danger']
        )
        grid.add_widget(expense_card)
        
        # Savings card
        savings_card = self.create_card(
            'Savings',
            format_currency(summary['net_cash_flow']),
            COLORS['primary']
        )
        grid.add_widget(savings_card)
        
        # Savings rate card
        savings_rate_card = self.create_card(
            'Savings Rate',
            f"{summary['savings_rate']}%",
            COLORS['secondary']
        )
        grid.add_widget(savings_rate_card)
        
        return grid
    
    def create_card(self, title, value, color):
        """Create a summary card"""
        card = BoxLayout(orientation='vertical', padding=20, spacing=8)
        
        with card.canvas.before:
            Color(*color)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.bind(pos=lambda instance, value: setattr(self.card_rect, 'pos', value),
                  size=lambda instance, value: setattr(self.card_rect, 'size', value))
        
        title_label = Label(
            text=title,
            font_size='13sp',
            color=(1, 1, 1, 0.85),
            size_hint_y=0.3,
            halign='left',
            valign='bottom'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        value_label = Label(
            text=str(value),
            font_size='26sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.7,
            halign='left',
            valign='top'
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        card.add_widget(title_label)
        card.add_widget(value_label)
        
        return card
    
    def create_recent_transactions(self):
        """Create recent transactions list"""
        layout = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        # Title
        title = Label(
            text='Recent Transactions',
            font_size='18sp',
            bold=True,
            color=COLORS['text'],
            size_hint_y=None,
            height=35,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        layout.add_widget(title)
        
        # Transactions list
        trans_list = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        trans_list.bind(minimum_height=trans_list.setter('height'))
        
        transactions = self.db.get_recent_transactions(5)
        
        if not transactions:
            no_data_card = BoxLayout(orientation='vertical', padding=30, size_hint_y=None, height=100)
            with no_data_card.canvas.before:
                Color(*COLORS['card'])
                self.no_data_rect = RoundedRectangle(pos=no_data_card.pos, size=no_data_card.size, radius=[12])
            no_data_card.bind(pos=lambda instance, value: setattr(self.no_data_rect, 'pos', value),
                             size=lambda instance, value: setattr(self.no_data_rect, 'size', value))
            
            no_data = Label(
                text='No transactions yet\nAdd your first transaction!',
                color=COLORS['text_light'],
                font_size='14sp',
                halign='center'
            )
            no_data.bind(size=no_data.setter('text_size'))
            no_data_card.add_widget(no_data)
            trans_list.add_widget(no_data_card)
        else:
            for trans in transactions:
                trans_item = self.create_transaction_item(trans)
                trans_list.add_widget(trans_item)
        
        layout.add_widget(trans_list)
        
        return layout
    
    def create_transaction_item(self, trans):
        """Create a transaction list item"""
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, padding=[15, 10])
        
        with item.canvas.before:
            Color(*COLORS['card'])
            self.item_rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[10])
        item.bind(pos=lambda instance, value: setattr(self.item_rect, 'pos', value),
                  size=lambda instance, value: setattr(self.item_rect, 'size', value))
        
        # Left side - category and description
        left = BoxLayout(orientation='vertical', size_hint_x=0.65, spacing=4)
        category_label = Label(
            text=trans['category'],
            font_size='15sp',
            bold=True,
            color=COLORS['text'],
            halign='left',
            valign='bottom'
        )
        category_label.bind(size=category_label.setter('text_size'))
        
        desc_text = trans.get('description', '') or trans['date']
        date_label = Label(
            text=desc_text[:30] + '...' if len(desc_text) > 30 else desc_text,
            font_size='12sp',
            color=COLORS['text_light'],
            halign='left',
            valign='top'
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        left.add_widget(category_label)
        left.add_widget(date_label)
        
        # Right side - amount
        amount_color = COLORS['success'] if trans['type'] == 'income' else COLORS['danger']
        amount_text = f"+{format_currency(trans['amount'])}" if trans['type'] == 'income' else f"-{format_currency(trans['amount'])}"
        
        amount_label = Label(
            text=amount_text,
            font_size='17sp',
            bold=True,
            color=amount_color,
            size_hint_x=0.35,
            halign='right',
            valign='middle'
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        
        item.add_widget(left)
        item.add_widget(amount_label)
        
        return item
    
    def create_navigation(self):
        """Create bottom navigation"""
        nav = GridLayout(cols=4, size_hint_y=None, height=65, spacing=0, padding=0)
        
        with nav.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.nav_rect = Rectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda instance, value: setattr(self.nav_rect, 'pos', value),
                 size=lambda instance, value: setattr(self.nav_rect, 'size', value))
        
        # Dashboard button (active)
        dashboard_btn = Button(
            text='[b]Dashboard[/b]',
            markup=True,
            background_normal='',
            background_color=COLORS['primary'],
            color=(1, 1, 1, 1),
            font_size='13sp',
            on_press=lambda x: None
        )
        nav.add_widget(dashboard_btn)
        
        # Transactions button
        trans_btn = Button(
            text='Transactions',
            background_normal='',
            background_color=(0.98, 0.98, 0.98, 1),
            color=COLORS['text'],
            font_size='13sp',
            on_press=lambda x: setattr(self.manager, 'current', 'transactions')
        )
        nav.add_widget(trans_btn)
        
        # Metrics button
        metrics_btn = Button(
            text='Metrics',
            background_normal='',
            background_color=(0.98, 0.98, 0.98, 1),
            color=COLORS['text'],
            font_size='13sp',
            on_press=lambda x: setattr(self.manager, 'current', 'metrics')
        )
        nav.add_widget(metrics_btn)
        
        # Backup button
        backup_btn = Button(
            text='Backup',
            background_normal='',
            background_color=(0.98, 0.98, 0.98, 1),
            color=COLORS['text'],
            font_size='13sp',
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
        # Refresh data
        self.clear_widgets()
        self.build_ui()
