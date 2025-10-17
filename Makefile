# ======================================================================================
# RTFM MK1 Makefile
# ======================================================================================
# "The distance between thought and action, minimized."

# --- Cosmetics ---
RED     := \033[0;31m
GREEN   := \033[0;32m
YELLOW  := \033[1;33m
BLUE    := \033[0;34m
PURPLE  := \033[0;35m
CYAN    := \033[0;36m
NC      := \033[0m

# --- Configuration ---
SHELL := /bin/bash

# Load PROJECT_NAME from env file if it exists and is not empty, otherwise use default
ENV_FILE := infra/env/.env
ENV_TEMPLATE := infra/env/.env.template

-include $(ENV_FILE)
PROJECT_NAME ?= RTFM
PROJECT_DESCRIPTION ?= "Manage Your Gambling Addiction In the Safety Of Your Linux Terminal"
# Stack variant: full (default) or core (minimal)
STACK ?= full
COMPOSE_FILE := infra/docker-compose.yml
COMPOSE_CORE := infra/docker-compose.core.yml

# Select compose file and project name based on STACK
ifeq ($(STACK),core)
    COMPOSE_PROJECT := $(PROJECT_NAME)-core
    COMPOSE := docker compose -f $(COMPOSE_CORE) --env-file $(ENV_FILE) -p $(COMPOSE_PROJECT)
else
    COMPOSE_PROJECT := $(PROJECT_NAME)
    COMPOSE := docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) -p $(COMPOSE_PROJECT)
endif

.DEFAULT_GOAL := help

# --- Phony Targets ---
.PHONY: help setup up down logs logs-manifest logs-runtime logs-arbiter logs-b-line ps build rebuild restart re status clean fclean prune stop ssh exec test test-manifest test-runtime test-integration health sync env-check env-create

# ======================================================================================
# HELP & USAGE
# ======================================================================================
help:
	@echo -e "$(BLUE)========================================================================="
	@echo -e " $(PROJECT_NAME) - $(PROJECT_DESCRIPTION)"
	@echo -e "=========================================================================$(NC)"
	@echo -e "$(CYAN)\"The distance between thought and action, minimized.\"$(NC)"
	@echo ""
	@echo -e "$(YELLOW)Usage: make [target] [STACK=core|full] [service=SERVICE_NAME]$(NC)"
	@echo ""
	@echo -e "$(GREEN)Stack Variants:$(NC)"
	@echo -e "  STACK=full (default)   - Complete stack with Neo4j, Redis, all services"
	@echo -e "  STACK=core             - Minimal stack (Redis, LLM Gateway, Chat Test)"
	@echo ""
	@echo -e "$(GREEN)Quick Start:$(NC)"
	@echo -e "  make up                - Start full stack"
	@echo -e "  make up STACK=core     - Start minimal core stack"
	@echo -e "  make down              - Stop all services"
	@echo -e "  make restart           - Restart all services"
	@echo ""
	@echo -e "$(GREEN)Core Stack Management:$(NC)"
	@echo -e "  build [service=<name>]     - Build service images (cached)."
	@echo -e "  rebuild [service=<name>]   - Rebuild service images (no-cache)."
	@echo -e "  re                         - Rebuild and restart (cached)."
	@echo -e "  rere                       - Rebuild and restart (no-cache)."
	@echo ""
	@echo -e "$(GREEN)Monitoring & Debugging:$(NC)"
	@echo -e "  status [service=<name>]    - Show status of services (Alias: ps)."
	@echo -e "  logs [service=<name>]      - Follow logs (all or specific service)."
	@echo -e "  logs-manifest              - Follow manifest ingestion service logs."
	@echo -e "  logs-runtime               - Follow runtime executor service logs."
	@echo -e "  logs-arbiter               - Follow C++ arbiter core logs."
	@echo -e "  logs-b-line                - Follow B-Line dashboard logs."
	@echo -e "  ssh service=<name>         - Get interactive shell into service."
	@echo -e "  exec svc=<name> cmd=\"<cmd>\" - Execute command in service."
	@echo -e "  health                     - Check health of all services."
	@echo ""
	@echo -e "$(GREEN)Environment:$(NC)"
	@echo -e "  env-check                  - Check if .env file exists"
	@echo -e "  env-create                 - Create .env from template"
	@echo ""
	@echo -e "$(GREEN)Manifest Operations:$(NC)"
	@echo -e "  sync                       - Force sync manifests from filesystem."
	@echo -e "  validate                   - Validate all manifests."
	@echo ""
	@echo -e "$(GREEN)CLI Chat Client:$(NC)"
	@echo -e "  cli-chat MANIFEST=<path>   - Start interactive CLI chat with agent."
	@echo ""
	@echo -e "$(GREEN)Testing & Validation:$(NC)"
	@echo -e "  test                       - Run all test suites."
	@echo -e "  test-manifest              - Test manifest ingestion service."
	@echo -e "  test-runtime               - Test runtime executor service."
	@echo -e "  test-integration           - Run integration tests."
	@echo ""
	@echo -e "$(GREEN)Cleaning & Pruning:$(NC)"
	@echo -e "  clean                      - Stop services and remove containers."
	@echo -e "  fclean                     - Stop services, remove containers and volumes."
	@echo -e "  prune                      - Ultimate clean: fclean + system prune."
	@echo ""
	@echo -e "$(YELLOW)Examples:$(NC)"
	@echo -e "  make up STACK=core         - Start minimal stack for development"
	@echo -e "  make logs service=llm_gateway - View LLM gateway logs"
	@echo -e "  make rebuild service=chat_test - Rebuild chat test service"
	@echo -e "  make cli-chat MANIFEST=std/manifests/agents/assistant/agent.yml - Chat with assistant"
	@echo ""
	@echo -e "$(YELLOW)The Great Work continues...$(NC)"
	@echo -e "$(BLUE)=========================================================================$(NC)"

# ======================================================================================
# ENVIRONMENT MANAGEMENT
# ======================================================================================
env-check:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo -e "$(RED)❌ Environment file not found: $(ENV_FILE)$(NC)"; \
		echo -e "$(YELLOW)Run 'make env-create' to create from template$(NC)"; \
		exit 1; \
	else \
		echo -e "$(GREEN)✅ Environment file exists: $(ENV_FILE)$(NC)"; \
	fi

env-create:
	@if [ -f "$(ENV_FILE)" ]; then \
		echo -e "$(YELLOW)⚠️  Environment file already exists: $(ENV_FILE)$(NC)"; \
		echo -e "$(YELLOW)Remove it first if you want to recreate from template$(NC)"; \
	else \
		cp "$(ENV_TEMPLATE)" "$(ENV_FILE)"; \
		echo -e "$(GREEN)✅ Created $(ENV_FILE) from template$(NC)"; \
		echo -e "$(YELLOW)⚠️  Remember to update your API keys in $(ENV_FILE)$(NC)"; \
	fi

# ======================================================================================
# QUICK START
# ======================================================================================
setup: env-check build up
	@echo -e "$(GREEN)✅ Cortex-Prime MK1 initialized and running.$(NC)"
	@echo -e "$(CYAN)Stack: $(STACK)$(NC)"
	@if [ "$(STACK)" = "core" ]; then \
		echo -e "$(CYAN)Chat Test: http://localhost:8888$(NC)"; \
		echo -e "$(CYAN)LLM Gateway: http://localhost:8081$(NC)"; \
	else \
		echo -e "$(CYAN)Manifest Ingestion: http://localhost:8082/docs$(NC)"; \
		echo -e "$(CYAN)Runtime Executor: http://localhost:8083/docs$(NC)"; \
	fi

# ======================================================================================
# CORE STACK MANAGEMENT
# ======================================================================================
up: env-check
	@echo -e "$(GREEN)🚀 Igniting Cortex-Prime MK1 [$(STACK) stack]...$(NC)"
	@$(COMPOSE) up -d --remove-orphans
	@echo -e "$(GREEN)✅ Services are now running in detached mode.$(NC)"
	@echo -e "$(YELLOW)Run 'make status' to see running services$(NC)"

down:
	@echo -e "$(RED)🛑 Shutting down Cortex-Prime MK1 [$(STACK)]...$(NC)"
	@$(COMPOSE) down --remove-orphans --timeout 5

stop:
	@echo -e "$(RED)⚡ Force stopping all $(COMPOSE_PROJECT) services...$(NC)"
	@docker ps -a --filter "name=$(COMPOSE_PROJECT)" --format "{{.Names}}" | xargs -r docker stop -t 2 2>/dev/null || true
	@docker ps -a --filter "name=$(COMPOSE_PROJECT)" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true
	@echo -e "$(GREEN)✅ All services forcefully stopped.$(NC)"

restart: down up

re: down build up
	@echo -e "$(GREEN)♻️  Stack rebuilt and restarted.$(NC)"

rere: down rebuild up
	@echo -e "$(GREEN)♻️  Stack rebuilt (no-cache) and restarted.$(NC)"

# ======================================================================================
# BUILDING IMAGES
# ======================================================================================
build:
	@echo -e "$(BLUE)🔨 Building images for $(or $(service),all services)...$(NC)"
	@$(COMPOSE) build $(service)

rebuild:
	@echo -e "$(YELLOW)🔨 Force-rebuilding (no cache) for $(or $(service),all services)...$(NC)"
	@$(COMPOSE) build --no-cache $(service)

# ======================================================================================
# MONITORING & DEBUGGING
# ======================================================================================
status:
	@echo -e "$(BLUE)📊 System Status Report:$(NC)"
	@$(COMPOSE) ps $(service)
ps: status

logs:
	@echo -e "$(BLUE)📜 Streaming logs for $(or $(service),all services)...$(NC)"
	@$(COMPOSE) logs -f --tail="100" $(service)

logs-manifest:
	@echo -e "$(CYAN)📜 Streaming Manifest Ingestion logs...$(NC)"
	@$(COMPOSE) logs -f --tail="100" manifest_ingestion

logs-runtime:
	@echo -e "$(CYAN)📜 Streaming Runtime Executor logs...$(NC)"
	@$(COMPOSE) logs -f --tail="100" runtime_executor

logs-arbiter:
	@echo -e "$(CYAN)📜 Streaming C++ Arbiter Core logs...$(NC)"
	@$(COMPOSE) logs -f --tail="100" agent-lib || echo -e "$(YELLOW)⚠️  Arbiter service not yet configured$(NC)"

logs-b-line:
	@echo -e "$(CYAN)🎨 Streaming B-Line Dashboard logs...$(NC)"
	@$(COMPOSE) logs -f --tail="100" b_line

ssh:
	@if [ -z "$(service)" ]; then \
		echo -e "$(RED)❌ Error: Service name required. Usage: make ssh service=<name>$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)🔌 Connecting to $(service)...$(NC)"
	@$(COMPOSE) exec $(service) /bin/bash || $(COMPOSE) exec $(service) /bin/sh

exec:
	@if [ -z "$(svc)" ] || [ -z "$(cmd)" ]; then \
		echo -e "$(RED)❌ Error: Service and command required. Usage: make exec svc=<name> cmd=\"<cmd>\"$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)⚡ Executing in $(svc): $(cmd)$(NC)"
	@$(COMPOSE) exec $(svc) $(cmd)

health:
	@echo -e "$(BLUE)🏥 Checking service health...$(NC)"
	@echo ""
	@echo -e "$(CYAN)Manifest Ingestion:$(NC)"
	@curl -s http://localhost:8082/health | jq . || echo -e "$(RED)❌ Service unreachable$(NC)"
	@echo ""
	@echo -e "$(CYAN)Runtime Executor:$(NC)"
	@curl -s http://localhost:8083/health | jq . || echo -e "$(YELLOW)⚠️  Service not running$(NC)"

# ======================================================================================
# CLI CHAT CLIENT
# ======================================================================================
cli-chat:
	@echo -e "$(CYAN)💬 Starting Cortex-CLI Chat Client...$(NC)"
	@if [ -z "$(MANIFEST)" ]; then \
		echo -e "$(RED)Error: MANIFEST variable required$(NC)"; \
		echo -e "$(YELLOW)Usage: make cli-chat MANIFEST=path/to/agent.yml$(NC)"; \
		echo -e "$(YELLOW)Example: make cli-chat MANIFEST=std/manifests/agents/assistant/agent.yml$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d "venv" ]; then \
		echo -e "$(YELLOW)Creating virtual environment...$(NC)"; \
		python3 -m venv venv; \
		. venv/bin/activate && pip install -q httpx httpx-sse; \
	fi
	@. venv/bin/activate && python3 scripts/cortex-cli -m $(MANIFEST)

# ======================================================================================
# MANIFEST OPERATIONS
# ======================================================================================
sync:
	@echo -e "$(PURPLE)🔄 Syncing manifests from filesystem...$(NC)"
	@curl -s -X POST http://localhost:8082/registry/sync | jq .

validate:
	@echo -e "$(PURPLE)✓ Validating all manifests...$(NC)"
	@curl -s http://localhost:8082/registry/status | jq .

# ======================================================================================
# TESTING & VALIDATION
# ======================================================================================
test: test-manifest test-runtime
	@echo -e "$(GREEN)✅ All test suites completed.$(NC)"

test-manifest:
	@echo -e "$(PURPLE)🧪 Running Manifest Ingestion tests...$(NC)"
	@docker run --rm -v $$(pwd)/services/manifest_ingestion:/app -w /app \
		$(PROJECT_NAME)-manifest_ingestion \
		python -m pytest tests/ -v --tb=short

test-runtime:
	@echo -e "$(PURPLE)🧪 Running Runtime Executor tests...$(NC)"
	@echo -e "$(YELLOW)⚠️  Runtime executor tests not yet implemented$(NC)"

test-integration:
	@echo -e "$(PURPLE)🧪 Running integration tests...$(NC)"
	@./scripts/run_tests.sh || echo -e "$(YELLOW)⚠️  Test script not found$(NC)"

# ======================================================================================
# CLEANING & PRUNING
# ======================================================================================
clean:
	@echo -e "$(RED)🧹 Cleaning containers and networks...$(NC)"
	@$(COMPOSE) down --remove-orphans

fclean:
	@echo -e "$(RED)🧹 Deep cleaning containers, networks, and volumes...$(NC)"
	@$(COMPOSE) down --volumes --remove-orphans
	@echo -e "$(GREEN)✅ Deep clean complete.$(NC)"

prune: fclean
	@echo -e "$(RED)💥 Executing ultimate prune sequence...$(NC)"
	@docker system prune -af --volumes
	@docker builder prune -af
	@echo -e "$(GREEN)✅ Full system prune complete.$(NC)"

stop: down
