import cv2
import json
import argparse
import os
import math
import scipy.spatial
import csv
import tqdm

VERTEX_VISIBILITY_THRESHOLD = 0.5

if __name__ == '__main__':
	limit = 1
	model_data = {}


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

		model = data['meta']['model']
		if model not in model_data:
			model_data[model] = {}
			for vertex in data['vertices']:
				model_data[model][vertex['id']] = 0
		
		# use sift to find the keypoints
		sift = cv2.SIFT_create()
		kp = sift.detect(image, None)
		kp, des = sift.compute(image, kp)

		# # draw keypoints deep copy
		# image_kp = image.copy()
		# cv2.drawKeypoints(image, kp, image_kp, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		# cv2.imwrite('sift_keypoints.jpg', image_kp)

		# the y is inverted in the json file
		vertices = [(float(vertex['x']), image.shape[0] - float(vertex['y'])) for vertex in data['vertices']]
		tree = scipy.spatial.KDTree(vertices)

		# find closest vertex for each keypoint
		for point in kp:
			# find closest vertex
			distance, index = tree.query(point.pt)
			# check if distance is smaller than limit
			if distance < limit and float(data['vertices'][index]['v']) > VERTEX_VISIBILITY_THRESHOLD:
				# increment counter for vertex
				model_data[model][index] += 1

				# draw marker
				# color = (0, 255, 0)
				# position = (round(point.pt[0]), round(point.pt[1]))
				# print(position)
				# cv2.drawMarker(image, position, color, cv2.MARKER_CROSS, 10, 1)
				# # draw red marker at vertex position
				# vertex_position = vertices[index]
				# color = (0, 0, 255)
				# position = (round(vertex_position[0]), round(vertex_position[1]))
				# cv2.drawMarker(image, position, color, cv2.MARKER_CROSS, 10, 1)

	

	# # save image
	# image_new_name = 'shifter.jpg'
	# cv2.imwrite(image_new_name, image)

	for model in model_data:
		outpu_name = os.path.join(args.folder, model + '_points.json')
		with open(outpu_name, 'w') as outfile:
			json.dump(model_data[model], outfile, separators=(',', ':'))