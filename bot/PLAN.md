# Bot Development Plan

## Architecture Overview

The bot follows a clean separation of concerns with testable handlers that work independently of Telegram. This enables offline testing via `--test` mode and ensures the same business logic works in both test and production environments.

## Phase 1: Project Scaffolding (Task 1)
- Create bot directory structure with handlers/, services/, and config modules
- Implement entry point (bot.py) with --test mode support
- Set up pyproject.toml with uv for dependency management
- Create environment configuration system
- Implement placeholder handlers that return simple responses

## Phase 2: Backend Integration (Task 2)
- Develop LMS API client in services/lms_client.py
- Implement health check endpoint integration
- Create score retrieval functionality
- Add error handling and retry logic
- Write unit tests for API clients

## Phase 3: Intent Routing (Task 3)
- Design intent classification system
- Implement command routing logic
- Create natural language query handling
- Add fallback responses for unrecognized queries
- Integrate with LLM for complex queries

## Phase 4: Deployment & Testing
- Configure Docker for bot service
- Set up environment variables on VM
- Implement logging and monitoring
- Create deployment scripts
- Document runbook for maintenance

## Key Design Principles

1. **Testability**: All handlers are pure functions that take input → return output
2. **Separation**: Telegram transport is separate from business logic
3. **Configuration**: Environment variables for all secrets
4. **Error Handling**: Graceful degradation with user-friendly messages
5. **Modularity**: Each feature in its own module for easy maintenance
