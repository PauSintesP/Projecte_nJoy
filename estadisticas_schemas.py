"""
Schemas for Event Statistics API
Handles statistics data validation and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HourlyEntryStats(BaseModel):
    """Statistics for ticket entries per hour"""
    hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)")
    count: int = Field(..., ge=0, description="Number of entries in this hour")
    hour_label: str = Field(..., description="Formatted hour label (e.g., '14:00')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hour": 20,
                "count": 45,
                "hour_label": "20:00"
            }
        }

class TemporalFlowPoint(BaseModel):
    """Point in temporal flow chart (cumulative entries over time)"""
    hour: int = Field(..., ge=0, le=23, description="Hour of the day")
    count: int = Field(..., ge=0, description="New entries in this hour")
    cumulative: int = Field(..., ge=0, description="Cumulative entries up to this hour")
    hour_label: str = Field(..., description="Formatted hour label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hour": 21,
                "count": 15,
                "cumulative": 45,
                "hour_label": "21:00"
            }
        }

class EventStatsResponse(BaseModel):
    """Complete event statistics response"""
    
    # Financial metrics
    ingreso_total: float = Field(..., description="Total revenue generated")
    ingreso_promedio_ticket: float = Field(..., description="Average revenue per ticket")
    
    # Capacity metrics
    capacidad_total: int = Field(..., description="Total event capacity")
    tickets_vendidos: int = Field(..., description="Number of tickets sold")
    tickets_disponibles: int = Field(..., description="Available tickets remaining")
    
    # Attendance metrics
    tickets_escaneados: int = Field(..., description="Number of tickets scanned/validated")
    tasa_asistencia: float = Field(..., description="Attendance rate percentage")
    
    # Hourly breakdown
    entradas_por_hora: List[HourlyEntryStats] = Field(..., description="Hourly entry breakdown")
    hora_pico: Optional[str] = Field(None, description="Peak hour with most entries")
    max_entradas_hora: int = Field(0, description="Maximum entries in a single hour")
    
    # Temporal flow (cumulative over time)
    flujo_temporal: List[TemporalFlowPoint] = Field(default=[], description="Cumulative entry flow over time")
    hora_evento: int = Field(..., description="Event start hour (for timeline reference)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ingreso_total": 2500.00,
                "ingreso_promedio_ticket": 25.00,
                "capacidad_total": 200,
                "tickets_vendidos": 100,
                "tickets_disponibles": 100,
                "tickets_escaneados": 85,
                "tasa_asistencia": 85.0,
                "entradas_por_hora": [
                    {"hour": 20, "count": 30, "hour_label": "20:00"},
                    {"hour": 21, "count": 45, "hour_label": "21:00"},
                    {"hour": 22, "count": 10, "hour_label": "22:00"}
                ],
                "hora_pico": "21:00",
                "max_entradas_hora": 45
            }
        }

class PasswordVerificationRequest(BaseModel):
    """Request to verify user password for stats access"""
    password: str = Field(..., min_length=1, description="User password for verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "mySecurePassword123"
            }
        }

class StatsAccessTokenResponse(BaseModel):
    """Response containing temporary access token for statistics"""
    access_token: str = Field(..., description="Temporary JWT token for stats access")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_in": 300,
                "token_type": "bearer"
            }
        }
