from PIL import Image, ImageDraw, ImageFont

def create_Text_Image(number: str, color: tuple[int,int,int]):
    image = Image.new("RGB", size=(400,200), color=(80,80,80))
    draw = ImageDraw.Draw(image)
        
    font = ImageFont.truetype("../fonts/LHANDW.TTF", 100)
    
    bbox = draw.textbbox((0, 0), number, font=font)
    number_width, number_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    number_x = (image.width - number_width) // 2
    number_y = (image.height - number_height - 50) // 2

    draw.text((number_x, number_y), number, fill=color, font=font)


    image.save(f"./images/{number}.png", "PNG")
