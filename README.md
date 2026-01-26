# Hanoi Relocation Dashboard
[Live Demo](https://mild-karee-alinursu-e614120e.koyeb.app/)

A Flask web application designed to help track progress toward relocating to Hanoi, Vietnam. This dashboard monitors learning goals (Python programming and Vietnamese language), freelance income, financial milestones, and provides a structured learning path.

## Features

### 📊 Dashboard
- **Income Gap Calculator**: Track monthly income targets and calculate remaining amount needed
- **Quick Stats**: Overview of Python hours, Vietnamese minutes, and freelance earnings
- **Progress Tracking**: Visual progress bars for weekly learning goals
- **Milestones**: Track important goals and deadlines
- **Notes**: Store research and important information

### 📅 Today View
- Daily activity tracking
- Quick entry for learning sessions and freelance projects
- Motivational messages
- Current week progress summary

### 🎓 Learning Path
- Structured skill progression through multiple phases
- Track completed skills and projects
- Visual roadmap for Python learning journey

### ⚙️ Settings
- Configure target relocation date
- Set income and learning goals
- Manage savings and monthly expenses
- Currency preferences
- GitHub username integration

## Project Structure

```
hanoi-relocation/
├── app/
│   ├── __init__.py          # Flask app factory
│   └── routes/
│       ├── __init__.py
│       ├── main.py          # Main page routes
│       └── api.py           # API endpoints for data operations
├── static/
│   ├── css/
│   │   └── styles.css       # Application styles
│   └── js/
│       ├── api.js           # API client functions
│       ├── auth.js          # Authentication utilities
│       ├── currency.js      # Currency conversion
│       ├── github-api.js    # GitHub integration
│       └── nav.js           # Navigation utilities
├── templates/
│   └── hanoi-relocation/
│       ├── index.html       # Main dashboard
│       ├── today.html       # Today's view
│       ├── learning-path.html  # Learning path tracker
│       └── settings.html    # Settings page
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd hanoi-relocation
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

Start the Flask development server:

```bash
python run.py
```

The application will be available at `http://localhost:5001`

### Default Configuration

The application comes with default settings:
- **Target Date**: October 31, 2026
- **Income Target**: 7,500 RON/month
- **Python Weekly Target**: 8 hours
- **Vietnamese Weekly Target**: 7 hours
- **Initial Savings**: 27,500 RON
- **Monthly Burn Rate**: 3,000 RON

You can modify these in the Settings page after starting the application.

## API Endpoints

The application provides RESTful API endpoints under `/api`:

### Settings
- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings

### Learning Sessions
- `GET /api/vietnamese-sessions` - Get Vietnamese learning sessions
- `POST /api/vietnamese-sessions` - Add new Vietnamese session
- `DELETE /api/vietnamese-sessions/<id>` - Delete session

- `GET /api/python-sessions` - Get Python learning sessions
- `POST /api/python-sessions` - Add new Python session
- `DELETE /api/python-sessions/<id>` - Delete session

### Freelance Projects
- `GET /api/freelance-projects` - Get freelance projects
- `POST /api/freelance-projects` - Add new project
- `DELETE /api/freelance-projects/<id>` - Delete project

### Milestones
- `GET /api/milestones` - Get all milestones
- `POST /api/milestones` - Create new milestone
- `PUT /api/milestones/<id>` - Update milestone
- `DELETE /api/milestones/<id>` - Delete milestone

### Notes
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create new note
- `PUT /api/notes/<id>` - Update note
- `DELETE /api/notes/<id>` - Delete note

### Learning Path
- `GET /api/learning-path` - Get learning path skills
- `PUT /api/learning-path/<skill_id>` - Update skill status

## Data Storage

**Note**: This is a prototype application. All data is stored in-memory and will be reset when the server restarts. For production use, consider implementing a database (SQLite, PostgreSQL, etc.).

## Technologies Used

- **Backend**: Flask 3.0+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **CORS**: flask-cors for API access
- **Styling**: Custom CSS with modern design

## Development

### Adding New Features

1. **Backend Routes**: Add new routes in `app/routes/main.py` or `app/routes/api.py`
2. **Frontend**: Update templates in `templates/hanoi-relocation/`
3. **Styling**: Modify `static/css/styles.css`
4. **JavaScript**: Add functionality in `static/js/`

### Code Structure

- **Blueprints**: The app uses Flask blueprints for route organization
- **API Design**: RESTful API with JSON responses
- **Client-Side**: Vanilla JavaScript for API interactions

## Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] User authentication and multi-user support
- [ ] Data persistence across server restarts
- [ ] Export/import functionality
- [ ] Advanced analytics and reporting
- [ ] Mobile-responsive improvements
- [ ] Dark mode support

## License

This project is for personal use.

## Contributing

This is a personal project, but suggestions and feedback are welcome!

---

**Built with ❤️ for tracking progress toward the Hanoi relocation goal**
