import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    LargeBinary,
    Date,
)
from sqlalchemy.orm import relationship
from app.db import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # user, reviewer, admin
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    idea_text = Column(Text, nullable=False)
    domain = Column(String(100), nullable=False, default="agricultural_robotics")
    status = Column(String(50), nullable=False, default="draft")  # draft, ready, needs_review
    safety_flag = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    owner = relationship("User", back_populates="projects")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")
    clarifications = relationship("Clarification", back_populates="project", cascade="all, delete-orphan", order_by="Clarification.position")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    subsystems = relationship("Subsystem", back_populates="project", cascade="all, delete-orphan")
    interfaces = relationship("Interface", back_populates="project", cascade="all, delete-orphan")
    bom_items = relationship("BOMItem", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    roadmap_stages = relationship("RoadmapStage", back_populates="project", cascade="all, delete-orphan", order_by="RoadmapStage.position")
    rule_findings = relationship("RuleFinding", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_json = Column(JSON, nullable=False)
    model_name = Column(String(100), nullable=False)
    prompt_version = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    project = relationship("Project", back_populates="versions")


class Clarification(Base):
    __tablename__ = "clarifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)

    project = relationship("Project", back_populates="clarifications")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(50), nullable=False)  # functional, constraint, assumption
    text = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")  # high, medium, low
    source_type = Column(String(50), nullable=False, default="model_estimate")  # catalogue, rule, model_estimate

    project = relationship("Project", back_populates="requirements")


class Subsystem(Base):
    __tablename__ = "subsystems"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    purpose = Column(Text, nullable=False)
    maps_to_requirement_ids = Column(JSON, default=list, nullable=False)

    project = relationship("Project", back_populates="subsystems")


class Interface(Base):
    __tablename__ = "interfaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    from_subsystem = Column(String(100), nullable=False)
    to_subsystem = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    project = relationship("Project", back_populates="interfaces")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    components = relationship("Component", back_populates="category")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    specs_json = Column(JSON, default=dict, nullable=False)
    typical_use = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    category = relationship("Category", back_populates="components")
    price_points = relationship("PricePoint", back_populates="component", cascade="all, delete-orphan")
    bom_items = relationship("BOMItem", back_populates="component")


class PricePoint(Base):
    __tablename__ = "price_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    component_id = Column(Integer, ForeignKey("components.id", ondelete="CASCADE"), nullable=False, index=True)
    low_inr = Column(Float, nullable=False)
    high_inr = Column(Float, nullable=False)
    checked_on = Column(Date, nullable=True)
    source_note = Column(String(255), nullable=False, default="placeholder, verify before use")
    price_verified = Column(Boolean, default=False, nullable=False)

    component = relationship("Component", back_populates="price_points")


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("components.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    role_in_design = Column(Text, nullable=False)
    confidence = Column(String(50), nullable=False, default="medium")  # high, medium, low
    source_type = Column(String(50), nullable=False, default="catalogue")

    project = relationship("Project", back_populates="bom_items")
    component = relationship("Component", back_populates="bom_items")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")  # high, medium, low
    reason = Column(Text, nullable=False)
    needs_expert = Column(Boolean, default=True, nullable=False)

    project = relationship("Project", back_populates="risks")


class RoadmapStage(Base):
    __tablename__ = "roadmap_stages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    title = Column(String(255), nullable=False)
    deliverable = Column(Text, nullable=False)
    duration_note = Column(String(100), nullable=False)

    project = relationship("Project", back_populates="roadmap_stages")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String(50), primary_key=True)  # e.g., DFM-01, SAFE-01
    area = Column(String(50), nullable=False)  # dfm, readiness, safety
    text = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # info, warn, fail, needs_expert
    version = Column(Integer, default=1, nullable=False)


class RuleFinding(Base):
    __tablename__ = "rule_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(50), ForeignKey("rules.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # pass, warn, fail, needs_expert
    note = Column(Text, nullable=False)

    project = relationship("Project", back_populates="rule_findings")
    rule = relationship("Rule")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    pdf_blob = Column(LargeBinary, nullable=True)
    status = Column(String(50), default="ai_draft", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    project = relationship("Project", back_populates="reports")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="queued", nullable=False)  # queued, running, done, failed
    stage = Column(String(50), default="init", nullable=False)
    progress_percent = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="jobs")


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    facility_type = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    notes = Column(Text, nullable=False)
