import os
import cv2
import numpy as np
import xml.etree.ElementTree as ET

ns = {
    'alto': 'http://www.loc.gov/standards/alto/ns-v4#'
}

folder = "2pages"

xml_files = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.xml')]

for file in xml_files:
    filename = file.split(".")[0]
    try:
        # Load the XML file
        tree = ET.parse(f'{filename}.xml')
        root = tree.getroot()

        # Load the image
        image = cv2.imread(f'{filename}.jpeg')

    except BaseException as e:
        print(e)
        print("File not found")
        exit()

    for page in root.findall('.//alto:Page', ns):
        n = 0
        # Iterate through each TextBlock element
        for text_block in page.findall('.//alto:TextBlock', ns):
            # Iterate through each TextLine element within the TextBlock
            for text_line in text_block.findall('.//alto:TextLine', ns):
                coords = text_line.find('.//alto:Polygon', ns).attrib['POINTS']
                label = text_line.get('TAGREFS')
                if label == "LT16":
                    continue
                points = np.array([[int(n) for n in point.split(',')] for point in coords.split()], np.int32)
                points = points.reshape((-1, 1, 2))

                # Create a mask and perform the crop
                mask = np.zeros(image.shape[0:2], dtype=np.uint8)
                cv2.fillPoly(mask, [points], (255))

                # Crop the image
                result = cv2.bitwise_and(image, image, mask=mask)
                x, y, w, h = cv2.boundingRect(points)  # Get the bounding box of the polygon
                cropped_image = result[y:y+h, x:x+w]

                # Save the cropped image
                try:
                    cv2.imwrite(f'{filename}_{n}_cropped_line.jpg', cropped_image)
                except BaseException as e:
                    print(e)
                    print("Error saving image")

                text = text_line.find('.//alto:String', ns).attrib['CONTENT']
                print(text)
                if text:
                    with open(f"{filename}_{n}_text.txt", "w") as f:
                        f.write(text)
                n += 1