FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create the uploads directory (in case it's empty and git doesn't track it)
RUN mkdir -p uploads

# Expose the port Flask runs on
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]