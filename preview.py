# Simple script to view output from sifter, show markers.
import json
import cv2
VERTEX_VISIBILITY_THRESHOLD = 0.5

with open('bmw.json') as f:
	data = json.load(f)

sorted_keys = sorted(data, key=lambda x: data[x], reverse=True)

image = cv2.imread('./renders/000000.jpg')

with open('./renders/000000.json') as f:
	img_data = json.load(f)

for i in range(64):
	id = int(sorted_keys[i])
	vertex = img_data['vertices'][id]
	visibility = float(vertex['v'])
	if visibility != 0 and visibility > VERTEX_VISIBILITY_THRESHOLD:
		position = ((float(vertex['x'])), (float(vertex['y'])))
		position = (round(position[0]), round(position[1]))
		position = (int(position[0]), int(position[1]))
		position = (position[0], image.shape[0] - position[1])
		color = (255 - int(255.0 * visibility), int(255.0 * visibility), 0)
		cv2.drawMarker(image, position, color, cv2.MARKER_CROSS, 5, 1)

# save image
image_new_name = 'bmw_markers.jpg'
cv2.imwrite(image_new_name, image)