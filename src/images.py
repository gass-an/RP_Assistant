from PIL import Image, ImageDraw, ImageFont

def create_bg_roll_Image(number: str, text_color: tuple[int,int,int], image_path: str, font_path: str):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    if font_path == "/app/fonts/LHANDW.TTF":
        size = 175
    else : 
        size = 100

    font = ImageFont.truetype(font_path, size)
    

    if image_path == "./images/bg_roll.jpg" :

        bbox = draw.textbbox((0, 0), number, font=font)
        number_width, number_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        number_x = (image.width - number_width - 50) // 2
        number_y = (image.height - number_height + 75) // 2

    else :
        
        bbox = draw.textbbox((0, 0), number, font=font)
        number_width, number_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        number_x = (image.width - number_width ) // 2
        number_y = (image.height - number_height - 100) // 2


    draw.text((number_x, number_y), number, fill=text_color, font=font)

    image.save(f"./images/{number}.png", "PNG")
