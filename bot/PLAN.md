# Bot Development Plan

## Overview
This bot provides a Telegram interface for the LMS (Learning Management System) backend.
It allows students to query their scores, check lab availability, and monitor backend health.

## Task 1: Scaffold
Set up the project structure with a testable handler architecture.
Handlers are plain functions separated from the Telegram transport layer.
The --test mode allows running commands without connecting to Telegram.

## Task 2: Backend Integration
Implement real API calls to the LMS backend.
The /scores command will fetch actual scores from the backend.
The /labs command will list available labs from the database.
The /health command checks backend availability via HTTP.

## Task 3: Intent Routing
Add natural language understanding using the Qwen LLM API.
Users can type free-form messages like "what labs are available" and the bot
will route them to the correct handler using LLM-based intent classification.

## Task 4: Deployment
Deploy the bot as a Docker container on the VM.
Add bot service to docker-compose.yml.
Configure environment variables via .env.bot.secret.
Ensure the bot restarts automatically on failure.

## Architecture
- bot.py — entry point, Telegram polling and --test mode
- handlers/ — plain functions, no Telegram dependency
- services/ — API client for LMS backend, LLM client
- config.py — environment variable loading
