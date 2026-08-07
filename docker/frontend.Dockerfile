# Scaffolding for Frontend Dockerfile (Phase 1)
# Targeting Node.js, React + Vite

FROM node:20-alpine

WORKDIR /app

# Copy package management files (placeholder)
# COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies (placeholder)
# RUN npm ci

# Copy application code
# COPY frontend/ /app/

# Expose Vite dev port
EXPOSE 5173
EXPOSE 3000

# Placeholder CMD for Vite dev server
# CMD ["npm", "run", "dev", "--", "--host"]
CMD ["echo", "Frontend container placeholder running..."]
