from ursina import *


def update():
    if cube.z < -8:
        cube.z = cube.z + 2 * time.dt
    phase_1()
    phase_2()
    shape()
    status()
    camera_position_1()
    failed_1()


def phase_1():
    if cube2.z < 7:
        cube2.z = cube2.z + 2 * time.dt
    if cube2.y < -8.69:
        cube2.y = cube2.y + 2 * time.dt


def phase_2():
    if cube4.x > - 9.63:
        cube4.x = cube4.x - 2*time.dt
    if cube4.y < -8.69:
        cube4.y = cube4.y + 2 * time.dt


def shape():
    if shape_1.z < -2.7:
        shape_1.z = shape_1.z + 2 * time.dt
    if shape_1.y < -6.8:
        shape_1.y = shape_1.y + 2 * time.dt


def status():
    if passed.x < 30:
        passed.x = passed.x + 45 * time.dt


def camera_position_1():
    if camera.rotation_x > 17:
        camera.rotation_x = camera.rotation_x - time.dt
    if camera.x > -51:
        camera.x = camera.x - 5*time.dt
    if camera.z < 48:
        camera.z = camera.z + 1.5*time.dt
    if camera.rotation_y > 130:
        camera.rotation_y = camera.rotation_y - 6*time.dt


def failed_1():
    if failed.x > -8.3:
        failed.x = failed.x - 2 * time.dt
    if failed.y < -6.6:
        failed.y = failed.y + time.dt


app = Ursina()
camera.position = (-10, 15, 30)
camera.rotation = (25, 180, 0)
# EditorCamera()
platform = Entity(model="plane", collider='mesh', color=color.rgb(205, 212, 211), scale=70, position=(0, -10, 0))
model = Entity(model='palpha', texture='app', collider='mesh', position=(-2, -9.5, 0))
cube = Entity(model='triangle_bis', color=color.rgb(76, 76, 76), position=(-3, -9, -19))
cube2 = Entity(model='triangle_bis', texture='cirrcle', collider='mesh', position=(0.2, -19.7, -17),
               scale=(.7, .7, .7))
cube4 = Entity(model='triangle_bis', texture='cirrcle', collider='mesh', position=(18, -22, 7), scale=(.7, .7, .7))
cube3 = Entity(model='cube', collider='mesh', color=color.gray, position=(-6.4, -8, 7), scale=(2, 2, 3.5))

success_prism = Entity(model='prism', collider='mesh', position=(0.4, -6.95, -2.8), color=color.rgb(1, 47, 120),
                       rotation=(90, 0, 0), scale=(0.7, 2, 0.7))
success_square = Entity(model='cube', collider='mesh', color=color.rgb(1, 47, 120), position=(-2.8, -6.8, -2.7))
success_sphere = Entity(model='sphere', collider='mesh', color=color.rgb(1, 47, 120), position=(-6.3, -6.8, -2.9),
                        scale=1.49)
shape_1 = Entity(model='prism', collider='mesh', color=color.rgb(2, 94, 240), position=(0.4, -20, -16),
                 rotation=(90, 0, 0), scale=(0.7, 2.1, 0.7))

success_cube2 = Entity(model='cube', collider='mesh', color=color.rgb(5, 92, 2), position=(-3, -6.7, 10.5), scale=0.99)
success_cube3 = Entity(model='cube', collider='mesh', color=color.rgb(5, 92, 2), position=(0.5, -6.7, 10.5), scale=0.99)
success_cube1 = Entity(model='cube', collider='mesh', color=color.rgb(5, 92, 2), position=(-6.5, -6.7, 10.5),
                       scale=0.99)


alert_cube = Entity(model='cube', collider='mesh', color=color.rgb(122, 0, 0), position=(-8.3, -6.6, 7.5), scale=0.8)
failed = Entity(model='cube', collider='mesh', color=color.rgb(212, 26, 13), position=(16.3, -15.6, 7.5), scale=0.81)

passed = Entity(model='rejected', collider='mesh', color=color.rgb(212, 26, 13), position=(-610, 0, 00), scale=5,
                rotation=(90, 310, 0))
app.run()
