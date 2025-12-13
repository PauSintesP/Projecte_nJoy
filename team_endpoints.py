from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import SessionLocal
from models import Team, TeamMember, Usuario
from auth import get_current_active_user, get_db
import team_schemas

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
    responses={404: {"description": "Not found"}},
)

# --- Team Member Event Endpoints ---

@router.get("/events", response_model=List[team_schemas.EventResponse]) # We need to ensure EventResponse is available in team_schemas or use properties
def get_team_events(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from models import Evento, TeamMember, Team
    
    # 1. Get all teams where user is a member (accepted) OR leader
    # Teams led by user
    led_teams = db.query(Team).filter(Team.leader_id == current_user.id).all()
    leader_ids = {t.leader_id for t in led_teams}
    
    # Teams where user is member
    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == 'accepted'
    ).all()
    
    for m in memberships:
        # Get the team to find the leader
        team = db.query(Team).filter(Team.id == m.team_id).first()
        if team:
            leader_ids.add(team.leader_id)
            
    if not leader_ids:
        return []
        
    # 2. Get events created by these leaders
    events = db.query(Evento).filter(Evento.creador_id.in_(leader_ids)).all()
    
    return events

# --- Promotor/Admin Endpoints ---

@router.post("/", response_model=team_schemas.TeamResponse)
def create_team(
    team: team_schemas.TeamCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["promotor", "admin", "owner"]:
        raise HTTPException(status_code=403, detail="Only promoters, owners or admins can create teams")
    
    # Check if team name exists
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already taken")
    
    new_team = Team(
        name=team.name,
        leader_id=current_user.id
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

@router.get("/managed", response_model=List[team_schemas.TeamListResponse])
def get_managed_teams(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get teams where user is leader
    teams = db.query(Team).filter(Team.leader_id == current_user.id).all()
    
    # Add member count logic if needed manually, but better to do in query or property
    # For now, let's just return them, pydantic will handle member_count if we add a property to model or hack it
    # Pydantic hack:
    results = []
    for t in teams:
        count = db.query(TeamMember).filter(TeamMember.team_id == t.id, TeamMember.status == 'accepted').count()
        t.member_count = count
        results.append(t)
        
    return results



@router.post("/{team_id}/invite", response_model=team_schemas.TeamMemberResponse)
def invite_user(
    team_id: int,
    invite: team_schemas.TeamInvite,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    if team.leader_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only the leader can invite members")
        
    # Find user by email
    target_user = db.query(Usuario).filter(Usuario.email == invite.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with this email not found")
        
    # Check if already in team
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == target_user.id
    ).first()
    
    if existing_member:
        if existing_member.status == 'rejected':
            # Re-invite
            existing_member.status = 'pending'
            existing_member.invited_at = datetime.now()
            db.commit()
            db.refresh(existing_member)
            return existing_member
        elif existing_member.status == 'active' or existing_member.status == 'accepted':
            raise HTTPException(status_code=400, detail="User is already in the team")
        else:
            raise HTTPException(status_code=400, detail="Invitation already pending")
            
    new_member = TeamMember(
        team_id=team_id,
        user_id=target_user.id,
        status='pending'
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

# --- User Endpoints ---

@router.get("/my-invitations", response_model=List[team_schemas.TeamInvitationResponse])
def get_my_invitations(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    invitations = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == 'pending'
    ).all()
    
    # Manual mapping to include Team Name
    results = []
    for inv in invitations:
        team = db.query(Team).filter(Team.id == inv.team_id).first()
        results.append({
            "id": inv.id,
            "team_id": inv.team_id,
            "team_name": team.name if team else "Unknown Team",
            "status": inv.status,
            "invited_at": inv.invited_at,
            "joined_at": inv.joined_at
        })
        
    return results

@router.post("/invitations/{member_id}/respond")
def respond_invitation(
    member_id: int,
    status_update: str, # accepted or rejected
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if status_update not in ['accepted', 'rejected']:
        raise HTTPException(status_code=400, detail="Invalid status")

    membership = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    if membership.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your invitation")
        
    membership.status = status_update
    if status_update == 'accepted':
        membership.joined_at = datetime.now()
        
    db.commit()
    return {"message": f"Invitation {status_update}"}

@router.get("/my-teams", response_model=List[team_schemas.TeamListResponse])
def get_my_teams(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Teams where I am a member
    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == 'accepted'
    ).all()
    
    teams = []
    for m in memberships:
        # We return the team object, but mapped to TeamListResponse
        # Pydantic will extract fields. member_count defaults to 0 if not present.
        t = m.team
        # We can optionally count members if we want, but UI doesn't use it.
        # To be safe against Pydantic validation if it expects 'member_count' on the object:
        # We can just construct a dict or rely on default=0 in schema if it's not required?
        # Schema: member_count: int = 0. So it has a default.
        teams.append(t)
        
    return teams


@router.get("/{team_id}", response_model=team_schemas.TeamResponse)
def get_team_details(
    team_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check permissions: Leader or Member
    is_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, 
        TeamMember.user_id == current_user.id,
        TeamMember.status == 'accepted'
    ).first()
    
    if team.leader_id != current_user.id and not is_member and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to view this team")

    # Enroll user emails for response
    for member in team.members:
        user_obj = db.query(Usuario).filter(Usuario.id == member.user_id).first()
        if user_obj:
            member.user_email = user_obj.email
            member.user_name = f"{user_obj.nombre} {user_obj.apellidos}"

    return team
