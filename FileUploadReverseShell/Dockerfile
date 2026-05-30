FROM php:8.2-apache

# Enable Apache mod_rewrite (optional)
RUN a2enmod rewrite

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY . .

# Fix permissions for uploads directory
RUN chown -R www-data:www-data uploads && chmod -R 755 uploads

# Expose port 80 (standard HTTP)
EXPOSE 80

# Run Apache in foreground
CMD ["apache2-foreground"]