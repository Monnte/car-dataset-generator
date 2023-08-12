import bpy
import math
import mathutils
import random

def clear_existing_objects():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def load_gltlf(model_path):
    bpy.ops.import_scene.gltf(filepath=model_path)
    loaded_objects = bpy.context.selected_objects

    if loaded_objects:
        return loaded_objects[0].name
    else:
        return None

def set_hdri_background(hdr_path):
    node_tree = bpy.context.scene.world.node_tree
    tree_nodes = node_tree.nodes

    tree_nodes.clear()

    node_background = tree_nodes.new(type='ShaderNodeBackground')
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    node_environment.image = bpy.data.images.load(hdr_path)

    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')

    links = node_tree.links
    links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

def setup_camera(camera_name, target_name, distance, camera_height):
    camera = bpy.data.objects[camera_name]
    target = bpy.data.objects[target_name]

    camera.location = target.location + mathutils.Vector((0, -distance, camera_height))
    camera.rotation_euler = (math.radians(90), 0, 0)

    track_to_constraint = camera.constraints.new(type='TRACK_TO')
    track_to_constraint.target = target
    track_to_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    track_to_constraint.up_axis = 'UP_Y'

def rotate_camera_around_object(camera_name, target_name, angle_degrees):
    camera = bpy.data.objects[camera_name]
    target = bpy.data.objects[target_name]

    # Calculate the rotation matrix
    angle_radians = math.radians(angle_degrees)
    rotation_matrix = mathutils.Matrix.Rotation(angle_radians, 3, 'Z')

    # Calculate the new camera location relative to the target
    relative_location = camera.location - target.location
    new_relative_location = rotation_matrix @ relative_location

    # Set the new camera location
    camera.location = target.location + new_relative_location

def render_and_save(model_name, render_number):
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = f'renders/{model_name}_render_{render_number}.png'
    bpy.ops.render.render(write_still=True)

def main():
    model_name = "bmw"
    camera_name = "Camera"
    total_renders = 10
    total_rotations = 1
    min_distance = 5
    max_distance = 20
    min_camera_height = 2
    max_camera_height = 4
    min_rotation = 0
    max_rotation = 360

    clear_existing_objects()
    target_name = load_gltlf("./assets/models/bmw/scene.gltf")
    set_hdri_background("./assets/hdr/background.hdr")

    if not target_name:
        print("Failed to load model")
        return

    random.seed(0)
    for i in range(total_renders):
        random_distance = random.uniform(min_distance, max_distance)
        random_camera_height = random.uniform(min_camera_height, max_camera_height)
        random_rotation = random.uniform(min_rotation, max_rotation)
        print(f"Generating render {i} with distance {random_distance}, camera height {random_camera_height}, and rotation {random_rotation}")

        setup_camera(camera_name, target_name, random_distance, random_camera_height)

        for j in range(total_rotations):
            rotate_camera_around_object(camera_name, target_name, random_rotation)
            render_and_save(f"{model_name}_render_{i}", j)

if __name__ == "__main__":
    main()
