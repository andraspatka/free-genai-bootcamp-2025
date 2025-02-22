.PHONY: start stop test pull test-text2sql

# Default target
start:
	cd .. && git submodule init && git submodule update && cd -
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

test:
	curl --noproxy "*" http://localhost:8008/api/generate -d '{\
		"stream": false,\
		"model": "llama3.2:1b",\
		"prompt":"Why is the sky blue?"\
		}'

test-text2sql:
	# curl --location http://localhost:9090/v1/postgres/health \
	# --header 'Content-Type: application/json' \
	# --data '{"user": "'postgres'","password": "'postgres'","host": "'localhost'", "port": "5442", "database": "'postgres'"}'
	curl http://localhost:9090/v1/text2sql\
		-X POST \
		-d '{"input_text": "Find the total number of Albums.","conn_str": {"user": "'postgres'","password": "'postgres'","host": "'postgres'", "port": "5432", "database": "'postgres'"}}' \
		-H 'Content-Type: application/json'

pull:
	curl http://localhost:8008/api/pull -d '{\
  		"model": "$(filter-out $@,$(MAKECMDGOALS))"\
	}'

# Ignore arguments passed to targets
%:
	@: