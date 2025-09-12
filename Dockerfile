# Production Dockerfile with nginx
FROM python:3.12-slim

# Install Node.js and nginx
RUN apt-get update && apt-get install -y curl nginx && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy Poetry configuration
COPY pyproject.toml ./
COPY poetry.lock* ./

# Copy everything
COPY . ./

# Install dependencies
RUN poetry install
RUN cd front && npm install

# Build frontend
RUN cd front && npm run build

# Configure nginx
RUN rm -rf /var/www/html/*
RUN cp -r front/build/client/* /var/www/html/

# Create nginx configuration
RUN echo 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /var/www/html;\n\
    index index.html;\n\
    \n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass http://localhost:8000;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Expose ports
EXPOSE 80 8000

# Start both nginx and the Python backend
CMD service nginx start && poetry run poe start
