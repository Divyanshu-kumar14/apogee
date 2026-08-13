"""
SQLAlchemy database models for APOGEE.
Defines all tables: telemetry_reading, tracked_object, conjunction_risk, 
transit_candidate, and alerts (shared integration table).
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class TelemetryReading(Base):
    """
    Stores simulated spacecraft telemetry readings.
    One row per metric per timestamp.
    """
    __tablename__ = "telemetry_reading"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spacecraft_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_spacecraft_metric_time', 'spacecraft_id', 'metric_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<TelemetryReading(spacecraft={self.spacecraft_id}, metric={self.metric_name}, value={self.value})>"


class TrackedObject(Base):
    """
    Stores orbital objects from CelesTrak TLE data.
    Includes apogee/perigee for altitude-based pre-filtering.
    """
    __tablename__ = "tracked_object"
    
    norad_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    tle_line1 = Column(String(69), nullable=False)
    tle_line2 = Column(String(69), nullable=False)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    apogee_km = Column(Float, nullable=True)  # For pre-filtering
    perigee_km = Column(Float, nullable=True)  # For pre-filtering
    
    def __repr__(self):
        return f"<TrackedObject(norad_id={self.norad_id}, name={self.name})>"


class ConjunctionRisk(Base):
    """
    Stores computed conjunction risk assessments.
    Links spacecraft to tracked objects with risk metrics.
    """
    __tablename__ = "conjunction_risk"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spacecraft_id = Column(String(50), nullable=False, index=True)
    object_norad_id = Column(Integer, ForeignKey('tracked_object.norad_id'), nullable=False)
    closest_approach_km = Column(Float, nullable=False)
    relative_velocity_kmps = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False, index=True)  # 0-100
    computed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Composite index for efficient risk queries
    __table_args__ = (
        Index('idx_spacecraft_risk', 'spacecraft_id', 'risk_score'),
    )
    
    def __repr__(self):
        return f"<ConjunctionRisk(spacecraft={self.spacecraft_id}, object={self.object_norad_id}, risk={self.risk_score})>"


class TransitCandidate(Base):
    """
    Stores TESS exoplanet transit detection results.
    Includes both BLS detection and ML vetting results.
    """
    __tablename__ = "transit_candidate"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tic_id = Column(Integer, nullable=False, index=True)
    target_name = Column(String(100), nullable=True)
    sector = Column(Integer, nullable=False)
    period = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    snr = Column(Float, nullable=False)
    disposition = Column(String(20), nullable=False)
    vetting_confidence = Column(Float, nullable=False)
    discovered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TransitCandidate(tic_id={self.tic_id}, sector={self.sector}, disposition={self.disposition})>"


class Alert(Base):
    """
    SHARED ALERTS TABLE - Core integration proof.
    Stores alerts from both Health Monitor (anomalies) and Debris Risk (conjunctions).
    response_category distinguishes engineering vs flight dynamics responses.
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    spacecraft_id = Column(String(50), nullable=False, index=True)
    source = Column(String(20), nullable=False)  # "health" | "debris"
    response_category = Column(String(20), nullable=False)  # "engineering" | "flight_dynamics"
    severity = Column(String(20), nullable=False, index=True)  # "nominal" | "watch" | "critical"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    explained = Column(Boolean, nullable=False, default=False)  # For watsonx/Granite integration
    explanation = Column(Text, nullable=True)  # Cached LLM explanation
    
    # Composite index for efficient alert queries
    __table_args__ = (
        Index('idx_spacecraft_severity_time', 'spacecraft_id', 'severity', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, source={self.source}, severity={self.severity}, category={self.response_category})>"
