import os
from PIL import Image

UPLOADED_IMG = r"C:\Users\User\.gemini\antigravity\brain\7e6e4f9e-083a-4b3b-a21a-06f41d41123a\.user_uploaded\media_1794138991332_57b9892b.jpg"
BASE_DIR = r"C:\Users\User\.gemini\antigravity\scratch\heritage-ecommerce"
IMG_DIR = os.path.join(BASE_DIR, "static", "images")
os.makedirs(IMG_DIR, exist_ok=True)

def process_pure_lehenga():
    src = Image.open(UPLOADED_IMG).convert("RGB")
    
    # Save the original pristine photo as emerald-gold-lehenga.jpg
    out_path = os.path.join(IMG_DIR, "emerald-gold-lehenga.jpg")
    src.save(out_path, quality=98)
    print("Saved clean emerald lehenga photo:", out_path)
    
    # Also save as slide-1-model.jpg so the slideshow can use it directly
    slide_model_path = os.path.join(IMG_DIR, "slide-1-model.jpg")
    src.save(slide_model_path, quality=98)
    print("Saved slide 1 model image:", slide_model_path)

if __name__ == "__main__":
    process_pure_lehenga()
