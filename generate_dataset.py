# --- 1. Grabbing the Tools ---
import random          # Lets us roll the dice and pick random things
import pandas as pd    # Lets us organize data into clean tables (like Excel)
import sqlite3         # Lets Python talk to your local database file
import os              # Lets Python interact with your computer (like making folders)

# Grabs the setup functions you wrote in your other file, database.py
from database import init_db, get_db_connection


# --- 2. Manufacturing the Fake Users ---
def generate_students(n=200):
    # This is our factory line. If we don't give it a number, it makes 200 fake users.
    
    first_names = [
        "Aarav", "Aditi", "Akash", "Ananya", "Amit", "Anjali", "Arjun", "Devendra", "Divya", "Gaurav",
        "Ishaan", "Kavita", "Manish", "Meera", "Nikhil", "Nisha", "Pranav", "Priya", "Sneha", "Tarun",
        "Vikram", "Rajesh", "Sunita", "Ramesh", "Sandeep", "Vivek", "Neha", "Manoj", "Ritu", "Swati",
        "Harish", "Kiran", "Deepak", "Sanjay", "Abhinav", "Jyoti", "Suresh", "Vijay", "Preeti", "Rohan",
        "Shalini", "Vinay", "Shreya", "Mohit", "Rashmi", "Kartik", "Tanvi", "Vikas", "Pooja", "Yash",
        "Rahul", "Ajay", "Amrita", "Vinod", "Anil", "Sunil", "Deepa", "Dinesh", "Geeta", "Gopal",
        "Hema", "Jitendra", "Kishore", "Lalita", "Madan", "Maya", "Mahesh", "Naresh", "Prem", "Sarita",
        "Sarika", "Anupam", "Ketan", "Payal", "Rakesh", "Sonia", "Tarika", "Umesh", "Varun", "Yogesh"
    ]
    last_names = [
        "Mehta", "Sharma", "Patel", "Iyer", "Verma", "Rao", "Nair", "Singh", "Kulkarni", "Joshi",
        "Gupta", "Reddy", "Pandey", "Sen", "Deshmukh", "Saxena", "Shah", "Mishra", "Patil", "Khanna",
        "Seth", "Kumar", "Yadav", "Tripathy", "Deshpande", "Choudhary", "Prasad", "Bose", "Das", "Vardhan",
        "Jha", "Acharya", "Chakraborty", "Bannerjee", "Pillai", "Menon", "Shenoy", "Hegde", "Bhat", "Prabhu",
        "Gowda", "Naidu", "Sinha", "Trivedi", "Pathak", "Dubey", "Dwivedi", "Chatterjee", "Dutt", "Malhotra"
    ]
    
    # Generate all unique combinations (80 * 50 = 4000 possible names)
    all_combinations = [f"{first} {last}" for first in first_names for last in last_names]
    random.shuffle(all_combinations)
    
    # Select the first n names
    names = all_combinations[:n]
    
    while len(names) < n:
        names.append(f"Developer {len(names) + 1}")
        
    experience_levels = ["Beginner", "Intermediate", "Advanced"]
    
    # A cheat sheet. If someone is assigned a major (like AI/ML), this gives them the right text labels.
    skills_map = {
        "AI/ML": "Python, PyTorch, Scikit-learn, TensorFlow",
        "Frontend": "React, HTML, CSS, Figma, Next.js",
        "Backend": "Python, Node.js, Express, SQL, Docker",
        "Fullstack": "React, Node.js, SQLite, WebDev, Tailwind"
    }

    students = [] # An empty bucket to hold our finished fake people
    
    # Loop 60 times to build each student
    for i in range(n):
        name = names[i] # Grab a unique name from our shuffled deck
        
        # Randomly assign this student a major/focus area
        archetype = random.choice(["AI/ML", "Frontend", "Backend", "Fullstack"])
        
        # Randomly pick an experience level. The odds are rigged: 50% chance they are Intermediate.
        exp = random.choices(experience_levels, weights=[0.25, 0.50, 0.25])[0]
        
        # Give them a totally average baseline score (between 2 and 6) for EVERY single skill.
        stats = {s: random.randint(2, 6) for s in ["dsa", "backend", "frontend", "ml", "uiux"]}
        
        # Now we cheat and boost their core stats based on their major.
        if archetype == "AI/ML":
            stats["ml"] = random.randint(7, 10)       # Boost ML to 7-10
            stats["dsa"] = random.randint(7, 10)      # Boost DSA to 7-10
            skills = skills_map["AI/ML"]              # Grab the AI text labels
        elif archetype == "Frontend":
            stats["frontend"] = random.randint(7, 10)
            stats["uiux"] = random.randint(7, 10)
            skills = skills_map["Frontend"]
        elif archetype == "Backend":
            stats["backend"] = random.randint(7, 10)
            stats["dsa"] = random.randint(7, 10)
            skills = skills_map["Backend"]
        else: # Fullstack gets a slightly more balanced boost
            stats["backend"] = random.randint(6, 9)
            stats["frontend"] = random.randint(6, 9)
            stats["dsa"] = random.randint(5, 8)
            skills = skills_map["Fullstack"]
            
        # Roll the dice for soft skills and availability
        comm = random.randint(4, 10)
        proj = random.randint(1, 6)
        hacks = random.randint(0, 4)
        avail = random.choice([10, 15, 20, 25, 30, 35])
        
        # Generate extra details
        first_name = name.split(" ")[0].lower()
        last_name = name.split(" ")[1].lower() if " " in name else "dev"
        email = f"{first_name}.{last_name}{i}@university.edu"
        university = random.choice([
            "IIT Bombay", "IIT Delhi", "BITS Pilani", "Delhi Technological University",
            "VIT Vellore", "IIIT Hyderabad", "Manipal Institute of Technology", "NSUT Delhi"
        ])
        github_url = f"https://github.com/{first_name}{i}"
        linkedin_url = f"https://linkedin.com/in/{first_name}-{last_name}-{i}"
        
        # Select 1 to 3 random interests
        interest_pool = ["AI", "Web3", "HealthTech", "FinTech", "EdTech", "IoT", "SaaS", "Security"]
        num_ints = random.randint(1, 3)
        ints = random.sample(interest_pool, num_ints)
        project_interests = ", ".join(ints)
        
        # Select preferred role
        if archetype == "AI/ML":
            preferred_role = random.choice(["AI Engineer", "Algorithm Specialist"])
        elif archetype == "Frontend":
            preferred_role = random.choice(["Frontend Developer", "UI/UX Designer"])
        elif archetype == "Backend":
            preferred_role = random.choice(["Backend Developer", "Algorithm Specialist"])
        else: # Fullstack
            preferred_role = random.choice(["Frontend Developer", "Backend Developer"])
            
        availability = random.choices(
            ["Available", "Busy", "Looking for team"],
            weights=[0.60, 0.10, 0.30]
        )[0]
        
        # Pack all this data into a dictionary and drop it in the students bucket
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
            "cluster_id": -1, # Blank placeholder. The ML model will fill this in later.
            "email": email,
            "password_hash": None,
            "university": university,
            "github_url": github_url,
            "linkedin_url": linkedin_url,
            "project_interests": project_interests,
            "preferred_role": preferred_role,
            "availability": availability
        })
        
    return students # Spit out the full bucket of 60 people


