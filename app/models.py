from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, text, UniqueConstraint
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    visibility = Column(String, nullable=False, server_default="private")
    owner = relationship("User")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    workspace_id = Column(Integer, ForeignKey(
        "workspaces.id", ondelete="CASCADE"), nullable=False)
    workspace = relationship("Workspace")


class WorkspaceMember(Base):
    __tablename__ = "workspacemembers"

    id = Column(Integer, primary_key=True, nullable=False)

    workspace_id = Column(Integer, ForeignKey(
        "workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    workspace = relationship("Workspace")
    user = relationship("User")

    __table_args = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_member"
        ),
    )
