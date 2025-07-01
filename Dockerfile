FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script source code
COPY src ./src

# Set the entrypoint to your python script
ENTRYPOINT ["python", "src/scrape_books.py"]