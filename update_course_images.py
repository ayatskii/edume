import os
import sys
import django
import requests
import random
from django.core.files.base import ContentFile
from io import BytesIO
from tqdm import tqdm
import time

# Set up Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from education.models import Course

def download_image(url):
    """Download image from URL and return as ContentFile"""
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return ContentFile(response.content)

def main():
    # Get all courses
    courses = Course.objects.all()
    print(f"Found {courses.count()} courses to update")
    
    # Different image categories to get a variety of images
    categories = [
        "education", "books", "library", "study", "school", 
        "university", "classroom", "laptop", "programming",
        "science", "mathematics", "business", "technology", 
        "design", "art", "music", "language", "history"
    ]
    
    # Create media directory if it doesn't exist
    os.makedirs('media/course_thumbnails', exist_ok=True)
    
    for i, course in enumerate(tqdm(courses)):
        # Get image from Unsplash with varying categories based on course category
        category = course.category.lower() if course.category else random.choice(categories)
        
        # Unsplash source API - simple and doesn't require registration
        width, height = 800, 600
        # Use a seed based on course ID to get consistent but different images
        seed = course.id or i + 1000  
        url = f"https://source.unsplash.com/random/{width}x{height}/?{category}&sig={seed}"
        
        # Add a brief delay to avoid rate limiting
        time.sleep(0.5)
        
        try:
            # Download the image
            image_content = download_image(url)
            if image_content:
                # Clean up old thumbnail if it exists
                if course.thumbnail:
                    try:
                        course.thumbnail.delete(save=False)
                    except:
                        pass
                
                # Update with new image
                filename = f"course_{course.id}_{category}_{seed}.jpg"
                course.thumbnail.save(filename, image_content, save=True)
                print(f"✅ Updated course: {course.title}")
            else:
                print(f"❌ Failed to download image for: {course.title}")
        except Exception as e:
            print(f"❌ Error updating image for {course.title}: {str(e)}")
    
    print("Finished updating course images")

if __name__ == "__main__":
    main() 