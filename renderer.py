import bpy
from random import uniform, choice
from numpy import cos, sin, pi
import os

cwd = os.getcwd()

### SETTINGS

# Define viewing angle bounds and other params
input_file = cwd + "/blender/IS4_new.blend"                 # Relative path to input blender file
output_path = cwd + "/renders/"                             # Relative render output path
n_renders = 2000                                            # Number of rendered images
render_engine = 'BLENDER_EEVEE'                             # Blender rendering engine

img_width = 240     # X size of the image
img_heigth = 180    # Y size of the image

min_azimuth = -150          # Negative bound of lateral camera rotation
max_azimuth = 150           # Positive bound of lateral camera rotation
min_elevation = -25         # Negative bound of pitching camera rotation
max_elevation = -5          # Positive bound of pitching camera rotation
min_distance = 6            # Minimum distance from the center of rendered scene
max_distance = 10           # Maximum distance from the center of rendered scene
max_ang_deviation = 3.      # Maximum angular deviation from optimal view angle (lateral, pitching)
max_roll_deviation = 5      # Maximum angular deviation from optimal view angle (roll)
empty_chance = 0.67         # Chance of not rendering the tank in the scene (0-1)
dummy_chance = 0.5          # Chance of rendering a dummy in the scene ONLY IF tank is not being rendered (0-1)

base_height = 1.5           # Base height of central point at which the camera looks
y_offset = 2.25             # Forward camera offset

focal_length = 25           # Focal length of camera lens

# Parts of the scene to manipulate in rendering
tank_parts = ['Gun', 'Hull', 'Track_Left', 'Track_Right', 'Turret', 'Wheels_Left', 'Wheels_Right']
tank_materials = ['TankMatArctic', 'TankMatClassic', 'TankMatNavy', 'TankMatCamo', 'TankMatTan', 'TankMatDark']
ground_names = ['Asphalt', 'Grass', 'Mud', 'Pavement']
sky_names = ['NiceSky', 'UglySky']

### EXECUTION ###########################################################

# Function to set camera position
def set_camera_position(camera, azimuth, elevation, distance, rand_azimuth = 0, rand_elevation = 0, rand_roll = 0):

    # Calculate camera position
    x = distance * cos(elevation - pi/2.) * sin(-azimuth)
    y = distance * cos(elevation - pi/2.) * cos(-azimuth) + y_offset
    z = distance * sin(elevation - pi/2.) - base_height

    # Set camera position
    camera.location = (-x, -y, -z)
    print(x, y, z)

    rand_az = uniform(-rand_azimuth, rand_azimuth)
    rand_elev = uniform(-rand_elevation, rand_elevation)
    rand_ro = uniform(-rand_roll, rand_roll)

    camera.rotation_euler = (elevation + rand_elev, rand_ro, azimuth + rand_az)


# Function to swap textures on objects
def change_material(obj, new_material_name):

    material_slots = obj.material_slots
    slot = material_slots[0]
    slot.material = bpy.data.materials.get(new_material_name)

def get_random_tank_material():

    return choice(tank_materials)

def get_random_scenery():

    for ground_name in ground_names:
        obj = bpy.data.objects[ground_name]
        obj.hide_render = True

    for sky_name in sky_names:
        obj = bpy.data.objects[sky_name]
        obj.hide_render = True

    bpy.data.objects[choice(ground_names)].hide_render = False
    bpy.data.objects[choice(sky_names)].hide_render = False

    lamp = bpy.data.lights.get('Lamp')
    lamp.energy = uniform(0.25, 7.5)


# Function to render and save image
def render_and_save(file_path):
    bpy.context.scene.render.filepath = file_path
    bpy.ops.render.render(use_viewport = True, write_still=True)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Load model
bpy.ops.wm.open_mainfile(filepath=input_file)
bpy.context.scene.render.engine = render_engine 


# Get all existing materials in the Blender file
existing_materials = bpy.data.materials

# Iterate over each material
for material in existing_materials:
    print("Material:", material.name)

# Set resolution
render = bpy.context.scene.render
render.resolution_x = 2 * img_width  # Width of the image
render.resolution_y = 2 * img_heigth  # Height of the image

# Set up camera
cam = bpy.data.objects['Camera']
cam.location = (0, -5, 0)
cam.rotation_euler = (pi/2, 0, 0)
cam.data.lens= focal_length

scene = bpy.context.scene
scene.camera = cam

# Generate random viewing angle and render 
torad = pi/180.

# Reload textures
for image in bpy.data.images:
        image.reload()

for i in range(n_renders):
    # Generate random viewing angle
    azimuth = torad * uniform(min_azimuth, max_azimuth)
    elevation = pi/2. + torad * uniform(min_elevation, max_elevation)
    distance = uniform(min_distance, max_distance)

    get_random_scenery()
    set_camera_position(cam,
                        azimuth, 
                        elevation, 
                        distance, 
                        torad*max_ang_deviation, 
                        torad*max_ang_deviation, 
                        torad*max_roll_deviation)
    
    dummy = bpy.data.objects['Dummy']
    dummy.hide_render = True

    if uniform(0,1) < empty_chance:
        for part_name in tank_parts:
            part = bpy.data.objects[part_name]
            part.hide_render = True
        
        if uniform(0,1) < dummy_chance:
            dummy_material = get_random_tank_material()
            change_material(dummy, dummy_material)
            dummy.hide_render = False

        savename = output_path + str(i) + "_nothing"

    else:
        new_material = get_random_tank_material()
        for part_name in tank_parts:
            part = bpy.data.objects[part_name]
            part.hide_render = False
            change_material(part, new_material)

        savename = output_path + str(i) + "_tank"


    # Set camera position
    print("### IMAGE ", str(i), " ###")
    print(cam.location, cam.rotation_euler)

    # Render and save image

    render_and_save(savename + ".png")