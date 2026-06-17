import os
import hashlib
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import (
    init_db, get_all_students, add_student, get_all_teams, 
    add_team, delete_team, get_student_by_email, update_student,
    add_message, get_messages, get_db_connection
)
from engine.ml_pipeline import (
    get_recommendations, calculate_ml_team_health, get_ml_team_recommendations
)

app = FastAPI(
    title="TeamMatch AI - ML REST API",
    description="FastAPI Backend with Security and Authenticated Profiles",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def hash_password(password: str) -> str:
    """Hashes the password with SHA-256 for basic security validation."""
    return hashlib.sha256(password.encode()).hexdigest()

def infer_skills_ratings(skills_list):
    """Infers 1-10 skill ratings from TeamMatch AI's text skill tags."""
    ratings = {"dsa": 4, "backend": 4, "frontend": 4, "ml": 4, "uiux": 4}
    skills_lower = [s.lower().strip() for s in skills_list]
    
    fe_keywords = ["react", "next.js", "vue", "angular", "html", "css", "tailwind", "svelte", "typescript", "javascript", "figma"]
    if any(k in skills_lower for k in fe_keywords):
        ratings["frontend"] = 7
        if "react" in skills_lower or "next.js" in skills_lower or "typescript" in skills_lower:
            ratings["frontend"] = 9
            
    be_keywords = ["node.js", "express", "django", "flask", "spring boot", "fastapi", "ruby on rails", "laravel", "go", "java", "c++", "c#", "sql", "postgresql", "mysql", "mongodb"]
    if any(k in skills_lower for k in be_keywords):
        ratings["backend"] = 7
        if "node.js" in skills_lower or "django" in skills_lower or "fastapi" in skills_lower:
            ratings["backend"] = 9
            
    ml_keywords = ["python", "tensorflow", "pytorch", "opencv", "scikit-learn", "keras", "hugging face", "langchain", "ai", "machine learning"]
    if any(k in skills_lower for k in ml_keywords):
        ratings["ml"] = 7
        if "tensorflow" in skills_lower or "pytorch" in skills_lower or "langchain" in skills_lower:
            ratings["ml"] = 9
            
    uiux_keywords = ["figma", "ui/ux", "design", "illustrator", "photoshop", "css", "tailwind"]
    if any(k in skills_lower for k in uiux_keywords):
        ratings["uiux"] = 7
        if "figma" in skills_lower or "ui/ux" in skills_lower:
            ratings["uiux"] = 9
            
    dsa_keywords = ["c++", "java", "python", "dsa", "leetcode", "algorithms", "data structures", "competitive programming"]
    if any(k in skills_lower for k in dsa_keywords):
        ratings["dsa"] = 7
        if "dsa" in skills_lower or "algorithms" in skills_lower:
            ratings["dsa"] = 9
            
    return ratings

def get_student_by_id(student_id: int):
    """Retrieves student profile by id."""
    students = get_all_students()
    return next((s for s in students if s['student_id'] == student_id), None)

def get_user_id_from_header(request: Request) -> int:
    """Extracts mock user ID (student_id) from Authorization Bearer header."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth.split(" ")[1]
    try:
        return int(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def api_register(request: Request):
    """Registers a new student profile with user credentials."""
    data = await request.json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        raise HTTPException(status_code=400, detail="Name, Email, and Password are required.")
    
    try:
        existing = get_student_by_email(data['email'])
        if existing:
            raise HTTPException(status_code=400, detail="Email is already registered.")
            
        student_profile = {
            "name": data['name'],
            "email": data['email'],
            "password_hash": hash_password(data['password']),
            "dsa": int(data.get('dsa', 5)),
            "backend": int(data.get('backend', 5)),
            "frontend": int(data.get('frontend', 5)),
            "ml": int(data.get('ml', 5)),
            "uiux": int(data.get('uiux', 5)),
            "experience_level": data.get('experience_level', 'Intermediate'),
            "projects_count": int(data.get('projects_count', 0)),
            "hackathons_count": int(data.get('hackathons_count', 0)),
            "availability_hours": int(data.get('availability_hours', 15)),
            "skills": data.get('skills', 'Generalist'),
            "communication": int(data.get('communication', 5)),
            "university": data.get('university', ''),
            "github_url": data.get('github_url', ''),
            "linkedin_url": data.get('linkedin_url', ''),
            "project_interests": data.get('project_interests', ''),
            "past_hackathon_name": data.get('past_hackathon_name', ''),
            "past_hackathon_project": data.get('past_hackathon_project', ''),
            "past_hackathon_desc": data.get('past_hackathon_desc', '')
        }
        
        add_student(student_profile)
        # Return student profile details excluding the credentials
        new_student = get_student_by_email(data['email'])
        student_data = dict(new_student)
        student_data.pop('password_hash', None)
        return {
            "message": "Registration successful.",
            "student": student_data,
            "token": str(student_data['student_id']),
            "userId": student_data['student_id']
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def api_login(request: Request):
    """Authenticates student credentials."""
    data = await request.json()
    if not data or not data.get('email') or not data.get('password'):
        raise HTTPException(status_code=400, detail="Email and Password are required.")
        
    try:
        student = get_student_by_email(data['email'])
        if not student:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
            
        hashed_input = hash_password(data['password'])
        if student['password_hash'] != hashed_input:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
            
        student_data = dict(student)
        student_data.pop('password_hash', None)
        return {
            "message": "Login successful.",
            "student": student_data,
            "token": str(student_data['student_id']),
            "userId": student_data['student_id']
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students/update")
async def api_update_student(request: Request):
    """Saves profile updates from the logged-in candidate."""
    data = await request.json()
    if not data or not data.get('student_id'):
        raise HTTPException(status_code=400, detail="student_id is required.")
        
    try:
        student_id = int(data['student_id'])
        student_profile = {
            "name": data['name'],
            "dsa": int(data.get('dsa', 5)),
            "backend": int(data.get('backend', 5)),
            "frontend": int(data.get('frontend', 5)),
            "ml": int(data.get('ml', 5)),
            "uiux": int(data.get('uiux', 5)),
            "experience_level": data.get('experience_level', 'Intermediate'),
            "projects_count": int(data.get('projects_count', 0)),
            "hackathons_count": int(data.get('hackathons_count', 0)),
            "availability_hours": int(data.get('availability_hours', 15)),
            "skills": data.get('skills', 'Generalist'),
            "communication": int(data.get('communication', 5)),
            "university": data.get('university', ''),
            "github_url": data.get('github_url', ''),
            "linkedin_url": data.get('linkedin_url', ''),
            "project_interests": data.get('project_interests', ''),
            "past_hackathon_name": data.get('past_hackathon_name', ''),
            "past_hackathon_project": data.get('past_hackathon_project', ''),
            "past_hackathon_desc": data.get('past_hackathon_desc', '')
        }
        
        update_student(student_id, student_profile)
        return {"message": "Profile updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students")
async def api_students():
    """Retrieves all registered developer profiles from SQLite database."""
    try:
        students = get_all_students()
        cleaned_students = []
        for s in students:
            s_dict = dict(s)
            s_dict.pop('password_hash', None)
            cleaned_students.append(s_dict)
        return cleaned_students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend")
async def api_recommend(request: Request):
    """ML Teammate Matcher: Queries the KNN model with Cosine Similarity."""
    data = await request.json()
    if not data or not data.get('student_id'):
        raise HTTPException(status_code=400, detail="student_id is required")
        
    student_id = int(data['student_id'])
    top_n = int(data.get('top_n', 5))
    
    try:
        recs = get_recommendations(student_id, top_n=top_n, metric='cosine')
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team-health")
async def api_team_health(request: Request):
    """ML Team Diagnostics: Uses K-Means group assignments to compute health score."""
    data = await request.json()
    if not data or 'members' not in data:
        raise HTTPException(status_code=400, detail="members list is required")
        
    try:
        result = calculate_ml_team_health(data['members'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team-recommend")
async def api_team_recommend(request: Request):
    """ML Recruit suggestions: Simulates recruit additions to recommend candidates."""
    data = await request.json()
    if not data or 'team_member_ids' not in data:
        raise HTTPException(status_code=400, detail="team_member_ids list is required")
        
    team_member_ids = [int(mid) for mid in data['team_member_ids']]
    top_n = int(data.get('top_n', 4))
    
    try:
        recs = get_ml_team_recommendations(team_member_ids, top_n=top_n)
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/teams")
async def api_get_teams():
    """Retrieves saved team rosters from SQLite database."""
    try:
        teams = get_all_teams()
        formatted_teams = []
        for t in teams:
            members_str = t['members']
            formatted_teams.append({
                "team_id": t['team_id'],
                "team_name": t['team_name'],
                "description": t['description'],
                "health_score": t['health_score'],
                "members": [int(mid) for mid in members_str.split(',') if mid],
                "created_at": t['created_at']
            })
        return formatted_teams
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/teams", status_code=status.HTTP_201_CREATED)
async def api_add_team(request: Request):
    """Saves a formed team assembly to the SQLite database."""
    data = await request.json()
    if not data or not data.get('team_name') or not data.get('members'):
        raise HTTPException(status_code=400, detail="team_name and members list are required")
        
    try:
        member_ids_str = ",".join(map(str, data['members']))
        team_record = {
            "team_name": data['team_name'],
            "description": data.get('description', ''),
            "health_score": float(data.get('health_score', 0.0)),
            "members": member_ids_str,
            "predicted_compatibility": "N/A"
        }
        
        add_team(team_record)
        return {"message": "Team roster successfully saved to SQLite database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/teams/{team_id}")
async def api_delete_team(team_id: int):
    """Deletes a saved team roster by ID."""
    try:
        delete_team(team_id)
        return {"message": f"Team {team_id} successfully deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages")
async def api_send_message(request: Request):
    """Sends a new message between two candidates."""
    data = await request.json()
    if not data or 'sender_id' not in data or 'receiver_id' not in data or 'message_text' not in data:
        raise HTTPException(status_code=400, detail="sender_id, receiver_id, and message_text are required.")
    try:
        add_message(int(data['sender_id']), int(data['receiver_id']), data['message_text'].strip())
        return {"status": "success", "message": "Message sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{user1_id}/{user2_id}")
async def api_get_messages(user1_id: int, user2_id: int):
    """Retrieves conversation history between two candidates."""
    try:
        msgs = get_messages(user1_id, user2_id)
        return msgs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile")
async def api_get_profile(request: Request):
    """Fetches mapped profile for authenticated student."""
    user_id = get_user_id_from_header(request)
    student = get_student_by_id(user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Map database schema to TeamMatch AI frontend schema
    return {
        "user_id": student['student_id'],
        "full_name": student['name'],
        "college": student['university'],
        "contact_email": student['email'],
        "github_link": student['github_url'],
        "linkedin_link": student['linkedin_url'],
        "skills": [s.strip() for s in student['skills'].split(",") if s.strip()] if student['skills'] else [],
        "interests": [i.strip() for i in student['project_interests'].split(",") if i.strip()] if student['project_interests'] else [],
        "experience_level": student['experience_level'],
        "preferred_role": student.get('preferred_role', 'Frontend Developer'),
        "availability": student.get('availability', 'Looking for team'),
        "past_hackathon": student.get('past_hackathon_name', ''),
        "past_project_name": student.get('past_hackathon_project', ''),
        "past_project_desc": student.get('past_hackathon_desc', '')
    }

@app.post("/api/profile")
async def api_post_profile(request: Request):
    """Saves updated profile fields and infers ML skill ratings."""
    user_id = get_user_id_from_header(request)
    data = await request.json()
    
    skills_list = data.get('skills', [])
    ratings = infer_skills_ratings(skills_list)
    
    avail_status = data.get('availability', 'Looking for team')
    avail_hours = 25 if avail_status == "Looking for team" else 20 if avail_status == "Available" else 5
    
    exp = data.get('experience_level', 'Intermediate')
    comm = 9 if exp == "Advanced" else 7 if exp == "Intermediate" else 5
    
    student_profile = {
        "name": data.get('full_name', ''),
        "dsa": ratings["dsa"],
        "backend": ratings["backend"],
        "frontend": ratings["frontend"],
        "ml": ratings["ml"],
        "uiux": ratings["uiux"],
        "experience_level": exp,
        "projects_count": 3 if exp == "Advanced" else 1 if exp == "Intermediate" else 0,
        "hackathons_count": 2 if exp == "Advanced" else 1 if exp == "Intermediate" else 0,
        "availability_hours": avail_hours,
        "skills": ", ".join(skills_list),
        "communication": comm,
        "university": data.get('college', ''),
        "github_url": data.get('github_link', ''),
        "linkedin_url": data.get('linkedin_link', ''),
        "project_interests": ", ".join(data.get('interests', [])),
        "past_hackathon_name": data.get('past_hackathon', ''),
        "past_hackathon_project": data.get('past_project_name', ''),
        "past_hackathon_desc": data.get('past_project_desc', ''),
        "preferred_role": data.get('preferred_role', 'Frontend Developer'),
        "availability": avail_status
    }
    
    update_student(user_id, student_profile)
    return {"success": True}

@app.post("/api/match/{userId}")
async def api_match(userId: int, request: Request):
    """KNN Matchmaker mapping into TeamMatch AI teammate card structures."""
    get_user_id_from_header(request)
    data = await request.json()
    limit = int(data.get('limit', 5))
    hackathon_mode = data.get('hackathonMode', False)
    search_skills = data.get('searchSkills', '')
    search_ints = data.get('searchInterests', '')
    
    recs = get_recommendations(userId, top_n=50, metric='cosine')
    
    matched = []
    for r in recs:
        cand = r['student']
        compat = r['compatibility_score']
        
        if hackathon_mode and cand.get('availability', 'Looking for team') == 'Busy':
            continue
            
        cand_skills = [s.strip() for s in cand['skills'].split(",") if s.strip()] if cand['skills'] else []
        cand_ints = [i.strip() for i in cand['project_interests'].split(",") if i.strip()] if cand['project_interests'] else []
        
        if search_skills:
            search_skills_list = [s.strip().lower() for s in search_skills.split(",") if s.strip()]
            if not any(any(sk in cs.lower() for cs in cand_skills) for sk in search_skills_list):
                continue
                
        if search_ints:
            search_ints_list = [i.strip().lower() for i in search_ints.split(",") if i.strip()]
            if not any(any(it in ci.lower() for ci in cand_ints) for it in search_ints_list):
                continue
        
        my_student = get_student_by_id(userId)
        my_skills = [s.strip().lower() for s in my_student['skills'].split(",") if s.strip()] if my_student and my_student['skills'] else []
        common_skills = [s for s in cand_skills if s.lower() in my_skills]
        
        matched.append({
            "user_id": cand['student_id'],
            "full_name": cand['name'],
            "college": cand['university'],
            "contact_email": cand['email'],
            "github_link": cand['github_url'],
            "linkedin_link": cand['linkedin_url'],
            "skills": cand_skills,
            "interests": cand_ints,
            "experience_level": cand['experience_level'],
            "preferred_role": cand.get('preferred_role', 'Frontend Developer'),
            "availability": cand.get('availability', 'Available'),
            "past_hackathon": cand.get('past_hackathon_name', ''),
            "past_project_name": cand.get('past_hackathon_project', ''),
            "matchPercentage": int(compat),
            "breakdown": {
                "skillScore": int(compat * 0.4),
                "interestScore": int(compat * 0.3),
                "expScore": int(compat * 0.2),
                "availScore": int(compat * 0.1)
            },
            "commonSkills": common_skills,
            "explanation": f"You both share {' and '.join(common_skills[:2]) if common_skills else 'hackathon goals'} tags."
        })
        
    return matched[:limit]

@app.get("/api/build-team/{userId}")
async def api_build_team(userId: int, request: Request):
    """K-Means Team Builder recommendations utilizing simulated roster health scores."""
    get_user_id_from_header(request)
    recs = get_ml_team_recommendations(team_member_ids=[userId], top_n=4)
    
    team = []
    for r in recs:
        cand = r['student']
        new_score = r['new_health_score']
        gain = r['health_gain']
        
        skills_ratings = {
            "Frontend Developer": cand['frontend'],
            "Backend Developer": cand['backend'],
            "AI Engineer": cand['ml'],
            "UI/UX Designer": cand['uiux'],
            "Algorithm Specialist": cand['dsa']
        }
        suggested_role = max(skills_ratings, key=skills_ratings.get)
        
        cand_skills = [s.strip() for s in cand['skills'].split(",") if s.strip()] if cand['skills'] else []
        cand_ints = [i.strip() for i in cand['project_interests'].split(",") if i.strip()] if cand['project_interests'] else []
        
        team.append({
            "user_id": cand['student_id'],
            "full_name": cand['name'],
            "college": cand['university'],
            "contact_email": cand['email'],
            "github_link": cand['github_url'],
            "linkedin_link": cand['linkedin_url'],
            "skills": cand_skills,
            "interests": cand_ints,
            "experience_level": cand['experience_level'],
            "preferred_role": cand.get('preferred_role', suggested_role),
            "availability": cand.get('availability', 'Available'),
            "past_hackathon": cand.get('past_hackathon_name', ''),
            "past_project_name": cand.get('past_hackathon_project', ''),
            "suggestedFor": suggested_role,
            "commonSkills": [],
            "matchPercentage": int(new_score),
            "explanation": f"Completes the team as a {suggested_role}, increasing predicted health by +{gain}%."
        })
    return team

@app.get("/api/conversations")
async def api_get_conversations(request: Request):
    """Lists conversations with latest messages for authenticated student."""
    user_id = get_user_id_from_header(request)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT
            CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as other_id
        FROM messages
        WHERE sender_id = ? OR receiver_id = ?
    """, (user_id, user_id, user_id))
    other_ids = [row['other_id'] for row in cursor.fetchall()]
    
    conversations = []
    for oid in other_ids:
        cursor.execute("""
            SELECT message_text, timestamp, sender_id
            FROM messages
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id, oid, oid, user_id))
        last_msg = cursor.fetchone()
        if not last_msg:
            continue
            
        cursor.execute("SELECT student_id, name, university, email FROM students WHERE student_id = ?", (oid,))
        other_student = cursor.fetchone()
        if not other_student:
            continue
            
        conversations.append({
            "room_id": f"{min(user_id, oid)}_{max(user_id, oid)}",
            "other_user_name": other_student['name'],
            "other_user_id": str(oid),
            "last_message": last_msg['message_text'],
            "last_timestamp": last_msg['timestamp']
        })
    
    conn.close()
    conversations.sort(key=lambda x: x['last_timestamp'], reverse=True)
    return conversations

@app.get("/api/messages/{room_id}")
async def api_get_room_messages(room_id: str, request: Request):
    """Retrieves conversation history mapped for TeamMatch AI room ID."""
    get_user_id_from_header(request)
    try:
        u1, u2 = map(int, room_id.split("_"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room_id format")
        
    msgs = get_messages(u1, u2)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name FROM students WHERE student_id IN (?, ?)", (u1, u2))
    names = {row['student_id']: row['name'] for row in cursor.fetchall()}
    conn.close()
    
    formatted_msgs = []
    for m in msgs:
        formatted_msgs.append({
            "_id": str(m['message_id']),
            "room_id": room_id,
            "sender_id": str(m['sender_id']),
            "sender_name": names.get(m['sender_id'], "Unknown"),
            "text": m['message_text'],
            "timestamp": m['timestamp']
        })
    return formatted_msgs

if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True, reload_dirs=[os.path.dirname(os.path.abspath(__file__))])
