FROM python:3.12

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./
COPY ./libs ./libs
RUN pip install -r requirements.txt

# Bundle app source
COPY ./ /app

WORKDIR /app/source
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]