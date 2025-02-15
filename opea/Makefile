.PHONY: start stop test

# Default target
start:
	@case "$(filter-out $@,$(MAKECMDGOALS))" in \
		ollama) \
			docker-compose up -d --build ollama;; \
		*) \
			docker-compose up -d --build;; \
	esac

# Stop all containers
stop:
	docker-compose down

# Doesn't work yet -> {"error":"model 'llama3.2:1b' not found"}%
test:
	curl --noproxy "*" http://localhost:8008/api/generate -d '{\
		"model": "llama3.2",\
		"prompt":"Why is the sky blue?"\
		}'

# Ignore arguments passed to targets
%:
	@: