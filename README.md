# RollIn

RollIn is a Streamlit application for classroom attendance management with
course setup, student enrollment, face-profile registration, live attendance
capture, history, and analytics.

## Features

- Secure login with hashed password storage
- Course and student management
- Student enrollment and unenrollment
- Face-profile registration with webcam capture
- Live attendance scanning with recognition feedback
- Attendance history export
- Basic attendance analytics export

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the app with `streamlit run app.py`.

## Project structure

- `app.py`: app entry point and navigation shell
- `views/`: Streamlit pages
- `database.py`: SQLite schema and data operations
- `face_utils.py`: face embedding and recognition helpers
- `camera_utils.py`: webcam discovery helpers
- `assets/styles.css`: shared application styling

## Notes

- Local biometric assets and the SQLite database are ignored by Git.
- Streamlit theme settings are stored in `.streamlit/config.toml`.
- Default development users are seeded by the database initialization layer.
