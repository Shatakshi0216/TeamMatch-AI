import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import (
    init_db, get_all_students, add_student, get_all_teams, 
    add_team, delete_team
)
from engine.ml_pipeline import (
    get_recommendations, calculate_ml_team_health, get_ml_team_recommendations
)

app = FastAPI(
    title="TeamMatch AI - ML REST API",
    description="FastAPI Backend for React Teammate Matching & Team Builder Diagnostics",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing) for local dev compatibility with React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
init_db()

# --- API ENDPOINTS FOR THE REACT FRONTEND ---

@app.get("/api/students")
async def api_students():
    """Retrieves all registered developer profiles from SQLite database."""
    try:
        students = get_all_students()
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students", status_code=status.HTTP_201_CREATED)
async def api_add_student(request: Request):
    """Registers a new developer profile."""
    data = await request.json()
    if not data or not data.get('name'):
        raise HTTPException(status_code=400, detail="Name field is required")
        
    try:
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
            "communication": int(data.get('communication', 5))
        }
        
        add_student(student_profile)
        return {"message": "Profile created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend")
async def api_recommend(request: Request):
    """
    ML Teammate Matcher: Queries the KNN model with Cosine Similarity
    using the complement vector query to return top N matched partners.
    """
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
    """
    ML Team Diagnostics: Uses K-Means group assignments to compute
    role diversity, calculate coverage metrics, and trigger skill-deficit gaps.
    """
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
    """
    ML Recruit suggestions: Simulates recruit additions, utilizing K-Means
    diversity gains to recommend candidates who fill team archetype gaps.
    """
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

if __name__ == '__main__':
    # Start the backend server on port 5000
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
