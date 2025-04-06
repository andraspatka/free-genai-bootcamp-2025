import uuid
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String, index=True, nullable=False)
    story = Column(Text, nullable=True)  # Story text might be generated later
    image = Column(String, nullable=True) # S3 path
    audio = Column(String, nullable=True) # S3 path

    quizzes = relationship("Quiz", back_populates="story")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False) # Correct answer

    story = relationship("Story", back_populates="quizzes")
    quiz_answers = relationship("QuizAnswer", back_populates="quiz")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    answer = Column(Text, nullable=False) # User's submitted answer
    is_correct = Column(Boolean, nullable=True) # Evaluation result

    quiz = relationship("Quiz", back_populates="quiz_answers")

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created (if they didn't exist).")

