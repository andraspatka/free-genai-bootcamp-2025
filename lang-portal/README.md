# Lang Portal Homework Week 1

The following activities were carried out:
- Converted seed data from japenese to italian using Cursor
- Missing endpoints implemented in backend-flask
- Technical Specs were reviewed and made more consistent (BackendTechnicalSpecs.md, FrontendTechnicalSpecs.md). They are however still too inconsistent so this is put on hold at the moment
- Attempt made to generate golang backend using Windsurf, somewhat successful. The tech spec inconsistencies were reflected in the code as well. See `prompts` directory for more information on the prompting used
- Dockerized lang portal using Cursor. Impressive results, but needed some tweaks
- Wrote API tests for backend-flask
- Tried out Cursor at first but transitioned to use Windsurf as it was more developer friendly from my PoV

# Dockerized lang portal

Start up the applications like so:

```
# Start both services
make start

# Start only backend
make start backend

# Start only frontend
make start frontend

# Stop all services
make stop

```