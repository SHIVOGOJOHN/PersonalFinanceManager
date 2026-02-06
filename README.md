# Personal Finance Manager

A fully functional Android personal finance management application built with Kivy and Buildozer, featuring offline-first architecture with cloud backup via FastAPI and MySQL.

**Currency**: Kenyan Shillings (KES)

## Features

### 📊 Dashboard
- Real-time financial overview
- Current month income and expenses
- Savings rate and spending rate
- Recent transactions list
- Quick navigation to all features

### 💰 Transactions
- Add, edit, and delete transactions
- Income and expense categorization
- Date and amount tracking
- Description notes
- Searchable transaction history

### 📈 Metrics & Analysis
- Savings rate calculation
- Spending rate tracking
- Net cash flow monitoring
- Expense breakdown by category
- Budget adherence tracking
- Visual progress bars and indicators

### ☁️ Cloud Backup & Restore
- Manual backup to MySQL cloud database
- Restore data from cloud
- Incremental sync for new transactions
- Network connectivity detection
- Sync status tracking

## Technology Stack

- **Frontend**: Kivy (Python)
- **Local Database**: SQLite
- **Backend API**: FastAPI
- **Cloud Database**: MySQL (Aiven)
- **Build Tool**: Buildozer

## Project Structure

```
Android/
├── main.py                 # Main Kivy application
├── config.py              # Configuration settings
├── database.py            # SQLite database handler
├── metrics.py             # Financial metrics calculator
├── sync_manager.py        # Cloud sync manager
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── buildozer.spec         # Buildozer configuration
├── screens/               # UI screens
│   ├── __init__.py
│   ├── dashboard.py       # Dashboard screen
│   ├── transactions.py    # Transactions screen
│   ├── metrics.py         # Metrics screen
│   └── backup.py          # Backup screen
└── backend/               # FastAPI backend
    ├── main.py            # API server
    └── requirements.txt   # Backend dependencies
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- For Android build: Linux/WSL with Buildozer dependencies

### Desktop Testing (Windows/Mac/Linux)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Test all features**:
   - Add transactions
   - View metrics
   - Check dashboard updates
   - (Backup/restore requires backend running)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create .env file**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your MySQL credentials:
   ```env
   DB_HOST=your-mysql-host.com
   DB_PORT=19274
   DB_USER=your-username
   DB_PASSWORD=your-password
   DB_NAME=defaultdb
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**:
   ```bash
   python main.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API documentation**:
   - Open browser to `http://localhost:8000/docs`
   - Test endpoints interactively

6. **Deploy to Render** (recommended):
   - See [backend/README.md](backend/README.md) for detailed deployment instructions
   - Push backend to GitHub
   - Create Web Service on Render
   - Add environment variables in Render dashboard

7. **Update API URL in config.py**:
   - For local testing: `http://localhost:8000`
   - For production: `https://your-app.onrender.com`

### Building Android APK

#### On Linux/WSL:

1. **Install Buildozer**:
   ```bash
   pip install buildozer
   ```

2. **Install Android dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

3. **Build debug APK**:
   ```bash
   buildozer android debug
   ```

4. **First build takes 30-60 minutes** (downloads SDK, NDK, and compiles dependencies)

5. **Find APK**:
   ```bash
   ls bin/*.apk
   ```

6. **Install on Android device**:
   ```bash
   buildozer android deploy run
   ```
   
   Or manually transfer the APK from `bin/` folder to your device

#### Build Options:

- **Debug APK**: `buildozer android debug`
- **Release APK**: `buildozer android release`
- **Deploy to device**: `buildozer android deploy`
- **Run on device**: `buildozer android deploy run`
- **Clean build**: `buildozer android clean`

## Configuration

### API Endpoint (config.py)

```python
# Change this to your deployed backend URL
API_BASE_URL = "http://localhost:8000"  # Local testing
# API_BASE_URL = "https://your-backend.com"  # Production
```

### MySQL Credentials

✅ **Credentials are now stored in environment variables**

1. Local development: Use `.env` file in `backend/` directory
2. Production (Render): Add environment variables in dashboard
3. Never commit `.env` file to git (already in `.gitignore`)

See [backend/README.md](backend/README.md) for setup instructions.

### Default Categories

Edit `config.py` to customize income and expense categories:

