# Stage 1: Build the React app
FROM node:20-alpine AS build
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the source code and build
COPY . .
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:stable-alpine
# Copy the build output to replace the default nginx contents.
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]