import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "teammatch.db"))

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionaries
    return conn

def init_db():
    """Initializes the database tables if they do not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT,
        dsa INTEGER NOT NULL,
        backend INTEGER NOT NULL,
        frontend INTEGER NOT NULL,
        ml INTEGER NOT NULL,
        uiux INTEGER NOT NULL,
        experience_level TEXT NOT NULL,
        projects_count INTEGER DEFAULT 0,
        hackathons_count INTEGER DEFAULT 0,
        availability_hours INTEGER DEFAULT 15,
        skills TEXT,
        communication INTEGER NOT NULL,
        cluster_id INTEGER DEFAULT -1,
        university TEXT DEFAULT '',
        github_url TEXT DEFAULT '',
        linkedin_url TEXT DEFAULT '',
        project_interests TEXT DEFAULT '',
        past_hackathon_name TEXT DEFAULT '',
        past_hackathon_project TEXT DEFAULT '',
        past_hackathon_desc TEXT DEFAULT '',
        preferred_role TEXT DEFAULT 'Frontend Developer',
        availability TEXT DEFAULT 'Looking for team'
    )
    """)
    
    # Add email and password_hash columns dynamically if database already exists
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN password_hash TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN university TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN github_url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN linkedin_url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN project_interests TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN past_hackathon_name TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN past_hackathon_project TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN past_hackathon_desc TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN preferred_role TEXT DEFAULT 'Frontend Developer'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN availability TEXT DEFAULT 'Looking for team'")
    except sqlite3.OperationalError:
        pass

    # Create messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message_text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
        
    # Create teams table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT NOT NULL,
        description TEXT,
        health_score REAL DEFAULT 0.0,
        members TEXT NOT NULL, -- Comma-separated student IDs (e.g. "1,3,5")
        predicted_compatibility TEXT DEFAULT 'N/A',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create training metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_metrics (
        metric_name TEXT PRIMARY KEY,
        metric_value REAL NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def get_all_students():
    """Fetches all student profiles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_email(email):
    """Fetches a student profile by their email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_student(s):
    """Registers a new student profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO students (
        name, email, password_hash, dsa, backend, frontend, ml, uiux, 
        experience_level, projects_count, hackathons_count, 
        availability_hours, skills, communication, cluster_id,
        university, github_url, linkedin_url, project_interests,
        past_hackathon_name, past_hackathon_project, past_hackathon_desc,
        preferred_role, availability
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        s['name'], s.get('email'), s.get('password_hash'), s['dsa'], s['backend'], s['frontend'], s['ml'], s['uiux'],
        s['experience_level'], s.get('projects_count', 0), s.get('hackathons_count', 0),
        s.get('availability_hours', 15), s.get('skills', 'Generalist'), s['communication'], s.get('cluster_id', -1),
        s.get('university', ''), s.get('github_url', ''), s.get('linkedin_url', ''), s.get('project_interests', ''),
        s.get('past_hackathon_name', ''), s.get('past_hackathon_project', ''), s.get('past_hackathon_desc', ''),
        s.get('preferred_role', 'Frontend Developer'), s.get('availability', 'Looking for team')
    ))
    conn.commit()
    conn.close()

def update_student(student_id, s):
    """Updates an existing student profile in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE students SET 
        name = ?, dsa = ?, backend = ?, frontend = ?, ml = ?, uiux = ?, 
        experience_level = ?, projects_count = ?, hackathons_count = ?, 
        availability_hours = ?, skills = ?, communication = ?,
        university = ?, github_url = ?, linkedin_url = ?, project_interests = ?,
        past_hackathon_name = ?, past_hackathon_project = ?, past_hackathon_desc = ?,
        preferred_role = ?, availability = ?
    WHERE student_id = ?
    """, (
        s['name'], s['dsa'], s['backend'], s['frontend'], s['ml'], s['uiux'],
        s['experience_level'], s['projects_count'], s['hackathons_count'],
        s['availability_hours'], s['skills'], s['communication'],
        s.get('university', ''), s.get('github_url', ''), s.get('linkedin_url', ''), s.get('project_interests', ''),
        s.get('past_hackathon_name', ''), s.get('past_hackathon_project', ''), s.get('past_hackathon_desc', ''),
        s.get('preferred_role', 'Frontend Developer'), s.get('availability', 'Looking for team'),
        student_id
    ))
    conn.commit()
    conn.close()

def update_student_cluster(student_id, cluster_id):
    """Updates the K-Means cluster assignment for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET cluster_id = ? WHERE student_id = ?", (cluster_id, student_id))
    conn.commit()
    conn.close()

def get_all_teams():
    """Fetches all saved teams."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY created_at DESC")
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams

def add_team(t):
    """Saves a new team roster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO teams (
        team_name, description, health_score, members, predicted_compatibility
    ) VALUES (?, ?, ?, ?, ?)
    """, (
        t['team_name'], t.get('description', ''), t.get('health_score', 0.0),
        t['members'], t.get('predicted_compatibility', 'N/A')
    ))
    conn.commit()
    conn.close()

def delete_team(team_id):
    """Deletes a team roster by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
    conn.commit()
    conn.close()

def save_metric(name, value):
    """Saves or updates a model evaluation metric."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO training_metrics (metric_name, metric_value, updated_at) 
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(metric_name) DO UPDATE SET 
        metric_value = excluded.metric_value, 
        updated_at = CURRENT_TIMESTAMP
    """, (name, value))
    conn.commit()
    conn.close()

def get_all_metrics():
    """Fetches all model evaluation metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM training_metrics")
    metrics = {row['metric_name']: row['metric_value'] for row in cursor.fetchall()}
    conn.close()
    return metrics

def add_message(sender_id, receiver_id, message_text):
    """Saves a new chat message to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO messages (sender_id, receiver_id, message_text)
    VALUES (?, ?, ?)
    """, (sender_id, receiver_id, message_text))
    conn.commit()
    conn.close()

def get_messages(user1_id, user2_id):
    """Retrieves message history between two candidates."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM messages 
    WHERE (sender_id = ? AND receiver_id = ?) 
       OR (sender_id = ? AND receiver_id = ?)
    ORDER BY timestamp ASC
    """, (user1_id, user2_id, user2_id, user1_id))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages
