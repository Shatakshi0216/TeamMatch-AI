import random
# Imports Python's built-in tool for generating random numbers and making random selections.
import pandas as pd
# used to create and manipulate tabular data (DataFrames).
import sqlite3
# Imports the library needed to interact with SQLite databases.
import os
# Imports the Operating System library, used here to create folders and delete files.
from database import init_db, get_db_connection
# Imports two specific functions from your local database.py file to set up and connect to your database.

def generate_students(n=60):
    """Generates synthetic student profiles belonging to 4 main tech archetypes."""
    names = [
        "Aarav Mehta", "Aditi Sharma", "Akash Patel", "Ananya Iyer", "Amit Verma", 
        "Anjali Rao", "Arjun Nair", "Devendra Singh", "Divya Kulkarni", "Gaurav Joshi",
        "Ishaan Gupta", "Karan Johar", "Kavita Reddy", "Manish Pandey", "Meera Sen",
        "Nikhil Deshmukh", "Nisha Saxena", "Pooja Hegde", "Pranav Shah", "Priya Mishra",
        "Rahul Dravid", "Rohan Gavaskar", "Siddharth Malhotra", "Sneha Patil", "Tarun Khanna",
        "Vikram Seth", "Yash Birla", "Aishwarya Roy", "Deepak Padukone", "Hrithik Roshan",
        "Kareena Kapoor", "Ranbir Kapoor", "Salman Khan", "Shahrukh Khan", "Varun Dhawan",
        "Alia Bhatt", "Katrina Kaif", "Priyanka Chopra", "Ranveer Singh", "Tiger Shroff",
        "Sanjay Dutt", "Sunny Deol", "Bobby Deol", "Juhi Chawla", "Madhuri Dixit",
        "Kajol Devgan", "Karisma Kapoor", "Rani Mukerji", "Preity Zinta", "Saif Ali Khan"
    ]
    # In case we need more names than 50, cycle or combine
    while len(names) < n:
        names.append(f"Developer {len(names) + 1}")
    
    # Randomizes the order of the names list so the results aren't identical every time.
    random.shuffle(names)
    
    experience_levels = ["Beginner", "Intermediate", "Advanced"]
    # A dictionary that maps a specific archetype (like "AI/ML") to a specific string of text representing their technical stack.
    skills_map = {
        "AI/ML": "Python, PyTorch, Scikit-learn, TensorFlow",
        "Frontend": "React, HTML, CSS, Figma, Next.js",
        "Backend": "Python, Node.js, Express, SQL, Docker",
        "Fullstack": "React, Node.js, SQLite, WebDev, Tailwind"
    }

    students = []
    for i in range(n):
        name = names[i]
        # Choose archetype
        archetype = random.choice(["AI/ML", "Frontend", "Backend", "Fullstack"])
        # Randomly assigns one of the four tech focuses to the student.
        exp = random.choices(experience_levels, weights=[0.25, 0.50, 0.25])[0]
        # Assigns an experience level, but uses weights (25% chance for Beginner, 
        # 50% for Intermediate, 25% for Advanced) instead of an equal split.
        
        # Base stats between 2 and 6
        stats = {s: random.randint(2, 6) for s in ["dsa", "backend", "frontend", "ml", "uiux"]}
        
        # Boost based on archetype
        if archetype == "AI/ML":
            stats["ml"] = random.randint(7, 10)
            stats["dsa"] = random.randint(7, 10)
            skills = skills_map["AI/ML"]
        elif archetype == "Frontend":
            stats["frontend"] = random.randint(7, 10)
            stats["uiux"] = random.randint(7, 10)
            skills = skills_map["Frontend"]
        elif archetype == "Backend":
            stats["backend"] = random.randint(7, 10)
            stats["dsa"] = random.randint(7, 10)
            skills = skills_map["Backend"]
        else: # Fullstack
            stats["backend"] = random.randint(6, 9)
            stats["frontend"] = random.randint(6, 9)
            stats["dsa"] = random.randint(5, 8)
            skills = skills_map["Fullstack"]
            
        comm = random.randint(4, 10)
        proj = random.randint(1, 6)
        hacks = random.randint(0, 4)
        avail = random.choice([10, 15, 20, 25, 30, 35])
        
        students.append({
            "name": name,
            "dsa": stats["dsa"],
            "backend": stats["backend"],
            "frontend": stats["frontend"],
            "ml": stats["ml"],
            "uiux": stats["uiux"],
            "experience_level": exp,
            "projects_count": proj,
            "hackathons_count": hacks,
            "availability_hours": avail,
            "skills": skills,
            "communication": comm,
            "cluster_id": -1
        })
    return students

def generate_historical_teams(students, n_teams=300):
    """
    Generates simulated team combinations and calculates compatibility success labels
    to train a Decision Tree Classifier.
    """
    team_data = []
    
    for _ in range(n_teams):
        # Pick 2 to 4 random members
        team_size = random.randint(2, 4)
        members = random.sample(students, team_size)
        
        # Extract features
        max_dsa = max(m["dsa"] for m in members)
        max_backend = max(m["backend"] for m in members)
        max_frontend = max(m["frontend"] for m in members)
        max_ml = max(m["ml"] for m in members)
        max_uiux = max(m["uiux"] for m in members)
        
        mean_comm = sum(m["communication"] for m in members) / len(members)
        min_avail = min(m["availability_hours"] for m in members)
        
        # Determine success label based on coverage, communication, availability
        # We need at least basic backend, frontend, and dsa coverage, plus reasonable comm and availability
        has_backend = max_backend >= 6
        has_frontend = max_frontend >= 6
        has_dsa = max_dsa >= 5
        good_comm = mean_comm >= 6.0
        no_bottleneck = min_avail >= 10
        
        # Compute scoring heuristic
        score = (0.2 * max_backend + 0.2 * max_frontend + 0.1 * max_dsa + 0.25 * mean_comm + 0.25 * (min_avail / 5))
        
        # Core rules
        if has_backend and has_frontend and has_dsa and good_comm and no_bottleneck:
            success_chance = 0.85
        elif not has_backend or not has_frontend:
            success_chance = 0.15  # critical skill missing
        else:
            success_chance = 0.45
            
        # Add random chance
        label = 1 if random.random() < success_chance else 0
        
        team_data.append({
            "max_dsa": max_dsa,
            "max_backend": max_backend,
            "max_frontend": max_frontend,
            "max_ml": max_ml,
            "max_uiux": max_uiux,
            "mean_communication": round(mean_comm, 2),
            "min_availability": min_avail,
            "team_size": team_size,
            "success": label
        })
        
    return pd.DataFrame(team_data)

def seed_database():
    """Seeds database with synthetic developers and saves historical team CSV."""
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if students exist, if so clear them first for fresh seed
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
    cursor.execute("DELETE FROM teams")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='teams'")
    conn.commit()
    conn.close()
    
    print("Generating profiles...")
    students = generate_students(60)
    
    # Save to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    for s in students:
        cursor.execute("""
        INSERT INTO students (
            name, dsa, backend, frontend, ml, uiux, 
            experience_level, projects_count, hackathons_count, 
            availability_hours, skills, communication, cluster_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s['name'], s['dsa'], s['backend'], s['frontend'], s['ml'], s['uiux'],
            s['experience_level'], s['projects_count'], s['hackathons_count'],
            s['availability_hours'], s['skills'], s['communication'], s['cluster_id']
        ))
    conn.commit()
    conn.close()
    print("Successfully seeded 60 developer profiles in SQLite database!")
    
    # Generate historical teams for model training
    print("Generating historical team match trials...")
    historical_df = generate_historical_teams(students, 300)
    
    os.makedirs("data", exist_ok=True)
    historical_df.to_csv("data/historical_teams.csv", index=False)
    print("Successfully saved 300 historical team trials to 'data/historical_teams.csv'!")



if __name__ == "__main__":
    
    seed_database()
