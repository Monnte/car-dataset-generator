import bpy
import math
import random
import bpy
from bpy_extras.object_utils import world_to_camera_view
import json
import argparse
import os
import time

PRECISION_DECIMALS = 3

def get_float_str(number):
    return f'{number:.{PRECISION_DECIMALS}f}'


# https://blender.stackexchange.com/questions/87754/ray-cast-function-not-able-to-select-all-the-vertices-in-camera-view/87774#87774
def generate_anotation(model_name, render_number, hdri_number, target_name, resolution, metadata = {}):
    scene = bpy.context.scene
    cam = bpy.data.objects['Camera']
    target = bpy.data.objects[target_name]
    bpy.ops.object.select_all(action='DESELECT')

    data = {}
    data['camera'] = {
        'x': get_float_str(cam.location.x),
        'y': get_float_str(cam.location.y),
        'z': get_float_str(cam.location.z),
        'rotation_x': get_float_str(cam.rotation_euler.x),
        'rotation_y': get_float_str(cam.rotation_euler.y),
        'rotation_z': get_float_str(cam.rotation_euler.z),
        'fov': get_float_str(math.degrees(cam.data.angle)),
    }
    data['meta'] = metadata


    limit = 0.1

    mWorld = target.matrix_world
    vertices = [mWorld @ v.co for v in target.data.vertices]


    data['vertices'] = []
    for i, v in enumerate( vertices ):
        co2D = world_to_camera_view( scene, cam, v )
        data['vertices'].append({
            'v_id': i,
            'x': get_float_str(co2D.x * resolution[0]),
            'y': get_float_str(co2D.y * resolution[1]),
            'v': False
        })

        if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0 and co2D.z >0:
            location= scene.ray_cast(bpy.context.window.view_layer.depsgraph, cam.location, (v - cam.location).normalized())
            if location[0] and (v - location[1]).length < limit:
                data['vertices'][i]['visible'] = True

    with open(f'{model_name}_render_{render_number}_{hdri_number}.json', 'w') as outfile:
        json.dump(data, outfile)


def setup_camera(target_name, camera_name="Camera"):
    target = bpy.data.objects[target_name]
    camera = bpy.data.objects[camera_name]

    rotation_x = math.radians(random.uniform(45,60))
    rotation_z = math.radians(random.uniform(0,360))

    fov_radians = math.radians(random.uniform(30, 70))

    camera.rotation_euler = (rotation_x, 0, rotation_z)
    camera.data.lens_unit = 'FOV'
    camera.data.angle = fov_radians

    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.ops.view3d.camera_to_view_selected()

    camera.data.angle += math.radians(random.uniform(1, 3))

def load_gltlf(model_path):
    bpy.ops.import_scene.gltf(filepath=model_path)
    loaded_objects = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')

    if loaded_objects:
        # join all objects to one
        meshes = [m for m in bpy.context.scene.objects if m.type == 'MESH']
        for mesh in meshes:
            mesh.select_set(state=True)
            bpy.context.view_layer.objects.active = mesh
        bpy.ops.object.join()
        # ================================

        name = bpy.context.object.name
        bpy.ops.object.select_all(action='DESELECT')
        return name
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

def clear_existing_objects():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def render_and_save(model_name, render_number, hdri_number, render_resolution):
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = f'{model_name}_render_{render_number}_{hdri_number}.png'
    bpy.context.scene.render.resolution_x = render_resolution[0]
    bpy.context.scene.render.resolution_y = render_resolution[1]
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.color_depth = '16'
    bpy.context.scene.render.image_settings.compression = 0
    bpy.ops.render.render(write_still=True)

def rotate_light():
    bpy.data.objects['camera_rotator'].rotation_euler.z += math.radians(random.uniform(0, 360))

def get_light_metadata():
    return {
        "rotation_z": get_float_str(bpy.data.objects['camera_rotator'].rotation_euler.z),
        "energy": get_float_str(bpy.data.objects['Light'].data.energy),
        "angle": get_float_str(bpy.data.objects['Light'].data.angle),
    }

def setup_environment(target_name):
    target = bpy.data.objects[target_name]
    lowest_z = min([(target.matrix_world @ v.co).z for v in target.data.vertices])

    # remove old light
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Light'].select_set(True)
    bpy.ops.object.delete()

    # setup new light
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 0))
    bpy.context.object.data.energy = 10
    bpy.context.object.data.angle = math.radians(random.uniform(10,90))
    bpy.context.object.name = "Light"

    # setup light rotator
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
    bpy.context.object.name = "camera_rotator"
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Light'].select_set(True)
    bpy.data.objects['camera_rotator'].select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    rotate_light()

    # create shadow catcher
    location = (target.location.x, target.location.y, lowest_z)
    bpy.ops.mesh.primitive_plane_add(size=1000, enter_editmode=False, align='WORLD', location=location)
    bpy.context.object.is_shadow_catcher = True
    bpy.context.object.visible_diffuse = False
    bpy.context.object.visible_glossy = False


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--config", type=str, default="./config.json")
    args, unknown = args.parse_known_args()

    assert os.path.exists(args.config), f"Config file {args.config} does not exist"

    with open(args.config) as f:
        config = json.load(f)

    random.seed(time.time())
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = config.get("render_device", "GPU")
    bpy.context.scene.cycles.samples = config.get("render_samples", 1024)

    render_resolution = config.get("render_resolution", [1080, 1080])
    redners_per_model = config.get("renders_per_model", 100)
    hdris = config.get("hdris", [])
    models = config.get("models", [])
    for i, model in enumerate(models):
        clear_existing_objects()

        model_path = model.get("path", None)
        save_path = model.get("save_path", None)
        if not model_path or not save_path:
            print(f"Model {i} does not have path")
            continue

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        target_name = load_gltlf(model_path)
        if not target_name:
            print(f"Failed to load model {model_path}")
            continue

        setup_environment(target_name)
        for j, hdri in enumerate(hdris):
            hdr_path = hdri.get("path", None)
            if not hdr_path:
                print(f"HDR {i} does not have path")
                continue

            set_hdri_background(hdr_path)
            for k in range(redners_per_model):
                setup_camera(target_name)
                if k % 10 == 0:
                    rotate_light()
                metadata = {"hdri": hdr_path, "model": model_path, "light": get_light_metadata()}
                generate_anotation(save_path, k, j, target_name, render_resolution, metadata)
                render_and_save(save_path, k,j, render_resolution)

if __name__ == "__main__":
    main()
