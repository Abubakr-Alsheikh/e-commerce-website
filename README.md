# Abubakr Alsheikh's Django Project Portfolio

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

This repository is a comprehensive collection of diverse web applications built within a single Django project. It serves as a portfolio to showcase a wide range of skills, from building a full-featured e-commerce platform to integrating modern AI services and creating interactive UIs with different frontend technologies.

## Featured Applications

This monorepo contains several distinct applications, each with its own set of features and technologies.


### 1. Footwear E-commerce Store (`core` app)
A complete e-commerce website for a shoe store, built with Django and a traditional Bootstrap-based template.

**Live Demo:** [Footwear Store](https://abubakralsheikh.pythonanywhere.com/)

**Features:**
- **Product Catalog:** Browse products by category (Men, Women) or view all products.
- **Product Detail Pages:** View detailed information, images, and customer reviews.
- **User Reviews & Ratings:** Authenticated users can leave reviews and ratings for products.
- **Shopping Cart:** Add/remove items, update quantities, and view order summary.
- **Coupon System:** Apply discount codes to the cart.
- **Checkout Process:** Multi-step checkout with billing and shipping address forms.
- **Stripe Integration:** Dummy payment processing for orders.
- **User Authentication:** Login, logout, and signup functionality using Django All-Auth.
- **Order Management:** View past orders and request refunds.
- **Dynamic Search:** Live search functionality in the navigation bar.

**Tech Stack:** Django, Bootstrap, jQuery, Stripe API, Django Crispy Forms, Django All-Auth.

---

### 2. AskVid - AI Video/Audio Q&A (`ask_yourtube` app)
An innovative tool that allows users to upload video or audio files and interact with their content using AI.

**Live Demo:** [AskVid](https://abubakralsheikh.pythonanywhere.com/askvid/)

**Features:**
- **File Upload:** Upload video or audio files (up to 50MB, 15 min duration).
- **AI Transcription:** Automatically transcribes the content of the uploaded file using **AssemblyAI**.
- **AI Summarization:** Generates a concise summary of the content using **Google's Gemini AI**.
- **Interactive Chat:** Ask questions about the video/audio content and receive answers from the AI.
- **Session History:** View previously uploaded files and their chat history.
- **User-Specific Data:** Uses local storage to maintain a unique user ID and associate files with it.

**Tech Stack:** Django, Google Generative AI (Gemini), AssemblyAI, Bootstrap, JavaScript (Vanilla).

---

### 3. Screen Scene - Movie Browser (`screen_scene` app)
A modern, responsive movie browsing application built with a Tailwind CSS frontend.

**Live Demo:** [Screen Scene](https://abubakralsheikh.pythonanywhere.com/screen-scene/)

**Features:**
- **Movie Discovery:** Browse lists of popular, top-rated, and upcoming movies.
- **Movie Details:** View comprehensive details for each movie, including synopsis, cast, and backdrop images.
- **Search Functionality:** Search for movies by title.
- **User Favorites:** Authenticated users can add or remove movies from their favorites list.
- **API Integration:** Fetches all movie data from **The Movie Database (TMDB) API**.

**Tech Stack:** Django, Tailwind CSS, Flowbite, JavaScript, TheMovieDB API.

---

### 4. Coaching Services Website (`coaching_website` app)
A sleek, professional landing page and booking system for a coaching business.

**Live Demo:** [Coaching Website](https://abubakralsheikh.pythonanywhere.com/coaching_website/)

**Features:**
- **Service & Pricing Plans:** Displays different coaching plans with pricing.
- **Booking Form:** Users can select a plan and fill out a form to request a coaching session.
- **Date & Time Picker:** Schedule appointments with a modern UI.
- **Form Validation:** Ensures all required information is submitted correctly.
- **Admin Notifications:** (Logic included) Sends email notifications upon new requests.

**Tech Stack:** Django, Tailwind CSS, Flowbite.

---

### 5. Zbon Company & Intellido (`zbon_company`, `intellido` apps)
Additional smaller applications demonstrating different layouts and API structures.
- **Zbon Company:** A simple product showcase website.
- **Intellido:** A backend app structured to serve as a REST API using Django REST Framework and JWT for authentication.

## Core Technologies Used

- **Backend:** Django, Django REST Framework
- **Frontend:**
  - Standard Django Templates with Bootstrap & jQuery
  - Modern Django Templates with Tailwind CSS & Flowbite
- **Database:** SQLite
- **APIs & Services:**
  - **Stripe:** Payment Processing
  - **Google Generative AI:** Chat & Summarization
  - **AssemblyAI:** Audio/Video Transcription
  - **The Movie Database (TMDB):** Movie Data
- **Authentication:** Django All-Auth, Django REST Framework Simple JWT
- **Deployment:** Gunicorn, Nginx (on PythonAnywhere)

## Project Structure

```
abubakr-alsheikh-e-commerce-website/
├── core/              # Main E-commerce Application (Footwear Store)
├── ask_yourtube/      # AI Video/Audio Q&A Tool (AskVid)
├── screen_scene/      # Movie & TV Show Browser
├── coaching_website/  # Coaching Service Booking Site
├── zbon_company/      # Simple Company/Product Showcase Site
├── intellido/         # REST API components
├── e_commerce_website/ # Django project settings and main URL configuration
├── static/            # Static assets (CSS, JS, Images)
├── templates/         # Global templates (e.g., for allauth)
├── manage.py
├── requirements.txt
└── tailwind.config.js
```

## Local Setup and Installation

### Prerequisites
- Python 3.8+ and `pip`
- Node.js and `npm` (for Tailwind CSS)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/abubakr-alsheikh-e-commerce-website.git
    cd abubakr-alsheikh-e-commerce-website
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install JavaScript dependencies:**
    ```bash
    npm install
    ```

5.  **Compile Tailwind CSS:**
    Run this command to build the CSS file required for the Tailwind-based apps.
    ```bash
    npx tailwindcss -i ./static/src/input.css -o ./coaching_website/static/src/output.css --watch
    ```
    *(Note: You may need to adjust the output path based on which app's static files you are working on, as per `tailwind.config.js`)*

6.  **Set up environment variables:**
    Create a `.env` file in the project root directory and add your API keys. You can use the example below:
    ```.env
    SECRET_KEY='your-django-secret-key'
    GENAI_API_KEY='your-google-gemini-api-key'
    ASSEMBLYAI_API_KEY='your-assemblyai-api-key'
    THEMOVIEDB_API_KEY='your-tmdb-api-key'
    STRIPE_PUBLIC_KEY='your-stripe-public-key'
    STRIPE_SECRET_KEY='your-stripe-secret-key'
    ```

7.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

8.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

9.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The applications will be available at the following paths:
- **E-commerce Store:** `http://127.0.0.1:8000/`
- **AskVid:** `http://127.0.0.1:8000/askvid/`
- **Screen Scene:** `http://127.0.0.1:8000/screen-scene/`
- **Coaching Website:** `http://127.0.0.1:8000/coaching_website/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

