# Final project

## Business use case

- Create an agent which is capable of generating out learning exercises for language learning
- The agent would have a set of tools at its disposal and could decide what sort of exercise to generate
- The agent should be able to generate exercises in a variety of languages
- The agent should be able to generate exercises for a variety of learning styles (e.g. reading, writing, speaking, listening)
- The agent should be able to generate exercises which are relevant to the user's current context (e.g. user is a student learning a new subject, the exercise should be about that subject)

## Technical specification

- AI Agent with a list of tools: 
  - Duckduckgo search
  - Website text getter
  - Youtube transcript downloader, structurizer
  - Text to speech converter
  - Text to image converter
- Use self hosted solutions for the GenAI tools wherever possible and practical
- The UI should be minimal and flexible. It should contain a set of parts which could be used by the agent for the exercise (image view, audio stream, text box, etc.) 

### Examples of exercises

Easy difficulty:
- Generate out a random English sentence and ask for the translation in Italian. Evaluate the translation and give feedback

Medium difficulty:
- Search for a listening exercises about a topic that the user is learning about on youtube. Download the transcript and structure it. After that generate out the listening exercise using text to speech. Lastly generate out a quiz with a number of questions based on the listening exercise. Save the transcript in the database, the text to speech audio on AWS S3 and the quiz in the database.

Hard difficulty:
- Generate a short story about a topic that the user is learning about. The story should be short and concise. Generate an image which encompasses the story. Save the story in the database, the image on AWS S3. Return the image to the user and ask them to describe the image in Italian. Evaluate their description and give them feedback.

### Agent final output format

- The agent's output should be a JSON object with the following fields: 
  - exerciseType: string (required)
  - difficulty: string (required)
  - text: string containing the exercise (optional)
  - image: string containing the path in S3 to the image (optional)
  - audio: string containing the path in S3 to the audio (optional)
