"""
    This is script contains a function that is used to extracts objects from an image and then paste those objects on another image.

    Inputs:

    image_dir: Path to the image directory (image containing objects)
    base_image_dir: Path to the directory containing images to be used as the new base
    output_dir: Path to the output folder (if it doesn't exist it'll create one)
    num_outputs: Number of outputs to be generated
"""

import os
import cv2
import shutil
import random
import argparse
from tqdm import tqdm

def extract_objects(image_dir, base_image_dir, output_dir, num_outputs):

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    augmented_data_dir = os.path.join(output_dir, "augmented_data")
    os.makedirs(augmented_data_dir, exist_ok=True)

    # Output data directory
    output_images_dir = os.path.join(augmented_data_dir, "images")
    os.makedirs(output_images_dir, exist_ok=True)

    output_labels_dir = os.path.join(augmented_data_dir, "labelTxt")
    os.makedirs(output_labels_dir, exist_ok=True)

    # Get a list of all image files
    image_files = os.listdir(os.path.join(image_dir, "images"))

    # Get a list of all base image files
    base_image_files = os.listdir(base_image_dir)

    for i in tqdm(range(num_outputs), desc='Extracting objects'):
        # Randomly select an image
        image_file = random.choice(image_files)

        # Randomly select a base image
        base_image_file = random.choice(base_image_files)
        base_image_path = os.path.join(base_image_dir, base_image_file)
        base_image = cv2.imread(base_image_path)

        # Load the image using OpenCV
        image_path = os.path.join(image_dir, "images", image_file)
        image = cv2.imread(image_path)

        # Check if the image was successfully loaded
        if image is None:
            print("Failed to load image: {}".format(image_file))
            continue

        elif image is not None:
            # Load the corresponding annotation file
            annotation_file = image_file.replace(".jpg", ".txt")
            annotation_path = os.path.join(image_dir, "labelTxt", annotation_file) 

            # Create a copy of the annotation file with the new name
            output_annotation_file = "output{}.txt".format(i)
            output_annotation_path = os.path.join(output_labels_dir, output_annotation_file)
            shutil.copyfile(annotation_path, output_annotation_path)

            # Extract the objects based on annotations in the .txt file 
            # Open the annotation file
            with open(annotation_path, 'r') as file:
                lines = file.readlines()

                skipped_annotations = []
            
                # Iterate through the lines and extract object information
                for line in lines:

                    x1, y1, x2, y2, x3, y3, x4, y4, label, difficulty = line.strip().split()
                    x1, y1, x2, y2, x3, y3, x4, y4 = map(float, [x1, y1, x2, y2, x3, y3, x4, y4])
                    
                    # Convert coordinates to integers
                    x1, y1, x2, y2, x3, y3, x4, y4 = int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), int(x4), int(y4)

                    # Extract the object from the image
                    object_img = image[min(y1, y2, y3, y4):max(y1, y2, y3, y4), min(x1, x2, x3, x4):max(x1, x2, x3, x4)]

                    # Get the dimensions of the extracted object
                    object_height, object_width, _ = object_img.shape

                    # Get the dimensions of the base image
                    base_image_height, base_image_width, _ = base_image.shape

                    # Check if the coordinates are within the dimensions of the base image
                    if y1 + object_height <= base_image_height and x1 + object_width <= base_image_width:
                        # Paste the object on the base image at the original coordinates
                        base_image[y1:y1 + object_height, x1:x1 + object_width] = object_img
                    else:
                        # Skip this annotation line
                        skipped_annotations.append(line)
                        continue

                    # Save the augmented image
                    output_image_file = "output{}.jpg".format(i)
                    output_image_path = os.path.join(output_images_dir, output_image_file)
                    cv2.imwrite(output_image_path, base_image)

            # Update the annotation file as well
            filtered_lines = [line for line in lines if line.strip() not in skipped_annotations]

            # Write the filtered lines back to the file
            with open(annotation_path, 'w') as file:
                file.writelines(filtered_lines)

    print("Extraction complete!")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add objects from a directory to a base image')
    parser.add_argument('--image_dir', required=True, help='Path to the folder containing image and label folders')
    parser.add_argument('--base_image_dir', required=True, help='Path to the base image directory')
    parser.add_argument('--output_dir', help='Path to the output directory')
    parser.add_argument('--num_outputs', type=int, default=5, help='The number of outputs to be generated. Default = 5')

    args = parser.parse_args()
    extract_objects(image_dir=args.image_dir, base_image_dir=args.base_image_dir, output_dir=args.output_dir, num_outputs=args.num_outputs)