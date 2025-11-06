# SlotSwapper - Peer-to-Peer Time-Slot Scheduling

A modern, full-stack web application with real-time notifications that allows users to swap calendar time slots with each other. Built with Django REST Framework, PostgreSQL, React, and WebSockets.

## 🚀 Features

### Core Features
- **User Authentication**: JWT-based secure signup and login
- **Event Management**: Create, view, update, and delete calendar events
- **Slot Swapping**: Mark events as swappable and request swaps with other users
- **Request Management**: Accept or reject incoming swap requests
- **Real-time Notifications**: Instant WebSocket notifications when users receive or respond to swap requests

### UI/UX Features
- **Modern Design**: Beautiful Tailwind CSS interface with gradient backgrounds
- **Responsive Layout**: Mobile-first design that works on all devices
- **Toast Notifications**: Elegant notification toasts for real-time updates
- **Smooth Animations**: Polished transitions and hover effects
- **Professional Styling**: Clean, modern interface with intuitive navigation

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Django 4.2
- Django REST Framework
- Django Channels (WebSockets)
- Redis (for channel layers)
- PostgreSQL
- JWT Authentication

**Frontend:**
- React 18
- React Router v6
- Axios
- Tailwind CSS
- Lucide React (icons)
- WebSocket API

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Redis 6+ (for WebSocket support)
- npm or yarn

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd slotswapper
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
# In PostgreSQL shell:
CREATE DATABASE slotswapper;

# Update database credentials in backend/settings.py

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. Redis Setup

**On Windows:**
1. Download Redis from https://github.com/microsoftarchive/redis/releases
2. Run `redis-server.exe`

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Linux:**
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

### 4. Start Backend Server

```bash
# Use Daphne for ASGI support (WebSockets)
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# Or use Django's development server (less features)
python manage.py runserver
```

Backend will run on `http://localhost:8000`

### 5. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Install Tailwind CSS and other packages
npm install -D tailwindcss postcss autoprefixer
npm install axios react-router-dom lucide-react

# Initialize Tailwind (if not done)
npx tailwindcss init

# Start React development server
npm start
```

Frontend will run on `http://localhost:3000`

## 📁 Project Structure

```
slotswapper/
├── backend/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py           # ASGI configuration for WebSockets
│   └── api/
│       ├── __init__.py
│       ├── models.py          # Event and SwapRequest models
│       ├── serializers.py     # DRF serializers
│       ├── views.py           # API views with notification logic
│       ├── consumers.py       # WebSocket consumer
│       ├── routing.py         # WebSocket routing
│       ├── urls.py
│       └── admin.py
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── Login.js
    │   │   ├── Signup.js
    │   │   ├── Dashboard.js
    │   │   ├── Marketplace.js
    │   │   ├── Requests.js
    │   │   └── NotificationToast.js
    │   ├── hooks/
    │   │   └── useWebSocket.js  # WebSocket hook
    │   ├── services/
    │   │   └── api.js
    │   ├── App.js
    │   ├── index.css            # Tailwind imports
    │   └── index.js
    ├── tailwind.config.js
    └── package.json
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/me/` - Get current user (requires auth)

### Events
- `GET /api/events/` - Get user's events
- `POST /api/events/` - Create new event
- `PUT /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
- `PATCH /api/events/{id}/update_status/` - Update event status

### Swap Operations
- `GET /api/swappable-slots/` - Get all available swappable slots
- `POST /api/swap-request/` - Create swap request
  - Body: `{ "mySlotId": int, "theirSlotId": int }`
- `POST /api/swap-response/{request_id}/` - Respond to swap request
  - Body: `{ "accept": boolean }`
- `GET /api/swap-requests/` - Get incoming and outgoing swap requests

### WebSocket
- `ws://localhost:8000/ws/notifications/?token={JWT_TOKEN}` - Real-time notifications

## 🎯 Usage Guide

### 1. Sign Up / Login
- Navigate to the signup page
- Create an account with username, email, and password
- Login with your credentials

### 2. Create Events
- Go to "My Calendar"
- Click "Create Event"
- Fill in event details (title, start time, end time)
- Event is created with "BUSY" status by default

### 3. Make Slots Swappable
- On your calendar, find an event
- Click "Make Swappable" to mark it available for swapping

### 4. Request a Swap
- Go to "Marketplace"
- Browse available slots from other users
- Click "Request Swap" on a desired slot
- Select one of your swappable slots to offer

