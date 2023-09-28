# Car dataset generator

## Description

This script generates a dataset of cars in different positions and with different lighting. The model is always whole captured by the camera.

Add your own models and hdri maps to `models` and `hdri` directories respectively.

## Anotations

Each vertex of the model is annotated with pixel position in output image and if the vertex is visible in the image.

### How to run

```bash
blender -b -P ./main.py
```

## Examples

Examples can be found in `dataset` directory.

<!-- ![image1](./dataset/000002.jpg)
![image1](./dataset/000006.jpg)
![image1](./dataset/000001.jpg) -->

<div style="display: flex; flex-direction: row; justify-content: space-between">
 <img src="./dataset/example.jpg" width="45%">
 <img src="./dataset/example_markers.jpg" width="45%">
</div>

<br>
<div style="display: flex; flex-direction: row; justify-content: space-between">
 <img src="./dataset/000002.jpg" width="30%">
 <img src="./dataset/000006.jpg" width="30%">
 <img src="./dataset/000001.jpg" width="30%">
</div>
