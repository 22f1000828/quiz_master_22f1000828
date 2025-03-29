# Quiz Management System

This is a Flask-based web application for managing quizzes, subjects, chapters, and users. It includes features for both administrators and regular users.

## Features

### Admin Features
- Create and manage subjects, chapters, quizzes, and questions.
- View all subjects and chapters in the admin dashboard.

### User Features
- Register and log in to the system.
- View available quizzes and take them.
- View scores and quiz history in the user dashboard.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database and create demo data:
   ```bash
   python demo.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open the application in your browser:
   ```
   http://127.0.0.1:5000
   ```

## Demo Credentials

### Admin
- **Username**: `admin@demo.com`
- **Password**: `admin123`

### User
- Register a new user via the registration page.

## Project Structure

```
project/
│
├── app.py                 # Main application entry point
├── applications/
│   ├── __init__.py        # Application factory (if applicable)
│   ├── models.py          # Database models
│   ├── routes.py          # Application routes
│   └── templates/         # HTML templates
│
├
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Key Files

- **`app.py`**: Initializes the Flask app and registers routes.
- **`models.py`**: Contains database models for users, subjects, chapters, quizzes, and scores.
- **`routes.py`**: Defines application routes using Flask Blueprints.
- **`demo.py`**: Populates the database with demo data for testing.

## Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, Jinja2 Templates
- **Environment**: Python 3.x

## Future Enhancements

- Add password hashing for user authentication.
- Implement pagination for large datasets.
- Add support for quiz analytics and reporting.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.