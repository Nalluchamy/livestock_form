#!/bin/bash
# Clean script for ELHGS

echo "Cleaning up ELHGS environment..."

docker-compose down -v
rm -f .env

echo "Cleanup complete."
