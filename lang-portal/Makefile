.PHONY: start stop

# Default target
start:
ifeq ($(filter $(firstword $(MAKECMDGOALS)), backend frontend),)
	docker-compose up --build
else ifeq ($(firstword $(MAKECMDGOALS)), backend)
	docker-compose up --build api
else ifeq ($(firstword $(MAKECMDGOALS)), frontend)
	docker-compose up --build frontend
endif

# Stop all containers
stop:
	docker-compose down

# Ignore arguments passed to targets
%:
	@: