from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    """Create a simple placeholder image for courses"""
    
    # Create directory if it doesn't exist
    os.makedirs('media/course_thumbnails', exist_ok=True)
    
    # Image dimensions
    width, height = 800, 600
    
    # Create a new white image
    image = Image.new('RGB', (width, height), color=(51, 102, 255))
    draw = ImageDraw.Draw(image)
    
    # Add text
    text = "Course Placeholder"
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype('arial.ttf', size=60)
    except IOError:
        font = ImageFont.load_default()
    
    # Get text size
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (300, 50)
    
    # Position text in the center
    position = ((width - text_width) // 2, (height - text_height) // 2)
    
    # Draw the text
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # Save the image
    image.save('media/course_thumbnails/placeholder.jpg')
    
    print("Placeholder image created at media/course_thumbnails/placeholder.jpg")

if __name__ == "__main__":
    create_placeholder_image() 