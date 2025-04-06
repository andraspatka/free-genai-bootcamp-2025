from sqlalchemy.orm import Session
from ..database.models import Story, Quiz, QuizAnswer
from ..database.session import get_db # Context manager for session
from .schemas import (
    CreateStoryInputSchema, CreateStoryOutputSchema,
    CreateQuizInputSchema, CreateQuizOutputSchema,
    CreateQuizAnswerInputSchema, CreateQuizAnswerOutputSchema,
    GetStoryInputSchema, GetStoryOutputSchema, StorySchema,
    # Add other schemas as needed
)
import logging
import uuid
from typing import List

logger = logging.getLogger(__name__)

# --- Create Operations ---

def create_story(input_data: CreateStoryInputSchema) -> CreateStoryOutputSchema:
    """Creates a new story record in the database."""
    logger.info(f"Creating story for topic: {input_data.topic}")
    db_story = Story(
        topic=input_data.topic,
        story=input_data.story,
        image=input_data.image_s3_path,
        audio=input_data.audio_s3_path
    )
    try:
        with get_db() as db:
            db.add(db_story)
            db.commit()
            db.refresh(db_story)
            logger.info(f"Successfully created story with ID: {db_story.id}")
            return CreateStoryOutputSchema(story_id=db_story.id, topic=db_story.topic)
    except Exception as e:
        logger.error(f"Error creating story: {e}", exc_info=True)
        # In a real app, might want to raise a specific DB error
        return CreateStoryOutputSchema(story_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), topic="Error") # Indicate failure

def create_quiz(input_data: CreateQuizInputSchema) -> CreateQuizOutputSchema:
    """Creates a new quiz record linked to a story."""
    logger.info(f"Creating quiz for story ID: {input_data.story_id}")
    db_quiz = Quiz(
        story_id=input_data.story_id,
        question=input_data.question,
        answer=input_data.answer
    )
    try:
        with get_db() as db:
            # Optional: Verify story_id exists first
            story = db.query(Story).filter(Story.id == input_data.story_id).first()
            if not story:
                 logger.error(f"Cannot create quiz, Story with ID {input_data.story_id} not found.")
                 # Indicate failure
                 return CreateQuizOutputSchema(quiz_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), story_id=input_data.story_id)

            db.add(db_quiz)
            db.commit()
            db.refresh(db_quiz)
            logger.info(f"Successfully created quiz with ID: {db_quiz.id}")
            return CreateQuizOutputSchema(quiz_id=db_quiz.id, story_id=db_quiz.story_id)
    except Exception as e:
        logger.error(f"Error creating quiz: {e}", exc_info=True)
        return CreateQuizOutputSchema(quiz_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), story_id=input_data.story_id) # Indicate failure

def create_quiz_answer(input_data: CreateQuizAnswerInputSchema) -> CreateQuizAnswerOutputSchema:
    """Creates a record for a user's answer to a quiz question."""
    logger.info(f"Creating quiz answer for quiz ID: {input_data.quiz_id}")
    db_quiz_answer = QuizAnswer(
        quiz_id=input_data.quiz_id,
        answer=input_data.user_answer,
        is_correct=input_data.is_correct # Can be null initially
    )
    try:
        with get_db() as db:
             # Optional: Verify quiz_id exists first
            quiz = db.query(Quiz).filter(Quiz.id == input_data.quiz_id).first()
            if not quiz:
                 logger.error(f"Cannot create quiz answer, Quiz with ID {input_data.quiz_id} not found.")
                 # Indicate failure
                 return CreateQuizAnswerOutputSchema(quiz_answer_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), quiz_id=input_data.quiz_id)

            db.add(db_quiz_answer)
            db.commit()
            db.refresh(db_quiz_answer)
            logger.info(f"Successfully created quiz answer with ID: {db_quiz_answer.id}")
            return CreateQuizAnswerOutputSchema(quiz_answer_id=db_quiz_answer.id, quiz_id=db_quiz_answer.quiz_id)
    except Exception as e:
        logger.error(f"Error creating quiz answer: {e}", exc_info=True)
        return CreateQuizAnswerOutputSchema(quiz_answer_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), quiz_id=input_data.quiz_id) # Indicate failure

# --- Read Operations ---

def get_stories(input_data: GetStoryInputSchema) -> GetStoryOutputSchema:
    """Retrieves stories from the database based on ID or topic."""
    logger.info(f"Querying stories with criteria: {input_data}")
    try:
        with get_db() as db:
            query = db.query(Story)
            if input_data.story_id:
                query = query.filter(Story.id == input_data.story_id)
            elif input_data.topic:
                # Use ilike for case-insensitive matching, adjust if exact match needed
                query = query.filter(Story.topic.ilike(f"%{input_data.topic}%"))
            else:
                # Maybe limit results if no criteria specified, or return error
                 logger.warning("No criteria specified for get_stories, returning empty list.")
                 return GetStoryOutputSchema(stories=[])

            results = query.all()
            logger.info(f"Found {len(results)} stories matching criteria.")
            # Convert SQLAlchemy models to Pydantic schemas
            output_stories = [StorySchema.from_orm(story) for story in results]
            return GetStoryOutputSchema(stories=output_stories)

    except Exception as e:
        logger.error(f"Error retrieving stories: {e}", exc_info=True)
        return GetStoryOutputSchema(stories=[])

# --- Add get_quiz, get_quiz_answer functions similarly ---
# --- Add Update/Delete operations as needed ---

# Example Usage (for testing, requires DB setup and potentially data)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # 1. Create a story
    story_input = CreateStoryInputSchema(topic="Test Topic", story="This is a test story.")
    story_output = create_story(story_input)
    print(f"Created Story: {story_output.model_dump_json(indent=2)}")

    if story_output.topic != "Error":
        story_id = story_output.story_id

        # 2. Create a quiz for the story
        quiz_input = CreateQuizInputSchema(
            story_id=story_id,
            question="What is the topic?",
            answer="Test Topic"
        )
        quiz_output = create_quiz(quiz_input)
        print(f"Created Quiz: {quiz_output.model_dump_json(indent=2)}")

        if quiz_output.story_id == story_id: # Check if creation seemed successful
            quiz_id = quiz_output.quiz_id

            # 3. Create a quiz answer
            answer_input = CreateQuizAnswerInputSchema(
                quiz_id=quiz_id,
                user_answer="Test Topic",
                is_correct=True
            )
            answer_output = create_quiz_answer(answer_input)
            print(f"Created Quiz Answer: {answer_output.model_dump_json(indent=2)}")

        # 4. Retrieve the story by topic
        get_input_topic = GetStoryInputSchema(topic="Test Topic")
        get_output_topic = get_stories(get_input_topic)
        print(f"Get Story by Topic: {get_output_topic.model_dump_json(indent=2)}")

        # 5. Retrieve the story by ID
        get_input_id = GetStoryInputSchema(story_id=story_id)
        get_output_id = get_stories(get_input_id)
        print(f"Get Story by ID: {get_output_id.model_dump_json(indent=2)}")
    else:
        print("Skipping dependent tests due to story creation failure.")


