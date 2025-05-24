import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app import app
from models import LostItem, FoundItem, Match

def save_image(form_image, folder):
    """
    Save an uploaded image with a unique filename
    
    Args:
        form_image: The uploaded file object
        folder: The destination subfolder (e.g., 'lost_items' or 'found_items')
        
    Returns:
        The relative path to the saved image
    """
    # Create a unique filename
    random_hex = uuid.uuid4().hex
    _, file_extension = os.path.splitext(secure_filename(form_image.filename))
    image_filename = random_hex + file_extension
    
    # Ensure the upload directory exists
    upload_dir = os.path.join(app.static_folder, 'uploads', folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the image
    image_path = os.path.join(upload_dir, image_filename)
    form_image.save(image_path)
    
    # Return the relative path for database storage
    return os.path.join('uploads', folder, image_filename)

def calculate_match_score(lost_item, found_item):
    """
    Calculate a similarity score between lost and found items
    
    Args:
        lost_item: A LostItem object
        found_item: A FoundItem object
        
    Returns:
        A float between 0.0 and 1.0 representing match confidence
    """
    score = 0.0
    
    # Check if categories match (high importance)
    if lost_item.category_id == found_item.category_id:
        score += 0.4
    
    # Check title similarity (moderate importance)
    # Simple word matching for demonstration
    lost_words = set(lost_item.title.lower().split())
    found_words = set(found_item.title.lower().split())
    common_words = lost_words.intersection(found_words)
    
    if len(lost_words) > 0 and len(found_words) > 0:
        title_similarity = len(common_words) / max(len(lost_words), len(found_words))
        score += title_similarity * 0.3
    
    # Check description similarity (moderate importance)
    lost_desc_words = set(lost_item.description.lower().split())
    found_desc_words = set(found_item.description.lower().split())
    common_desc_words = lost_desc_words.intersection(found_desc_words)
    
    if len(lost_desc_words) > 0 and len(found_desc_words) > 0:
        desc_similarity = len(common_desc_words) / max(len(lost_desc_words), len(found_desc_words))
        score += desc_similarity * 0.2
    
    # Check location similarity (low importance)
    if lost_item.location_lost.lower() in found_item.location_found.lower() or \
       found_item.location_found.lower() in lost_item.location_lost.lower():
        score += 0.1
    
    # Check date compatibility (lost date should be before or equal to found date)
    if lost_item.date_lost <= found_item.date_found:
        score += 0.0  # Just ensure it's a valid match, no extra points
    else:
        # If found date is before lost date, this is likely not a match
        score = 0.0  # Invalid match
    
    return min(score, 1.0)  # Cap at 1.0

def find_potential_matches(lost_item):
    """
    Find potential matches for a lost item
    
    Args:
        lost_item: A LostItem object
        
    Returns:
        A list of tuples (found_item_id, score) sorted by score
    """
    potential_matches = []
    
    # Query for unclaimed found items
    found_items = FoundItem.query.filter_by(status='unclaimed').all()
    
    for found_item in found_items:
        # Skip if found date is before lost date (impossible match)
        if found_item.date_found < lost_item.date_lost:
            continue
        
        score = calculate_match_score(lost_item, found_item)
        
        # Only consider significant matches (adjust threshold as needed)
        if score > 0.5:
            potential_matches.append((found_item.id, score))
    
    # Sort by score in descending order
    return sorted(potential_matches, key=lambda x: x[1], reverse=True)
