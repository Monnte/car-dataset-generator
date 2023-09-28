# Generate marker images from json files anotations.
import cv2
import json
import argparse
import os
import math
import tqdm

VERTEX_VISIBILITY_THRESHOLD = 0.5

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--folder', type=str, default='./renders')
	args = parser.parse_args()

	file_names = os.listdir(args.folder)
	image_names = [f for f in file_names if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

	for image_name in tqdm.tqdm(image_names):
		image_path = os.path.join(args.folder, image_name)
		json_path = os.path.join(args.folder, image_name.split('.')[0] + '.json')

		if not os.path.exists(json_path):
			continue


		image = cv2.imread(image_path)
		with open(json_path) as f:
			data = json.load(f)

		for vertex in data['vertices']:
			visibility = float(vertex['v'])
			if visibility != 0 and visibility > VERTEX_VISIBILITY_THRESHOLD:
				position = (int(float(vertex['x'])), int(float(vertex['y'])))
				position = (position[0], position[1])
				color = (255 - int(255.0 * visibility), int(255.0 * visibility), 0)
				cv2.drawMarker(image, position, color, cv2.MARKER_CROSS, 5, 1)

		image_new_name = image_name.split('.')[0] + '_markers.' + image_name.split('.')[1]
		cv2.imwrite(os.path.join(args.folder, image_new_name), image)
	
