#Python Image
FROM python:3.13

# Working directory inside the container
WORKDIR /app

# Requirements for server
COPY requirements.txt .

# Installataion of python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the project files to this container
COPY . .

# CMD instructions - what Docker should run when container starts
CMD ["uvicorn", "serve.app:app", "--host", "0.0.0.0", "--port", "8000"]
