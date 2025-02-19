.PHONY: start stop test pull

# Default target
start:
	@case "$(filter-out $@,$(MAKECMDGOALS))" in \
		ollama) \
			docker-compose up -d --build ollama;; \
		*) \
			docker-compose up -d --build;; \
	esac
	docker exec -it ollama-server ollama pull llama3.2:1b

# Stop all containers
stop:
	docker-compose down

# Doesn't work yet -> {"error":"model 'llama3.2:1b' not found"}%
test:
	curl --noproxy "*" http://localhost:8008/api/generate -d '{\
		"stream": false,\
		"model": "llama3.2:1b",\
		"prompt":"Why is the sky blue?"\
		}'

pull:
	curl http://localhost:8008/api/pull -d '{\
  		"model": "$(filter-out $@,$(MAKECMDGOALS))"\
	}'

# Ignore arguments passed to targets
%:
	@: