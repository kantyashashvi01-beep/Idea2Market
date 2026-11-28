"""Initial schema for Idea2market

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-28 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("idea_text", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(100), nullable=False, server_default="agricultural_robotics"),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("safety_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])

    op.create_table(
        "project_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_json", sa.JSON(), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prompt_version", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_project_versions_project_id", "project_versions", ["project_id"])

    op.create_table(
        "clarifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_clarifications_project_id", "clarifications", ["project_id"])

    op.create_table(
        "requirements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="model_estimate"),
    )
    op.create_index("ix_requirements_project_id", "requirements", ["project_id"])

    op.create_table(
        "subsystems",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("maps_to_requirement_ids", sa.JSON(), nullable=False),
    )
    op.create_index("ix_subsystems_project_id", "subsystems", ["project_id"])

    op.create_table(
        "interfaces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_subsystem", sa.String(100), nullable=False),
        sa.Column("to_subsystem", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )
    op.create_index("ix_interfaces_project_id", "interfaces", ["project_id"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
    )

    op.create_table(
        "components",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("specs_json", sa.JSON(), nullable=False),
        sa.Column("typical_use", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_components_category_id", "components", ["category_id"])

    op.create_table(
        "price_points",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("component_id", sa.Integer(), sa.ForeignKey("components.id", ondelete="CASCADE"), nullable=False),
        sa.Column("low_inr", sa.Float(), nullable=False),
        sa.Column("high_inr", sa.Float(), nullable=False),
        sa.Column("checked_on", sa.Date(), nullable=True),
        sa.Column("source_note", sa.String(255), nullable=False, server_default="placeholder, verify before use"),
        sa.Column("price_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_price_points_component_id", "price_points", ["component_id"])

    op.create_table(
        "bom_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("component_id", sa.Integer(), sa.ForeignKey("components.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("role_in_design", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="catalogue"),
    )
    op.create_index("ix_bom_items_project_id", "bom_items", ["project_id"])
    op.create_index("ix_bom_items_component_id", "bom_items", ["component_id"])

    op.create_table(
        "risks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("needs_expert", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_risks_project_id", "risks", ["project_id"])

    op.create_table(
        "roadmap_stages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("deliverable", sa.Text(), nullable=False),
        sa.Column("duration_note", sa.String(100), nullable=False),
    )
    op.create_index("ix_roadmap_stages_project_id", "roadmap_stages", ["project_id"])

    op.create_table(
        "rules",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("area", sa.String(50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_table(
        "rule_findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_id", sa.String(50), sa.ForeignKey("rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
    )
    op.create_index("ix_rule_findings_project_id", "rule_findings", ["project_id"])

    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("pdf_blob", sa.LargeBinary(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="ai_draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reports_project_id", "reports", ["project_id"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="queued"),
        sa.Column("stage", sa.String(50), nullable=False, server_default="init"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_jobs_project_id", "jobs", ["project_id"])

    op.create_table(
        "facilities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("facility_type", sa.String(100), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("facilities")
    op.drop_table("jobs")
    op.drop_table("reports")
    op.drop_table("rule_findings")
    op.drop_table("rules")
    op.drop_table("roadmap_stages")
    op.drop_table("risks")
    op.drop_table("bom_items")
    op.drop_table("price_points")
    op.drop_table("components")
    op.drop_table("categories")
    op.drop_table("interfaces")
    op.drop_table("subsystems")
    op.drop_table("requirements")
    op.drop_table("clarifications")
    op.drop_table("project_versions")
    op.drop_table("projects")
    op.drop_table("users")
