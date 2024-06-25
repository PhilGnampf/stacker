# Use the official Golang image to build and run the Go application
FROM golang:latest

# Set the current working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum files
COPY go.mod ./

# Copy the source code
COPY . .

# Build the Go app
RUN go build -o api .

# Expose port 9090 to the outside world
EXPOSE 9090

# Command to run the executable
CMD ["./api"]
