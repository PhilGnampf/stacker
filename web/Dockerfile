# Use the official Node.js image
FROM node:latest

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the source code
COPY . .

# Build the Vite project
RUN npm run build

# Install a simple web server to serve the built files
RUN npm install -g serve

# Expose port 5000 (or any port you prefer)
EXPOSE 5000

# Command to run the application
CMD ["serve", "-s", "dist", "-l", "5000"]
