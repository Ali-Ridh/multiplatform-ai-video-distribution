# multiplatform-ai-video-distribution
🚀 AI-powered video repurposing &amp; multi-account automation engine. Clips long-form content into viral 9:16 shorts and automates distribution across TikTok, IG Reels, and YouTube Shorts with built-in originality filters for mass-scale monetization.


A comprehensive video pipeline system for creating, processing, and distributing high-quality content across multiple social media platforms.

## Features

### 🎬 High-Performance Video Pipeline

- **Intelligent Reframing**: Real-time face tracking using MediaPipe to ensure the speaker stays centered in 9:16 crop
- **Dynamic Subtitling**: Word-level timestamped captions in .ass or .srt format using Faster-Whisper
- **B-Roll Engine**: Automated stock footage overlay system for split-screen effects
- **Video Templates**: 3 distinct visual templates (Minimalist, Hormozi, Gaming) using MoviePy

### 🛡️ Originality Layer (Anti-Shadowban)

- **Metadata Spinner**: LLM-powered unique titles, descriptions, and hashtags
- **Visual Fingerprinting**: Subtle variations in background blur, color grading, and fonts
- **Audio Hashing**: Slight pitch or speed adjustments (±1%) to change audio signatures

### 🚀 Distribution & Account Management

- **OAuth2 Vault**: Secure storage for TikTok, Google, and Meta access tokens
- **Proxy Support**: Residential proxies for location simulation
- **Staggered Scheduler**: Human-in-the-loop queue with drip-feed functionality
- **Worker Queue**: Celery + Redis for CPU-intensive rendering tasks

### 📊 Analytics & Dashboard

- **Next.js Frontend**: Real-time dashboard with health status monitoring
- **Clip Review Gallery**: UI for previewing AI-generated clips and manual approval
- **Analytics Scraper**: Background task to track view counts and engagement metrics

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Redis server
- FFmpeg
- OpenAI API key

### Database Configuration

**SQLite (Default - Lightweight, File-based):**
- Already configured in `.env` as `DATABASE_URL=sqlite:///./opus.db`
- No additional setup required
- Works well for development and small-scale operations

**PostgreSQL (Production - Scalable):**
For production or high-volume use (15+ accounts):
1. Install PostgreSQL from [PostgreSQL.org](https://www.postgresql.org/download/)
2. Create database and user:
   ```sql
   CREATE DATABASE opus;
   CREATE USER opus_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE opus TO opus_user;
   ```
3. Update `.env` file:
   ```
   DATABASE_URL=postgresql://opus_user:your_secure_password@localhost:5432/opus
   ```

### Installation

1. **Clone the repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Create environment variables**:
   ```bash
   cp .env.example .env
   ```
   Fill in your API keys and configuration.

5. **Initialize database**:
   ```bash
   python create_tables.py
   ```
   This will create all the necessary tables in SQLite.

6. **Test database connection**:
   ```bash
   python test_simple.py
   ```

### Running the System

1. **Start Redis server**:
   ```bash
   redis-server
   ```

2. **Start Celery worker**:
   ```bash
   celery -A src.worker.celery_app worker --loglevel=info --concurrency=4
   ```

3. **Start Flower monitoring**:
   ```bash
   celery -A src.worker.celery_app flower --port=5555
   ```

4. **Start the backend server**:
   ```bash
   python main.py dashboard
   ```

5. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

### Usage

#### Command Line Interface

```bash
# Process a single video
python main.py process https://youtube.com/watch?v=dQw4w9WgXcQ

# Render processed videos
python main.py render

# Upload rendered videos
python main.py upload

# Start dashboard server
python main.py dashboard

# Start Celery worker
python main.py worker

# Start Flower monitoring
python main.py flower
```

#### API Endpoints

- `GET /api/health` - Health check
- `POST /api/process` - Process a video from URL
- `GET /api/videos` - List processed videos
- `POST /api/render` - Render video variations
- `POST /api/upload-video` - Upload video to platforms
- `GET /api/analytics` - Get analytics data

## Project Structure

```
Opus/
├── src/
│   ├── api/              # FastAPI backend
│   │   └── server.py     # REST API endpoints
│   ├── worker/           # Celery tasks
│   │   ├── celery_app.py # Celery configuration
│   │   └── tasks.py      # Async task definitions
│   ├── database.py       # Database session management
│   ├── models.py         # SQLAlchemy ORM models
│   ├── opus.py           # Core engine orchestrator
│   ├── downloader.py     # Video downloader
│   ├── transcriber.py    # Speech-to-text
│   ├── segmenter.py      # Viral segment detector
│   ├── reframer.py       # Face-tracking reframer
│   ├── templater.py      # Video template engine
│   ├── renderer.py       # Video rendering with fingerprinting
│   ├── distributor.py    # Platform API integrations
│   ├── scheduler.py      # Staggered scheduler
│   └── caption_generator.py # Caption variation generator
├── frontend/             # Next.js dashboard
│   ├── app/              # Pages and components
│   ├── components/       # React components
│   └── styles/           # CSS styles
├── create_tables.py      # Database table creation script
├── database_setup.py     # Database connection test script
├── test_simple.py        # Simple database test
├── test_database.py      # Comprehensive database test
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── opus.db               # SQLite database file (created automatically)
```

## Database Structure

The system uses SQLAlchemy ORM with these main tables:

| Table | Purpose |
|-------|---------|
| `users` | System user accounts and authentication |
| `accounts` | Social media platform accounts with API credentials |
| `videos` | Processed video metadata |
| `video_renditions` | Rendered video variations for each platform |
| `video_segments` | Viral segments detected in videos |
| `analytics` | Video performance analytics |
| `tasks` | Background task tracking |
| `schedules` | Video upload schedule |
| `proxies` | Proxy server configuration |

## Technologies Used

- **Python**: FastAPI, Celery, Redis, OpenCV, MediaPipe, MoviePy, FFmpeg
- **JavaScript/TypeScript**: Next.js, React, TailwindCSS, Recharts
- **AI/LLM**: OpenAI GPT-4o, Faster-Whisper
- **Databases**: SQLite (local), PostgreSQL (production)
- **Message Queue**: Redis + Celery

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for GPT-4o and Whisper
- `REDIS_URL`: Redis server URL (default: redis://localhost:6379/0)
- `TIKTOK_API_KEY` / `TIKTOK_SECRET_KEY`: TikTok API credentials
- `YOUTUBE_API_KEY`: YouTube Data API v3 key
- `INSTAGRAM_ACCESS_TOKEN` / `INSTAGRAM_APP_SECRET`: Instagram Graph API credentials
- `PROXY_ENABLED`: Enable proxy support (True/False)
- `PROXY_LIST`: Comma-separated list of residential proxies
- `UPLOAD_DIR`: Directory for downloaded videos
- `OUTPUT_DIR`: Directory for processed/rendered videos

## Advanced Features

### Viral Segment Detection

Uses GPT-4o to analyze transcripts and identify segments with high viral potential based on:

- Emotional hooks (surprise, curiosity, anger, joy)
- Actionable information or advice
- Controversial or thought-provoking statements
- Relatable or aspirational content
- High information density in short time

### Video Fingerprinting

Applied during rendering to create unique variations:

- Subtle hue, saturation, and brightness adjustments
- Background blur variations
- Vignette effects
- Audio speed/pitch adjustments (±0.5% to ±1.5%)

### Staggered Scheduling

Prevents platform spam detection by distributing posts over time:

- Base delay: 5 minutes per video
- Random offset: 0-5 minutes per video
- Account-specific delays

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
