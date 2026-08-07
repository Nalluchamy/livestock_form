# Setup script for ELHGS (Windows PowerShell)

Write-Host "Setting up Explainable Livestock Health Grading System..."

# Copy environment variables
if (-not (Test-Path .env)) {
    Write-Host "Creating .env from .env.example..."
    Copy-Item .env.example .env
}

Write-Host "Scaffolding complete. Run 'docker-compose up -d' to start the placeholder services."
