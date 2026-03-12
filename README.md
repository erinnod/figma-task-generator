# Figma → Development Task Generator

> An AI system that transforms Figma design files into structured
> engineering task breakdowns using LLM reasoning.

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## What It Does

[Short paragraph — fill in as you build]

## Architecture

[Link to ARCHITECTURE.md]

## Demo

[Screenshot / GIF — add in Phase 9]

## Quick Start

[Fill in during Phase 2]

## Project Structure

[Fill in during Phase 2]

## Development Log

[Link to DEVELOPMENT_LOG.md]

## Requirements explanation

fastapi - Web framework. Handles HTTP requests, routing, and automatic documentation.

uvicorn — The server that runs FastAPI. FastAPI is the framework, uvicorn is the engine that serves it.

httpx — A modern HTTP client for Python. This will be used to call the Figma API. Better than requests because it supports async.

python-dotenv — Reads the .env file and loads API keys as environment variables.

pydantic — Data validation library. Defines the shape of the data as Python classes and Pydantic enforces it. FastAPI is built on top of this.

anthropic — The official Python SDK for Claude (Anthropic's LLM). This is the primary LLM client.

openai — The official OpenAI SDK. Installing both so the system can switch between providers.
