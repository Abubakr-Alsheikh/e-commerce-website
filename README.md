# Sama Media - Dynamic Portfolio Website

![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

This repository contains the source code for a dynamic portfolio website for **Sama Media**, a graphic design and advertising services company. The project includes a public-facing website to showcase services and a full-featured admin dashboard for content management.

This project was developed as a graduation project for the Institute of Computer Technology, Aleppo University.

## Table of Contents

- [Features](#features)
  - [Public Website](#public-website)
  - [Admin Dashboard](#admin-dashboard)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Admin Credentials](#admin-credentials)
- [Configuration](#configuration)
- [Author](#author)

## Features

### Public Website

- **Homepage:** A welcoming landing page with an introduction to the company and a preview of the latest projects.
- **Services:** A detailed page describing the company's offerings, including design, printing, and execution.
- **Projects Gallery:** A dynamic, interactive gallery (using Swiper.js) to showcase the company's portfolio.
- **Clients/Customers:** A page displaying the logos of companies Sama Media has worked with.
- **Team Page:** Introduces the core team members.
- **Contact Form:** A functional contact form that stores user messages directly into the database.
- **Responsive Design:** Ensures a seamless experience on all devices, from desktops to mobile phones.
- **Social Media Integration:** Easy-to-access links to the company's social media profiles.

### Admin Dashboard

- **Secure Login:** The dashboard is protected by a username and password authentication system.
- **Content Management (CRUD):**
  - **Projects:** Add, edit, and delete projects, including image uploads.
  - **Customers:** Add, edit, and delete client information, including their logos.
  - **Team:** Add, edit, and delete team members, with support for image uploads and gender-specific default avatars.
- **Message Management:** View and delete messages received from the public website's contact form.
- **Dashboard Home:** An overview page displaying the latest messages and a form to change the admin password.

## Technology Stack

- **Backend:** PHP
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript
- **Libraries:**
  - [Swiper.js](https://swiperjs.com/) for the projects gallery slider.
  - [Font Awesome](https://fontawesome.com/) for icons.
- **Development Environment:** XAMPP (or any Apache/MySQL/PHP stack)

## Project Structure

The project is organized into a clear and maintainable structure.

```
└── sama-media-website/
    ├── dashboard/        # Admin panel files (CRUD operations, login, etc.)
    ├── scripts/          # JavaScript files (for both public site and dashboard)
    ├── styles/           # CSS stylesheets
    ├── webfonts/         # Font Awesome font files
    ├── conn.php          # Database connection file
    ├── index.php         # Main homepage
    ├── services.php      # Services page
    ├── projects.php      # Projects page
    ├── customers.php     # Customers page
    ├── team.php          # Team page
    ├── contact.php       # Contact page and form handler
    ├── samadata.sql      # Database dump file
    ├── .htaccess         # Apache configuration for clean URLs and security
    └── ...
```