# --- 3. Running the Simulations (Historical Teams) ---
def generate_historical_teams(students, n_teams=300):
    # This builds a "cheat sheet" of successful/failed teams to train your ML model.
    team_data = [] # Empty bucket for fake teams
    
    # Loop 300 times to create 300 test scenarios
    for _ in range(n_teams):
        team_size = random.randint(2, 4) # Decide if this team has 2, 3, or 4 people
        members = random.sample(students, team_size) # Pluck that many students from our pool of 60
        
        # Look at the whole team and find the highest score in each category
        max_dsa = max(m["dsa"] for m in members)
        max_backend = max(m["backend"] for m in members)
        max_frontend = max(m["frontend"] for m in members)
        max_ml = max(m["ml"] for m in members)
        max_uiux = max(m["uiux"] for m in members)
        
        # Find the team's average communication score
        mean_comm = sum(m["communication"] for m in members) / len(members)
        
        # Find the bottleneck: the member with the lowest available hours
        min_avail = min(m["availability_hours"] for m in members)
        
        # Evaluate if the team meets our baseline requirements for success
        has_backend = max_backend >= 6
        has_frontend = max_frontend >= 6
        has_dsa = max_dsa >= 5
        good_comm = mean_comm >= 6.0
        no_bottleneck = min_avail >= 10
        
        # Quick math to generate a rough internal score
        score = (0.2 * max_backend + 0.2 * max_frontend + 0.1 * max_dsa + 0.25 * mean_comm + 0.25 * (min_avail / 5))
        
        # The Heuristic Logic: 
        if has_backend and has_frontend and has_dsa and good_comm and no_bottleneck:
            success_chance = 0.85 # If they pass all checks, 85% chance they succeed
        elif not has_backend or not has_frontend:
            success_chance = 0.15 # If they lack core dev skills, it drops to 15%
        else:
            success_chance = 0.45 # Anyone left in the middle gets a 45% coin toss
            
        # Roll a random decimal. If it's under the success chance, give them a 1 (Success). Else 0 (Fail).
        label = 1 if random.random() < success_chance else 0
        
        # Pack the team's max stats and their final label into the bucket
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
        
    # Convert the bucket of 300 teams into a clean Pandas DataFrame (Excel-style table)
    return pd.DataFrame(team_data)


# --- 4. Pushing the Big Red Button (Seeding the Database) ---
def seed_database():
    # This function actually saves all the fake data to your computer
    init_db() # Create the empty database tables
    
    # Open the door to the database so Python can send commands
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Wipe the slate clean of mock data, but preserve actual registered users.
    cursor.execute("DELETE FROM students WHERE password_hash IS NULL OR password_hash = ''")
    cursor.execute("DELETE FROM teams")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='teams'") # Reset ID counter to 1
    
    conn.commit() # Save the deletions
    conn.close()  # Close the database door
    
    print("Generating profiles...")
    students = generate_students(200) # Generate the 200 fake people
    
    # Re-open the door to insert the new data
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Loop through the people and shove them permanently into the database
    for s in students:
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
            s['name'], s['email'], s['password_hash'], s['dsa'], s['backend'], s['frontend'], s['ml'], s['uiux'],
            s['experience_level'], s['projects_count'], s['hackathons_count'],
            s['availability_hours'], s['skills'], s['communication'], s['cluster_id'],
            s['university'], s['github_url'], s['linkedin_url'], s['project_interests'],
            '', '', '',
            s['preferred_role'], s['availability']
        ))
    conn.commit()
    conn.close()
    print("Successfully seeded 200 developer profiles in SQLite database!")
    
    print("Generating historical team match trials...")
    historical_df = generate_historical_teams(students, 500) # Generate the 500 test scenarios
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "historical_teams.csv")
    
    # Save that Excel-like table of teams as a CSV file in the data folder
    historical_df.to_csv(csv_path, index=False)
    print(f"Successfully saved 500 historical team trials to '{csv_path}'!")

    
    


# --- 5. The Trigger ---
if __name__ == "__main__":
    # Standard Python rule: "Only run the code below if the user ran THIS file directly."
    seed_database()      # Run the database population