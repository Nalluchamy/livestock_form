#!/bin/bash
# Setup script for ELHGS (Linux/macOS)

echo "Setting up Explainable Livestock Health Grading System..."

# Copy environment variables
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Scaffolding complete. Run 'docker-compose up -d' to start the placeholder services."