### 5. Manage Swap Requests
- Go to "Requests"
- View incoming requests (others wanting your slots)
- Accept or reject requests
- View your outgoing requests and their status
- **Receive real-time notifications** when requests are received or responded to

### 6. Real-time Notifications
- Automatic WebSocket connection on login
- Toast notifications appear for:
  - New swap requests received
  - Swap requests accepted
  - Swap requests rejected
- Notifications auto-dismiss after 5 seconds

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:
- Access tokens are stored in localStorage
- Tokens are automatically attached to API requests
- WebSocket connection authenticated via query parameter
- Protected routes redirect to login if not authenticated

## 🎨 Design Decisions

1. **Django Channels + Redis**: WebSocket support for real-time notifications
2. **Tailwind CSS**: Utility-first CSS for rapid, responsive design
3. **JWT Authentication**: Stateless authentication suitable for SPA and WebSockets
4. **PostgreSQL**: Relational database for complex queries and data integrity
5. **React Hooks**: Modern React patterns with custom hooks for WebSocket
6. **Status Management**: Three-state system (BUSY, SWAPPABLE, SWAP_PENDING) prevents race conditions
7. **Gradient Design**: Modern gradient backgrounds and professional styling

## 🚧 Challenges & Solutions

### Challenge 1: Real-time Notifications
**Solution**: Implemented Django Channels with Redis for WebSocket support, custom React hook for WebSocket management

### Challenge 2: WebSocket Authentication
**Solution**: Pass JWT token via query parameter, validate in WebSocket consumer

### Challenge 3: Preventing Concurrent Swap Requests
**Solution**: Implemented `SWAP_PENDING` status that locks slots during pending requests

### Challenge 4: Atomic Swap Operations
**Solution**: Used Django's `@transaction.atomic` decorator to ensure data consistency

### Challenge 5: Professional UI/UX
**Solution**: Implemented Tailwind CSS with custom animations, gradients, and responsive design patterns

## 🔮 Bonus Features Implemented

✅ **Real-time Notifications**: WebSocket integration for instant notifications
✅ **Professional Design**: Modern Tailwind CSS styling with animations
✅ **Toast Notifications**: Elegant notification system
✅ **Responsive Design**: Mobile-first approach
✅ **Loading States**: Smooth loading indicators
✅ **Error Handling**: Comprehensive error messages

## 📝 Testing

### Backend Testing
```bash
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing Checklist
- [ ] User signup and login
- [ ] Create, edit, delete events
- [ ] Mark events as swappable
- [ ] Request swaps
- [ ] Accept/reject swap requests
- [ ] Real-time notifications appear
- [ ] Mobile responsive design works
- [ ] WebSocket reconnection on disconnect

## 🚀 Deployment

### Backend (Render/Railway)
1. Add `gunicorn` and `daphne` to requirements.txt
2. Create `Procfile`: `web: daphne backend.asgi:application --port $PORT --bind 0.0.0.0`
3. Set environment variables (DATABASE_URL, REDIS_URL)
4. Deploy via Git

### Frontend (Vercel/Netlify)
1. Update API URL in `src/services/api.js` to production URL
2. Update WebSocket URL in `src/hooks/useWebSocket.js`
3. Build: `npm run build`
4. Deploy build folder

### Redis
- Use Redis Cloud (free tier available)
- Update CHANNEL_LAYERS in settings.py with production Redis URL

## 🐛 Troubleshooting

**WebSocket not connecting?**
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check Django is running with Daphne, not runserver
- Verify WebSocket URL includes token parameter

**Notifications not appearing?**
- Check browser console for WebSocket errors
- Ensure JWT token is valid
- Verify Redis connection in Django logs

**Tailwind styles not working?**
- Run `npm install -D tailwindcss`
- Ensure tailwind.config.js exists
- Check src/index.css has @tailwind directives

## 📄 Dependencies

**Backend (requirements.txt):**
```
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
psycopg2-binary==2.9.9
django-cors-headers==4.3.0
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0
```

**Frontend (package.json):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.5",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

## 📄 License

This project is part of ServiceHive SDE assignment.

## 👤 Author

[Your Name]
- GitHub: [@yourusername]
- Email: your.email@example.com

## 🙏 Acknowledgments

- ServiceHive for the assignment opportunity
- Django, React, and Tailwind communities for excellent documentation
- Lucide for beautiful React icons
