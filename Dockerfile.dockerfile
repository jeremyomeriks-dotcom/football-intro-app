# Use Nginx as base image
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy all HTML files to nginx directory
COPY *.html /usr/share/nginx/html/

# Copy nginx configuration (optional - using default)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]