"""
    This is a function that randomly extracts patches from an image directory and stitches them together 
    to form a new image. The number of output images, output image sizes are specified by the user

    Inputs:

    directory: The path to the folder containing the images from which the patches are to be extracted.
    output_size: The desired size of the output image (e.g., (256, 256)).
    num_outputs: The number of output images to be generated.
    output_directory: The path to the folder where the output images should be saved.
    grids: The number of grids in x-axis.

"""

import os
import random
import argparse
from PIL import Image
from tqdm import tqdm

def create_stitched_images(
        directory: str, 
        output_size: int, 
        num_outputs: int, 
        output_directory: str, 
        grids: int):
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Save the file names
    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Check if number of images is less than one; raise error if true
    if len(image_files) == 0:
        print("No images in the directory.")
        return

    # Calculate the patch size based on output size and grids
    patch_size = output_size // grids

    # Create as many empty images as there are expected outputs.
    for output_index in range(num_outputs):
        output_image = Image.new('RGB', (output_size, output_size))
        x = 0
        y = 0

        random.shuffle(image_files)  # Randomize the order of image files for each output

        # Calculate the number of patches in each dimension
        num_patches_x = output_size // patch_size
        num_patches_y = output_size // patch_size

        for patch_index_x in tqdm(range(num_patches_x), desc='Processing patches'):
            for patch_index_y in range(num_patches_y):
                # Randomly choose an image file
                patch_image_file = random.choice(image_files)

                patch_width = patch_size
                patch_height = patch_size

                patch_image_path = os.path.join(directory, patch_image_file)
                patch_image = Image.open(patch_image_path)

                # Calculate the maximum allowed position for the patch
                max_x = patch_image.size[0] - patch_width
                max_y = patch_image.size[1] - patch_height

                # Generate a random position for the patch within the image
                random_x = random.randint(0, max_x)
                random_y = random.randint(0, max_y)

                # Extract the patch
                patch_image = patch_image.crop((random_x, random_y, random_x + patch_width, random_y + patch_height))

                output_image.paste(patch_image, (x, y))

                x += patch_size

            x = 0
            y += patch_size

        # Save stitched image
        output_filename = f"output_{output_index + 1}.jpg"
        output_filepath = os.path.join(output_directory, output_filename)
        output_image.save(output_filepath)
        print(f"Stitched image {output_index + 1} saved: {output_filepath}")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a new image using patches extracted from other images')
    parser.add_argument('--directory', required=True, help='Path to the directory (base images)')
    parser.add_argument('--output_size', type=int, default=512, help='Output image size. Default = 512')
    parser.add_argument('--num_outputs', type=int, default=1, help='Number of outputs to be generated. Default = 1')
    parser.add_argument('--output_directory', required=True, help='Path to the output directory')
    parser.add_argument('--grids', type=int, default=2, help='The number of grids on x and y axis. Default = 2')

    args = parser.parse_args()
    create_stitched_images(
        directory=args.directory, 
        output_size=args.output_size, 
        num_outputs=args.num_outputs, 
        output_directory=args.output_directory, 
        grids=args.grids)