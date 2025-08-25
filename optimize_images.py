from PIL import Image
import os

def optimize_image(input_path, output_path=None, quality=85, max_size=(1920, 1080)):
    """
    Optimize an image by:
    1. Resizing it to a maximum size while maintaining aspect ratio
    2. Compressing it with a specified quality
    3. Saving it as both JPG and WebP formats
    
    Args:
        input_path: Path to the original image
        output_path: Path to save the optimized image (without extension)
        quality: Compression quality (1-100)
        max_size: Maximum dimensions (width, height)
    """
    if output_path is None:
        # Use the same directory and filename but add '_optimized'
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_optimized"
    
    # Open the image
    img = Image.open(input_path)
    
    # Get original dimensions
    orig_width, orig_height = img.size
    print(f"Original image size: {orig_width}x{orig_height} pixels")
    print(f"Original file size: {os.path.getsize(input_path) / (1024 * 1024):.2f} MB")
    
    # Calculate new dimensions while maintaining aspect ratio
    width, height = img.size
    if width > max_size[0] or height > max_size[1]:
        ratio = min(max_size[0] / width, max_size[1] / height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"Resized to: {new_size[0]}x{new_size[1]} pixels")
    
    # Save as optimized JPG
    jpg_path = f"{output_path}.jpg"
    img.save(jpg_path, "JPEG", quality=quality, optimize=True)
    print(f"Saved optimized JPG: {jpg_path}")
    print(f"New JPG size: {os.path.getsize(jpg_path) / (1024 * 1024):.2f} MB")
    
    # Save as WebP (better compression)
    webp_path = f"{output_path}.webp"
    img.save(webp_path, "WEBP", quality=quality)
    print(f"Saved WebP: {webp_path}")
    print(f"WebP size: {os.path.getsize(webp_path) / (1024 * 1024):.2f} MB")
    
    return jpg_path, webp_path

if __name__ == "__main__":
    # Optimize the cover image
    input_image = "media/images/Acces.jpg"
    output_prefix = "media/images/Acces_optimized"
    
    jpg_path, webp_path = optimize_image(input_image, output_prefix, quality=80)
    print("\nOptimization complete!")
    print(f"Compression ratio JPG: {os.path.getsize(jpg_path) / os.path.getsize(input_image):.2%}")
    print(f"Compression ratio WebP: {os.path.getsize(webp_path) / os.path.getsize(input_image):.2%}")
