.PHONY: start stop

# Default target
start:
	@case "$(filter-out $@,$(MAKECMDGOALS))" in \
		backend) \
			docker-compose up --build api;; \
		frontend) \
			docker-compose up --build frontend;; \
		*) \
			docker-compose up --build;; \
	esac

# Stop all containers
stop:
	docker-compose down

# Ignore arguments passed to targets
%:
	@: