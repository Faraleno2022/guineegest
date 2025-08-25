from PIL import Image, ImageDraw, ImageFont
import os

# Créer le dossier team s'il n'existe pas déjà
os.makedirs('media/images/team', exist_ok=True)

# Dimensions de l'image
width, height = 400, 400
background_color = (52, 152, 219)  # Bleu
text_color = (255, 255, 255)  # Blanc

# Créer une nouvelle image avec fond bleu
image = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(image)

# Dessiner un cercle pour simuler un avatar
circle_radius = 150
circle_center = (width // 2, height // 2)
circle_bbox = (
    circle_center[0] - circle_radius,
    circle_center[1] - circle_radius,
    circle_center[0] + circle_radius,
    circle_center[1] + circle_radius
)
draw.ellipse(circle_bbox, fill=(41, 128, 185))  # Bleu plus foncé

# Ajouter les initiales au centre
try:
    # Essayer de charger une police, sinon utiliser la police par défaut
    font = ImageFont.truetype("arial.ttf", 120)
except IOError:
    font = ImageFont.load_default()

text = "GG"  # Initiales pour Guinée-Ges
text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (120, 120)
text_position = (width // 2 - text_width // 2, height // 2 - text_height // 2)
draw.text(text_position, text, font=font, fill=text_color)

# Enregistrer l'image
image.save('media/images/team/team-member-1.jpg')
print("Image placeholder créée avec succès dans media/images/team/team-member-1.jpg")
