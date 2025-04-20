import os
import sys
import django
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from io import BytesIO
from tqdm import tqdm

# Set up Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from education.models import Course

def generate_image(title, category, width=800, height=600):
    """Generate a custom image with text based on course category and title"""
    # Create a new image with a color based on category
    category_colors = {
        'Programming': (41, 128, 185),      # Blue
        'Data Science': (155, 89, 182),     # Purple
        'Web Development': (52, 152, 219),  # Light Blue
        'Mobile Development': (26, 188, 156), # Green
        'DevOps': (46, 204, 113),           # Light Green
        'Design': (241, 196, 15),           # Yellow
        'Business': (230, 126, 34),         # Orange
        'Marketing': (231, 76, 60),         # Red
        'Language Learning': (142, 68, 173), # Dark Purple
        'Mathematics': (39, 174, 96)        # Dark Green
    }
    
    # Default color if category not in predefined list
    color = category_colors.get(category, (52, 73, 94))  # Dark Gray default
    
    # Create background with gradient
    background = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(background)
    
    # Add some shapes for visual interest
    for _ in range(10):
        shape_x = random.randint(0, width)
        shape_y = random.randint(0, height)
        shape_size = random.randint(20, 100)
        shape_color = tuple(max(0, min(255, c + random.randint(-30, 30))) for c in color)
        draw.ellipse(
            (shape_x, shape_y, shape_x + shape_size, shape_y + shape_size),
            fill=shape_color
        )
    
    # Add text - course title and category
    try:
        font = ImageFont.truetype('arial.ttf', size=40)
        small_font = ImageFont.truetype('arial.ttf', size=30)
    except IOError:
        # Use default font if arial not available
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add semi-transparent overlay for better text visibility
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([(0, height//2 - 60), (width, height//2 + 60)], fill=(0, 0, 0, 128))
    
    background = Image.alpha_composite(background.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(background)
    
    # Draw text
    title_text = title if len(title) < 30 else title[:27] + "..."
    draw.text(
        (width//2, height//2 - 25),
        title_text,
        fill=(255, 255, 255),
        font=font,
        anchor="mm"
    )
    
    draw.text(
        (width//2, height//2 + 25),
        category,
        fill=(255, 255, 255, 200),
        font=small_font,
        anchor="mm"
    )
    
    # Save to BytesIO
    img_io = BytesIO()
    background.save(img_io, format='JPEG', quality=90)
    img_io.seek(0)
    
    return ContentFile(img_io.getvalue())

def main():
    # Get all courses
    courses = Course.objects.all()
    print(f"Found {courses.count()} courses to update")
    
    # Create media directory if it doesn't exist
    os.makedirs('media/course_thumbnails', exist_ok=True)
    
    for i, course in enumerate(tqdm(courses)):
        try:
            # Generate custom image
            image_content = generate_image(course.title, course.category)
            
            # Clean up old thumbnail if it exists
            if course.thumbnail:
                try:
                    course.thumbnail.delete(save=False)
                except:
                    pass
            
            # Update with new image
            filename = f"course_{course.id}_{course.category.lower().replace(' ', '_')}.jpg"
            course.thumbnail.save(filename, image_content, save=True)
            print(f"✅ Updated course: {course.title}")
        except Exception as e:
            print(f"❌ Error updating image for {course.title}: {str(e)}")
    
    print("Finished updating course images")

if __name__ == "__main__":
    main() 