.PHONY: start stop

# Default target
start:
	mkdir -p exports
	docker-compose up -d --build
	docker exec -it ollama-server ollama pull llama3.2:1b

# Stop all containers
stop:
	docker-compose down
