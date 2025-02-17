# THE WANDERLIST

#### Video Demo: <https://youtu.be/MxRewLwK2Cw>

#### Description:

# The Wanderlist: AI-Powered Travel Planning & Music Curation

## Project Overview

The Wanderlist is a web application that revolutionizes the travel planning experience by combining intelligent itinerary generation with personalized music curation. Born from the observation that trip planning often involves hours of research across multiple platforms, The Wanderlist streamlines this process by offering a unique solution that not only plans your journey but enhances it through carefully curated musical accompaniment.

The application leverages OpenAI's GPT-4 model and Spotify's API to transform simple user inputs - location, mood, activity preferences, and budget - into comprehensive travel itineraries with matching playlists. What sets The Wanderlist apart is its innovative approach to travel planning, understanding that the perfect trip is not just about the destinations and activities, but also about the atmosphere and emotions that accompany the journey.

## Project Structure

```
wanderlist/
├── static/                      # Static assets directory
│   ├── apple-touch-icon.png
│   ├── favicon.ico
│   ├── favicon.svg
│   ├── logo.svg
│   ├── logo-white.svg
│   ├── site.webmanifest
│   ├── travel-accessories.mp4
│   └── web-app-manifest-*.png
├── templates/                   # Jinja2 HTML templates
│   ├── layout.html             # Base template with common elements
│   ├── homepage.html           # Main landing page
│   ├── login.html             # User authentication
│   ├── signup.html            # User registration
│   ├── questions.html         # Travel preference form
│   ├── answer.html            # Results display
│   ├── forgot.html            # Password recovery
│   └── reset.html             # Password reset
├── app.py                      # Main Flask application
└── requirements.txt            # Project dependencies
```

## Technical Architecture

### Frontend Implementation

The frontend of The Wanderlist features a modern, responsive design implemented with:

- HTML5 for structural elements and semantic markup
- Tailwind CSS for styling, with a custom gradient background (blue-300 to purple-200)
- Font Awesome icons for enhanced visual elements
- Custom SVG assets for branding (logo and favicon)
- Responsive meta tags for mobile optimization

The frontend uses Jinja2 templating with a base `layout.html` that includes:

- Viewport configuration for responsive design
- Font Awesome integration
- Favicon setup
- Consistent header with navigation
- Dynamic session handling for authentication state

### Backend Structure

The backend was built using Python and Flask, utilizing several key APIs and services:

1. **Main Application (app.py)**:

   - Implements user authentication with secure password hashing
   - Uses Flask-Session for server-side session management
   - Integrates OpenAI's GPT-4 for intelligent travel recommendations
   - Implements Spotify API integration for playlist generation
   - Includes email functionality through Resend for password reset features
   - Manages persistent user sessions with remember-me functionality using cookies

2. **Database Management**:

   - Utilizes SQLite for data persistence
   - Implements user authentication tables with secure password hashing
   - Stores temporary reset codes for password recovery

3. **Authentication System**:
   - Custom implementation of user registration and login
   - Secure password reset flow with email verification
   - Remember-me functionality with secure cookie handling

## Design Decisions and Challenges

### UI/UX Design

The application features a carefully crafted user interface with:

- A gradient background from blue-300 to purple-200 for visual appeal
- Consistent branding with custom SVG logos
- Mobile-first responsive design
- Clear navigation and user feedback
- Smooth transitions and animations
- Progressive form submission for travel preferences

### Framework Selection

The decision to use Flask over other frameworks like Django was deliberate. While Django offers more built-in functionality, Flask's lightweight nature and flexibility better suited the project's needs. This allowed for more granular control over the application's architecture and made it easier to implement custom features without unnecessary overhead.

### API Integration

The application integrates several external services:

1. **OpenAI API**: For generating personalized travel recommendations
2. **Spotify API**: For playlist matching and music curation
3. **Resend Email Service**: For password reset functionality

## Future Enhancements

The current implementation serves as a strong foundation, but several enhancements are planned:

1. Enhanced playlist matching algorithms
2. User preference storage
3. Social sharing features
4. Advanced error handling
5. Expanded email notification system

## Acknowledgments

This project was created as part of the CS50x course. Special thanks to:

- The course staff for their guidance and support
- OpenAI and Spotify teams for their excellent APIs
- Tailwind CSS team for their utility-first framework
- Font Awesome for their comprehensive icon library
