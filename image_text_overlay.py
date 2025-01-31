from PIL import Image, ImageDraw, ImageFont
import torch


import numpy as np

class ImageTextOverlay:
    def __init__(self, device="cpu"):
        self.device = device
    _alignments = ["left", "right", "center"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"multiline": True, "default": "Hello"}),
                "font_size": ("INT", {"default": 16, "min": 1, "max": 256, "step": 1}),
                "x": ("INT", {"default": 0}),
                "y": ("INT", {"default": 0}),
                "font": ("STRING", {"default": "arial.ttf"}),  # Assuming it's a path to a .ttf or .otf file
                "alignment": (cls._alignments, {"default": "left"}),  # ["left", "right", "center"]
                "color": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFF, "step": 1, "display": "color", "tooltip": "Format 0xRRGGBB; pre-pend 0x, e.g: 0xFFFFFF for white"}),
                "position_option": ("BOOLEAN", {"default": False, "label_on": "Using Bottom Right", "label_off": "Using X,Y Position", "tooltip": "Toggle to place text at the bottom right of the image or use custom X, Y positions."}),
                "background": ("BOOLEAN", {"default": False, "label_on": "Opaque", "label_off": "Transparent", "tooltip": "Toggle to add an opaque white background to the text with black font color."}),
                "opaque_size": ("INT", {"default": 10, "min": 0, "max": 50, "step": 1, "tooltip": "Adjust the size of the opaque background box."}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "image/text"

    def draw_text_on_image(self, image, text, font_size, x, y, font, alignment, color, position_option, background, opaque_size):
        # Convert tensor to numpy array and then to PIL Image
        image_tensor = image
        image_np = image_tensor.cpu().numpy()  # Change from CxHxW to HxWxC for Pillow
        image = Image.fromarray((image_np.squeeze(0) * 255).astype(np.uint8))  # Convert float [0,1] tensor to uint8 image

        # Convert color from INT to RGB tuple
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        color_rgb = (r, g, b)

        # Load font
        loaded_font = ImageFont.truetype(font, font_size)

        # Prepare to draw on image
        draw = ImageDraw.Draw(image)

        # Adjust x and y coordinates based on ignore_position
        if position_option:
            text_width = draw.textlength(text, font=loaded_font)
            text_bbox = draw.textbbox((0, 0), text, font=loaded_font)
            text_height = text_bbox[3] - text_bbox[1] + opaque_size  # Add opaque_size to the height
            x = image.width - text_width - 10  # 10 pixels buffer from the right
            y = image.height - text_height - 10  # 10 pixels buffer from the bottom

        # Draw opaque background if needed
        if background:
            text_width = draw.textlength(text, font=loaded_font)
            text_bbox = draw.textbbox((0, 0), text, font=loaded_font)
            text_height = text_bbox[3] - text_bbox[1] + opaque_size  # Add opaque_size to the height
            draw.rectangle([x, y, x + text_width, y + text_height], fill="white")
            color_rgb = (0, 0, 0)  # Set text color to black

        # Adjust x coordinate based on alignment
        if alignment == "center":
            x -= text_width // 2
        elif alignment == "right":
            x -= text_width

        # Draw text on the image
        draw.text((x, y), text, fill=color_rgb, font=loaded_font)

        # Convert back to Tensor if needed
        image_tensor_out = torch.tensor(np.array(image).astype(np.float32) / 255.0)  # Convert back to CxHxW
        image_tensor_out = torch.unsqueeze(image_tensor_out, 0)

        return (image_tensor_out,)


NODE_CLASS_MAPPINGS = {
    "Image Text Overlay": ImageTextOverlay,
}
