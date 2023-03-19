FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Install dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the code into the container
COPY . .

# Start the application
CMD [ "python", "main.py", "--rm" ]
