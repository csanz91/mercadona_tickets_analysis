# Use the official Node.js image as the base image
FROM node:20.10-bookworm-slim AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./source/package*.json ./

# Install dependencies and recreate package-lock.json
RUN npm install

# Copy the rest of the application
COPY ./source /app

# Build the application
RUN npm run build

FROM node:20.10-bookworm-slim

WORKDIR /app
COPY --from=build /app .
# ENV HOST is not though you can uncomment if if needed
ENV HOST=0.0.0.0
ENV PORT=80
EXPOSE 80

CMD ["node", "build"]
