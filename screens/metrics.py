"""
Metrics Screen - Financial Analysis and Visualizations
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from config import COLORS
from utils import format_currency, get_current_month_range


class MetricsScreen(Screen):
    def __init__(self, db_handler, metrics_calculator, **kwargs):
        super().__init__(**kwargs)
        self.db = db_handler
        self.metrics = metrics_calculator
        self.name = 'metrics'
        self.build_ui()
    
    def build_ui(self):
        """Build the metrics UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=5)
        content.bind(minimum_height=content.setter('height'))
        
        # Key metrics
        metrics_section = self.create_key_metrics()
        content.add_widget(metrics_section)
        
        # Expense breakdown
        expense_section = self.create_expense_breakdown()
        content.add_widget(expense_section)
        
        # Budget adherence
        budget_section = self.create_budget_adherence()
        content.add_widget(budget_section)
        
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
            text='Financial Metrics',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        
        return layout
    
    def create_key_metrics(self):
        """Create key metrics section"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=250)
        
        # Section title
        title = Label(
            text='Key Metrics (Current Month)',
            font_size='18sp',
            bold=True,
            color=COLORS['text'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Get metrics
        start_date, end_date = get_current_month_range()
        summary = self.metrics.get_dashboard_summary()
        
        # Metrics grid
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        
        # Savings Rate
        savings_card = self.create_metric_card(
            'Savings Rate',
            f"{summary['savings_rate']}%",
            COLORS['success'] if summary['savings_rate'] > 20 else COLORS['warning']
        )
        grid.add_widget(savings_card)
        
        # Spending Rate
        spending_card = self.create_metric_card(
            'Spending Rate',
            f"{summary['spending_rate']}%",
            COLORS['danger'] if summary['spending_rate'] > 80 else COLORS['secondary']
        )
        grid.add_widget(spending_card)
        
        # Net Cash Flow
        cash_flow_card = self.create_metric_card(
            'Net Cash Flow',
            format_currency(summary['net_cash_flow']),
            COLORS['success'] if summary['net_cash_flow'] > 0 else COLORS['danger']
        )
        grid.add_widget(cash_flow_card)
        
        # Transaction Count
        count_card = self.create_metric_card(
            'Transactions',
            str(summary['transaction_count']),
            COLORS['primary']
        )
        grid.add_widget(count_card)
        
        section.add_widget(grid)
        
        return section
    
    def create_metric_card(self, title, value, color):
        """Create a metric card"""
        card = BoxLayout(orientation='vertical', padding=15, spacing=5)
        
        with card.canvas.before:
            Color(*color)
            card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
        card.bind(pos=lambda instance, value: setattr(card_rect, 'pos', value),
                  size=lambda instance, value: setattr(card_rect, 'size', value))
        
        title_label = Label(
            text=title,
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=0.4
        )
        
        value_label = Label(
            text=str(value),
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.6
        )
        
        card.add_widget(title_label)
        card.add_widget(value_label)
        
        return card
    
    def create_expense_breakdown(self):
        """Create expense breakdown section"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        # Section title
        title = Label(
            text='Expense Breakdown',
            font_size='18sp',
            bold=True,
            color=COLORS['text'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Get breakdown
        breakdown = self.metrics.get_expense_breakdown()
        
        if not breakdown:
            no_data = Label(
                text='No expense data available',
                color=COLORS['text_light'],
                size_hint_y=None,
                height=40
            )
            section.add_widget(no_data)
        else:
            # Create bars for each category
            for item in breakdown[:5]:  # Top 5 categories
                bar = self.create_category_bar(
                    item['category'],
                    item['total'],
                    item['percentage']
                )
                section.add_widget(bar)
        
        return section
    
    def create_category_bar(self, category, amount, percentage):
        """Create a category breakdown bar"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=5)
        
        # Category and amount
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        cat_label = Label(
            text=category,
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.6,
            halign='left',
            valign='middle'
        )
        cat_label.bind(size=cat_label.setter('text_size'))
        
        amount_label = Label(
            text=format_currency(amount),
            font_size='14sp',
            bold=True,
            color=COLORS['text'],
            size_hint_x=0.4,
            halign='right',
            valign='middle'
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        
        info_layout.add_widget(cat_label)
        info_layout.add_widget(amount_label)
        container.add_widget(info_layout)
        
        # Progress bar
        bar_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, padding=[0, 5, 0, 0])
        
        # Background
        bar_bg = BoxLayout(size_hint_x=1)
        with bar_bg.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            bar_bg_rect = RoundedRectangle(pos=bar_bg.pos, size=bar_bg.size, radius=[5])
        bar_bg.bind(pos=lambda instance, value: setattr(bar_bg_rect, 'pos', value),
                    size=lambda instance, value: setattr(bar_bg_rect, 'size', value))
        
        # Fill bar
        bar_fill = BoxLayout(size_hint_x=percentage/100)
        with bar_fill.canvas.before:
            Color(*COLORS['danger'])
            bar_fill_rect = RoundedRectangle(pos=bar_fill.pos, size=bar_fill.size, radius=[5])
        bar_fill.bind(pos=lambda instance, value: setattr(bar_fill_rect, 'pos', value),
                      size=lambda instance, value: setattr(bar_fill_rect, 'size', value))
        
        # Percentage label
        perc_label = Label(
            text=f'{percentage:.1f}%',
            font_size='12sp',
            color=COLORS['text'],
            size_hint_x=None,
            width=60
        )
        
        bar_bg.add_widget(bar_fill)
        bar_container.add_widget(bar_bg)
        bar_container.add_widget(perc_label)
        container.add_widget(bar_container)
        
        return container
    
    def create_budget_adherence(self):
        """Create budget adherence section"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        # Section title
        title = Label(
            text='Budget Adherence',
            font_size='18sp',
            bold=True,
            color=COLORS['text'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Get adherence
        adherence = self.metrics.get_budget_adherence()
        
        if not adherence:
            no_data = Label(
                text='No budget data available',
                color=COLORS['text_light'],
                size_hint_y=None,
                height=40
            )
            section.add_widget(no_data)
        else:
            # Show top categories by usage
            for item in adherence[:5]:
                budget_item = self.create_budget_item(item)
                section.add_widget(budget_item)
        
        return section
    
    def create_budget_item(self, item):
        """Create a budget adherence item"""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=70, spacing=5, padding=5)
        
        with container.canvas.before:
            Color(*COLORS['card'])
            container_rect = RoundedRectangle(pos=container.pos, size=container.size, radius=[5])
        container.bind(pos=lambda instance, value: setattr(container_rect, 'pos', value),
                       size=lambda instance, value: setattr(container_rect, 'size', value))
        
        # Category and amounts
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        cat_label = Label(
            text=item['category'],
            font_size='14sp',
            bold=True,
            color=COLORS['text'],
            size_hint_x=0.5,
            halign='left',
            valign='middle'
        )
        cat_label.bind(size=cat_label.setter('text_size'))
        
        amounts_label = Label(
            text=f"{format_currency(item['actual'])} / {format_currency(item['budget'])}",
            font_size='12sp',
            color=COLORS['text_light'],
            size_hint_x=0.5,
            halign='right',
            valign='middle'
        )
        amounts_label.bind(size=amounts_label.setter('text_size'))
        
        info_layout.add_widget(cat_label)
        info_layout.add_widget(amounts_label)
        container.add_widget(info_layout)
        
        # Progress bar
        bar_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        # Background
        bar_bg = BoxLayout(size_hint_x=1)
        with bar_bg.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            bar_bg_rect = RoundedRectangle(pos=bar_bg.pos, size=bar_bg.size, radius=[5])
        bar_bg.bind(pos=lambda instance, value: setattr(bar_bg_rect, 'pos', value),
                    size=lambda instance, value: setattr(bar_bg_rect, 'size', value))
        
        # Fill bar (cap at 100% for display)
        fill_percentage = min(item['percentage_used'], 100) / 100
        bar_fill = BoxLayout(size_hint_x=fill_percentage)
        
        # Color based on usage
        if item['over_budget']:
            bar_color = COLORS['danger']
        elif item['percentage_used'] >= 80:
            bar_color = COLORS['warning']
        else:
            bar_color = COLORS['success']
        
        with bar_fill.canvas.before:
            Color(*bar_color)
            bar_fill_rect = RoundedRectangle(pos=bar_fill.pos, size=bar_fill.size, radius=[5])
        bar_fill.bind(pos=lambda instance, value: setattr(bar_fill_rect, 'pos', value),
                      size=lambda instance, value: setattr(bar_fill_rect, 'size', value))
        
        # Percentage label
        perc_text = f'{item["percentage_used"]:.1f}%'
        if item['over_budget']:
            perc_text += ' (OVER)'
        
        perc_label = Label(
            text=perc_text,
            font_size='12sp',
            bold=item['over_budget'],
            color=bar_color,
            size_hint_x=None,
            width=100
        )
        
        bar_bg.add_widget(bar_fill)
        bar_container.add_widget(bar_bg)
        bar_container.add_widget(perc_label)
        container.add_widget(bar_container)
        
        return container
    
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
            background_color=COLORS['primary'],
            on_press=lambda x: self.manager.current == 'metrics'
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
        # Refresh data
        self.clear_widgets()
        self.build_ui()
