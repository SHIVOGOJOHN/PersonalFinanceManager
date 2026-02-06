"""
Financial metrics calculation engine
"""
from datetime import datetime
from utils import get_current_month_range, get_date_range_months


class MetricsCalculator:
    def __init__(self, db_handler):
        self.db = db_handler
    
    def get_savings_rate(self, start_date=None, end_date=None):
        """
        Calculate savings rate: (Total Income - Total Expenses) / Total Income * 100
        Returns percentage
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        income = self.db.get_total_by_type('income', start_date, end_date)
        expense = self.db.get_total_by_type('expense', start_date, end_date)
        
        if income == 0:
            return 0
        
        savings_rate = ((income - expense) / income) * 100
        return round(savings_rate, 2)
    
    def get_spending_rate(self, start_date=None, end_date=None):
        """
        Calculate spending rate: Total Expenses / Total Income * 100
        Returns percentage
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        income = self.db.get_total_by_type('income', start_date, end_date)
        expense = self.db.get_total_by_type('expense', start_date, end_date)
        
        if income == 0:
            return 0
        
        spending_rate = (expense / income) * 100
        return round(spending_rate, 2)
    
    def get_net_cash_flow(self, start_date=None, end_date=None):
        """
        Calculate net cash flow: Income - Expenses
        Returns amount
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        income = self.db.get_total_by_type('income', start_date, end_date)
        expense = self.db.get_total_by_type('expense', start_date, end_date)
        
        return round(income - expense, 2)
    
    def get_expense_breakdown(self, start_date=None, end_date=None):
        """
        Get expense breakdown by category with percentages
        Returns list of dicts with category, amount, percentage, count
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        breakdown = self.db.get_category_breakdown('expense', start_date, end_date)
        total_expense = sum(item['total'] for item in breakdown)
        
        if total_expense == 0:
            return []
        
        for item in breakdown:
            item['percentage'] = round((item['total'] / total_expense) * 100, 2)
        
        return breakdown
    
    def get_income_breakdown(self, start_date=None, end_date=None):
        """
        Get income breakdown by category with percentages
        Returns list of dicts with category, amount, percentage, count
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        breakdown = self.db.get_category_breakdown('income', start_date, end_date)
        total_income = sum(item['total'] for item in breakdown)
        
        if total_income == 0:
            return []
        
        for item in breakdown:
            item['percentage'] = round((item['total'] / total_income) * 100, 2)
        
        return breakdown
    
    def get_budget_adherence(self, start_date=None, end_date=None):
        """
        Calculate budget vs actual spending for each category
        Returns list of dicts with category, budget, actual, remaining, percentage_used
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        budgets = self.db.get_all_budgets()
        expense_breakdown = self.db.get_category_breakdown('expense', start_date, end_date)
        
        # Create lookup dict for expenses
        expense_dict = {item['category']: item['total'] for item in expense_breakdown}
        
        adherence = []
        for budget in budgets:
            category = budget['category']
            budget_limit = budget['monthly_limit']
            actual = expense_dict.get(category, 0)
            remaining = budget_limit - actual
            percentage_used = (actual / budget_limit * 100) if budget_limit > 0 else 0
            
            adherence.append({
                'category': category,
                'budget': budget_limit,
                'actual': round(actual, 2),
                'remaining': round(remaining, 2),
                'percentage_used': round(percentage_used, 2),
                'over_budget': actual > budget_limit
            })
        
        return sorted(adherence, key=lambda x: x['percentage_used'], reverse=True)
    
    def get_emergency_fund_progress(self, target_amount, start_date=None, end_date=None):
        """
        Calculate emergency fund progress
        Returns dict with current_amount, target_amount, percentage, remaining
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        # Calculate total savings (cumulative net cash flow)
        income = self.db.get_total_by_type('income', start_date, end_date)
        expense = self.db.get_total_by_type('expense', start_date, end_date)
        current_amount = income - expense
        
        if current_amount < 0:
            current_amount = 0
        
        percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
        remaining = target_amount - current_amount
        
        return {
            'current_amount': round(current_amount, 2),
            'target_amount': target_amount,
            'percentage': round(percentage, 2),
            'remaining': round(remaining, 2)
        }
    
    def get_debt_to_income_ratio(self, total_debt, start_date=None, end_date=None):
        """
        Calculate debt-to-income ratio: (Total Debt / Total Income) * 100
        Returns percentage
        """
        if not start_date or not end_date:
            start_date, end_date = get_current_month_range()
        
        income = self.db.get_total_by_type('income', start_date, end_date)
        
        if income == 0:
            return 0
        
        ratio = (total_debt / income) * 100
        return round(ratio, 2)
    
    def get_savings_trend(self, months=6):
        """
        Get savings trend over specified number of months
        Returns list of dicts with month, income, expense, savings
        """
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months-1)
        
        # Get all months in range
        month_list = get_date_range_months(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        trend = []
        for year_month in month_list:
            summary = self.db.get_monthly_summary(year_month)
            income = summary.get('income', 0)
            expense = summary.get('expense', 0)
            savings = income - expense
            
            trend.append({
                'month': year_month,
                'income': round(income, 2),
                'expense': round(expense, 2),
                'savings': round(savings, 2)
            })
        
        return trend
    
    def get_spending_trend(self, months=6):
        """
        Get spending trend by category over specified months
        Returns dict with categories as keys and list of monthly amounts
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months-1)
        
        month_list = get_date_range_months(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # Get all expense categories
        categories = [cat['name'] for cat in self.db.get_categories('expense')]
        
        trend = {cat: [] for cat in categories}
        
        for year_month in month_list:
            # Get first and last day of month
            year, month = map(int, year_month.split('-'))
            month_start = f"{year_month}-01"
            
            if month == 12:
                month_end = f"{year + 1}-01-01"
            else:
                month_end = f"{year}-{month + 1:02d}-01"
            
            breakdown = self.db.get_category_breakdown('expense', month_start, month_end)
            breakdown_dict = {item['category']: item['total'] for item in breakdown}
            
            for cat in categories:
                trend[cat].append({
                    'month': year_month,
                    'amount': round(breakdown_dict.get(cat, 0), 2)
                })
        
        return trend
    
    def check_budget_alerts(self, threshold=80):
        """
        Check for budget alerts (categories exceeding threshold percentage)
        Returns list of categories over threshold
        """
        start_date, end_date = get_current_month_range()
        adherence = self.get_budget_adherence(start_date, end_date)
        
        alerts = []
        for item in adherence:
            if item['percentage_used'] >= threshold:
                alerts.append({
                    'category': item['category'],
                    'percentage_used': item['percentage_used'],
                    'over_budget': item['over_budget'],
                    'actual': item['actual'],
                    'budget': item['budget']
                })
        
        return alerts
    
    def get_dashboard_summary(self):
        """
        Get comprehensive dashboard summary for current month
        Returns dict with all key metrics
        """
        start_date, end_date = get_current_month_range()
        
        income = self.db.get_total_by_type('income', start_date, end_date)
        expense = self.db.get_total_by_type('expense', start_date, end_date)
        
        return {
            'income': round(income, 2),
            'expense': round(expense, 2),
            'net_cash_flow': round(income - expense, 2),
            'savings_rate': self.get_savings_rate(start_date, end_date),
            'spending_rate': self.get_spending_rate(start_date, end_date),
            'transaction_count': len(self.db.get_all_transactions(start_date, end_date)),
            'budget_alerts': len(self.check_budget_alerts()),
            'top_expense_category': self._get_top_category('expense', start_date, end_date),
            'top_income_source': self._get_top_category('income', start_date, end_date)
        }
    
    def _get_top_category(self, trans_type, start_date, end_date):
        """Helper to get top category by amount"""
        breakdown = self.db.get_category_breakdown(trans_type, start_date, end_date)
        if breakdown:
            return breakdown[0]['category']
        return "N/A"
