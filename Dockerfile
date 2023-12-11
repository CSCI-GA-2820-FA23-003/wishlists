FROM docker.io/rofrano/nyu-devops-base:fa23

# Create working folder and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN sudo pip install -U pip wheel && \
    sudo pip install --no-cache-dir -r requirements.txt

# Copy the application contents
COPY service/ ./service/

# added this to solve an error complaining about locking the /etc/passwd file
USER root

# Switch to a non-root user
RUN useradd --uid 2000 flask && chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP=service:app
ENV PORT 8000
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "service:app"]