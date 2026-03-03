#!/usr/bin/env python3
"""
Script to create sample data for testing the Opus dashboard
"""

import sys
from src.database import get_db, Base, engine
from src.models import Account, Video, Analytics
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def main():
    print('=== Opus Dashboard Sample Data Setup ===')
    print(f'Python version: {sys.version}')
    print()
    
    try:
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print('1. Checking database connection...')
        try:
            # Test connection
            db.execute(text('SELECT 1'))
            print('OK - Database connection successful')
        except Exception as e:
            print(f'ERROR - Database connection failed: {e}')
            return False
            
        print()
        
        print('2. Creating accounts...')
        try:
            accounts = [
                Account(
                    platform='tiktok',
                    username='@test_tiktok',
                    access_token='test_token_123',
                    is_active=True,
                    created_at=datetime.now()
                ),
                Account(
                    platform='youtube',
                    username='Test YouTube',
                    access_token='yt_token_456',
                    is_active=True,
                    created_at=datetime.now()
                ),
                Account(
                    platform='instagram',
                    username='@test_instagram',
                    access_token='ig_token_789',
                    is_active=True,
                    created_at=datetime.now()
                )
            ]
            
            db.add_all(accounts)
            db.commit()
            print(f'OK - Created {len(accounts)} accounts')
        except Exception as e:
            print(f'ERROR - Error creating accounts: {e}')
            return False
            
        print()
        
        print('3. Creating videos...')
        try:
            accounts = db.query(Account).all()
            videos = []
            
            for i in range(5):
                video = Video(
                    original_url=f'https://example.com/video{i+1}',
                    original_path=f'/uploads/video{i+1}.mp4',
                    processed_path=f'/output/processed/video{i+1}_processed.mp4',
                    duration=60 + i * 10,
                    title=f'Sample Video {i+1}',
                    description=f'This is a sample video description {i+1}',
                    thumbnail_path=f'/output/thumbnails/video{i+1}.jpg',
                    account_id=accounts[i % len(accounts)].id,
                    status='completed',
                    created_at=datetime.now()
                )
                videos.append(video)
                
            db.add_all(videos)
            db.commit()
            print(f'OK - Created {len(videos)} videos')
        except Exception as e:
            print(f'ERROR - Error creating videos: {e}')
            return False
            
        print()
        
        print('4. Creating analytics data...')
        try:
            videos = db.query(Video).all()
            platforms = ['tiktok', 'youtube', 'instagram']
            analytics = []
            
            for i, video in enumerate(videos):
                anal = Analytics(
                    video_id=video.id,
                    account_id=video.account_id,
                    platform=platforms[i % len(platforms)],
                    views=5000 + i * 1000,
                    likes=500 + i * 100,
                    comments=50 + i * 10,
                    shares=100 + i * 20,
                    engagement_rate=8.5 + i * 0.5,
                    posted_at=datetime.now(),
                    last_scraped=datetime.now()
                )
                analytics.append(anal)
                
            db.add_all(analytics)
            db.commit()
            print(f'OK - Created {len(analytics)} analytics records')
        except Exception as e:
            print(f'ERROR - Error creating analytics: {e}')
            return False
            
        print()
        
        print('5. Verifying data...')
        try:
            print(f'Accounts: {db.query(Account).count()}')
            print(f'Videos: {db.query(Video).count()}')
            print(f'Analytics: {db.query(Analytics).count()}')
            
            total_views = 0
            for anal in db.query(Analytics).all():
                total_views += anal.views
            
            print(f'Total views: {total_views}')
        except Exception as e:
            print(f'ERROR - Error verifying data: {e}')
            return False
            
        db.close()
        
        print()
        print('=== Sample data setup completed successfully! ===')
        return True
        
    except Exception as e:
        print(f'ERROR - Fatal error: {e}')
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
