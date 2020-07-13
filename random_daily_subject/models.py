from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# engine = create_engine("sqlite:///:memory:")
Base = declarative_base()


class Title(Base):
    __tablename__ = "titles"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    count = Column(Integer)
    is_holiday = Column(Boolean)
    is_special = Column(Boolean)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    bodies = relationship(
        "Body", back_populates="title", cascade="all, delete, delete-orphan"
    )
    submissions = relationship(
        "Submission", back_populates="title", cascade="all, delete, delete-orphan"
    )
    holidays = relationship(
        "Holiday", back_populates="title", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Title(title={self.title}, count={self.count}, "
            f"is_holiday={self.is_holiday}, is_special={self.is_special}, "
            f"is_active={self.is_active}, created_at={self.created_at}, "
            f"modified_at={self.modified_at})>"
        )


class Body(Base):
    __tablename__ = "bodies"
    id = Column(String, primary_key=True)
    body = Column(String, nullable=False)
    count = Column(Integer)
    title_id = Column(String, ForeignKey("titles.id"))
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    title = relationship("Title", back_populates="bodies")
    submissions = relationship("Submission", back_populates="body")

    def __repr__(self):
        return (
            f"<Body(body={self.body}, count={self.count}, title_id={self.title_id}, "
            f"is_active={self.is_active}, created_at={self.created_at}, "
            f"modified_at={self.modified_at})>"
        )


class Submission(Base):
    __tablename__ = "submitted"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    weekday = Column(Integer)
    title_id = Column(String, ForeignKey("titles.id"), nullable=False)
    body_id = Column(String, ForeignKey("bodies.id"))

    title = relationship("Title", back_populates="submissions")
    body = relationship("Body", back_populates="submissions")

    def __repr__(self):
        return (
            f"<Submission(title={self.title_id}, body={self.body_id}, "
            f"date={self.date})>"
        )


class Holiday(Base):
    __tablename__ = "holidays"
    title_id = Column(String, ForeignKey("titles.id"), primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    title = relationship("Title", back_populates="holidays")

    def __repr__(self):
        return (
            f"<Holiday(title_id={self.title_id}, day={self.day}, month={self.month}, "
            f"is_active={self.is_active}, created_at={self.created_at}, "
            f"modified_at={self.modified_at})>"
        )