```python
DEFAULT_CATEGORIES = {
    "income": ["Salary", "Freelance", ...],
    "expense": ["Food & Dining", "Transportation", ...]
}
```

### Budget Limits

Edit `config.py` to set default monthly budgets:

```python
DEFAULT_MONTHLY_BUDGET = {
    "Food & Dining": 500,
    "Transportation": 200,
    ...
}
```

## Usage Guide

### Adding Transactions

1. Navigate to **Transactions** screen
2. Tap **+ Add Transaction**
3. Select type (Income/Expense)
4. Choose category
5. Enter amount and date
6. Add description (optional)
7. Tap **Save**

### Viewing Metrics

1. Navigate to **Metrics** screen
2. View key metrics for current month
3. Check expense breakdown
4. Monitor budget adherence
5. Identify overspending categories

### Cloud Backup

1. Navigate to **Backup** screen
2. Check network connectivity status
3. Tap **Backup to Cloud** to upload all data
4. Tap **Sync Unsynced Transactions** for incremental backup
5. Tap **Restore from Cloud** to download data

### Restoring Data

1. Install app on new device
2. Navigate to **Backup** screen
3. Tap **Restore from Cloud**
4. All transactions, budgets, and categories will be restored

## Financial Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Savings Rate** | `(Income - Expenses) / Income × 100` | Higher is better (>20% is good) |
| **Spending Rate** | `Expenses / Income × 100` | Lower is better (<80% is good) |
| **Net Cash Flow** | `Income - Expenses` | Positive means saving money |
| **Budget Adherence** | `Actual / Budget × 100` | <100% means under budget |

## Troubleshooting

### Desktop App Issues

**App won't start**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**Database errors**:
- Delete `finance.db` file and restart app
- Database will be recreated automatically

### Backend Issues

**Connection refused**:
- Ensure backend is running: `cd backend && python main.py`
- Check firewall settings
- Verify port 8000 is not in use

**MySQL connection failed**:
- Check internet connectivity
- Verify MySQL credentials in `backend/main.py`
- Check MySQL server status

### Buildozer Issues

**Build fails**:
- Run `buildozer android clean`
- Delete `.buildozer` folder
- Try again: `buildozer android debug`

**Missing dependencies**:
- Install required system packages (see Building Android APK section)
- Update buildozer: `pip install --upgrade buildozer`

**APK crashes on Android**:
- Check `adb logcat` for errors
- Ensure all permissions are granted
- Verify API URL is accessible from mobile network

## Deployment

### Backend Deployment Options

1. **Heroku**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

2. **Railway**:
   - Connect GitHub repository
   - Deploy automatically

3. **DigitalOcean App Platform**:
   - Create new app
   - Connect repository
   - Deploy

4. **AWS EC2**:
   - Launch instance
   - Install dependencies
   - Run with systemd service

### Update API URL

After deploying backend, update `config.py`:

```python
API_BASE_URL = "https://your-deployed-backend.com"
```

Then rebuild APK:

```bash
buildozer android clean
buildozer android debug
```

## Security Considerations

✅ **Good Practices**:
- MySQL credentials stored only in backend
- HTTPS recommended for production
- Local data stored in SQLite (encrypted storage optional)

⚠️ **Recommendations**:
- Use environment variables for credentials
- Implement user authentication
- Enable SSL/TLS for MySQL connection
- Add API rate limiting
- Implement data encryption at rest

## Future Enhancements

- [ ] Data export (CSV/PDF)
- [ ] Charts and visualizations (graphs)
- [ ] Recurring transactions
- [ ] Multi-currency support
- [ ] Receipt photo attachments
- [ ] Biometric authentication
- [ ] Dark mode
- [ ] Widgets for home screen
- [ ] Notifications for budget alerts

## License

This project is for personal use. Feel free to modify and extend as needed.

## Support

For issues or questions:
1. Check this README
2. Review error logs
3. Test on desktop before building APK
4. Check Kivy and Buildozer documentation

## Credits

- Built with [Kivy](https://kivy.org/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- Database hosted on [Aiven](https://aiven.io/)
- Packaged with [Buildozer](https://buildozer.readthedocs.io/)

---

**Version**: 0.1  
**Last Updated**: February 2026  
**Status**: Fully Functional ✅
