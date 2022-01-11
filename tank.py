from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar

app = Ursina()
window.borderless = False
window.title = f"Tanks"
window.icon = "assets/favicon.ico"
window.exit_button.visible = False
window.fps_counter.visible = False
window.center_on_screen()

sound_1 = Audio('assets/sounds/sound_1',loop = False, autoplay = False)
sound_2 = Audio('assets/sounds/sound_2',loop = False, autoplay = False)
sound_3 = Audio('assets/sounds/sound_3',loop = False, autoplay = False)
sound_4 = Audio('assets/sounds/sound_4',loop = False, autoplay = False)
sound_5 = Audio('assets/sounds/sound_5',loop = False, autoplay = False)
sound_6 = Audio('assets/sounds/sound_6',loop = True, autoplay = True)
sound_7 = Audio('assets/sounds/sound_7',loop = False, autoplay = False)
sound_8 = Audio('assets/sounds/sound_8',loop = True, autoplay = False)
sound_9 = Audio('assets/sounds/sound_9',loop = False, autoplay = False)
sound_10 = Audio('assets/sounds/sound_10',loop = True, autoplay = False)
sound_11 = Audio('assets/sounds/sound_11',loop = False, autoplay = False)

random.seed(0)
Entity.default_shader = lit_with_shadows_shader
application.development_mode = False

class FirstPersonController(FirstPersonController):
    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.rotation_x * (held_keys['d'] - held_keys['a'])
            ).normalized()

        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit:self.position += self.direction * self.speed * time.dt

        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))

            if ray.distance <= self.height+.1:
                if not self.grounded:self.land()
                self.grounded = True
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5:self.y = ray.world_point[1]
                return
            else:self.grounded = False

            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity

ground = Entity(model='plane', collider='box', scale=80, texture='assets/grass_texture.jpg', texture_scale=(4,4))
player = FirstPersonController(model='assets/models/tank2/IS',collider='box',texture='IS.dds',color=color.yellow,speed=4,gravity=0,z=ground.scale_x/2 - 5,rotation_y = 180)

restart_btn = Button(text='Новая игра', color=color.white, scale_x=.4,position = (0,-.2,-1),scale_y = .05,model = 'cube',visible=False)
restart_btn.on_click = application.hot_reloader.reload_code

hb = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5,position=(-.25,-.42,1),max_value=100)
lamp = Button(color=color.rgb(255,255,255,a=0),position = (-.2,.1,-1),model = 'cube',icon='assets/lamp.png',scale=(.15,.15),visible=False)

player.camera_pivot.position = (0,4,-1)

player.rotation_x -= held_keys['a']
player.rotation_x= clamp(player.rotation_x, -90, 90)

player.cursor = Entity(parent=camera.ui,model='quad',color=color.white,scale=.03,rotation_z=90,texture='assets/crosshair.png',default_shader=None) 

fps_counter = Text(position=Vec3(-.87,0.48,0),text = '60 fps')
timer_text = Text(position=Vec3(-.87,0.44,0))
count_text = Text(position=Vec3(-.87,0.40,0))
message_area = Text(origin=(0,15))

p = Panel(scale=5,visible = False)
hp_p = Panel(scale=5,color = color.red)

descr = dedent('''
    <scale:1.5>Победа!<scale:1>

    Все танки противника уничтожены

    Чтобы продолжить, нажмите f5''').strip()

Text.default_resolution = 1080 * Text.size
win_text = Text(text=descr, origin=(0,-1.5),visible=False,color=color.white,z=-1)

descr = dedent('''
    <scale:1.5>Поражение<scale:1>

    Вы уничожены

    Чтобы продолжить, нажмите f5''').strip()

Text.default_resolution = 1080 * Text.size
loose_text = Text(text=descr, origin=(0,-1.5),visible=False,color=color.white,z=-1)

gun = Entity(model='cube',parent=camera,position=(0,2,-2),scale=(.3,.2,1),origin_z=-.5,color=color.red,on_cooldown=False,visible=False)
gun.muzzle_flash = Entity(parent=gun,z=1,world_scale=.5,model='quad',color=color.yellow,enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

cup = Entity(model = 'assets/models/cup/cup',collider = 'box',scale = 0.2,color = color.rgb(255,215,0,a=255),position = Vec3(0,1.5,-round(ground.scale_x/2)))

pointer = Entity(model='assets/models/pointer/pointer.fbx',position=cup.position,y = 10,color=color.red,scale = 0.009)
pointer.look_at = (player.x,5,player.z)

cursor = Entity(parent=camera.ui,model='quad',color=color.white,scale=1.1,rotation_z=90,texture='assets/sniper_mode.png',visible=False) 

editor_camera = EditorCamera(enabled=False, ignore_paused=True)

def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        editor_camera.position = (0,80,0)
        editor_camera.look_at((0,0,0))
        editor_camera.rotation_y = 180
        hb.visible = not editor_camera.enabled
        message_area.visible = not editor_camera.enabled
        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)

for i in range(round(ground.scale_x/3*2)):
    Entity(model='assets/models/rock/Rock1',y=-1, scale=1, texture='assets/models/rock/Rock-Texture-Surface.jpg',x=random.uniform(-round(ground.scale_x/2),round(ground.scale_x/2)),z=random.uniform(-round(ground.scale_x/2)+10,round(ground.scale_x/2)-10),collider='assets/models/rock/Rock1',scale_y = random.uniform(2,4),rotation_y = random.randint(0,360))

for i in range(round(ground.scale_x/4)):
    Entity(model = 'assets/models/tree/Tree.fbx',scale = 0.01,x=random.uniform(-round(ground.scale_x/2),round(ground.scale_x/2)),z=random.uniform(-round(ground.scale_x/2)+10,round(ground.scale_x/2)-10))

class Wall(Entity):
    def __init__ (self,position=(0,0,0),scale_x = 0,scale_z = 0,rotation=(0,0,0),model='cube',texture='brick',texture_scale=(30,3)):
        super().__init__(
        model=model, scale=2,
        texture=texture,
        rotation = rotation,
        texture_scale=texture_scale,
        position = position,
        collider='box',
        scale_y = 6,
        scale_x = scale_x,
        scale_z = scale_z,
        color=color.white
        )

Wall((0,2,round(ground.scale_x/2)),round(ground.scale_x),.5,(0,0,0))
Wall((round(ground.scale_x/2),2,0),.5,round(ground.scale_x),(0,0,0))
Wall((-round(ground.scale_x/2),2,0),.5,round(ground.scale_x),(0,0,0))
Wall((23,2,-round(ground.scale_x/2)),round(ground.scale_x/2.1),.5,(0,0,0))
Wall((-23,2,-round(ground.scale_x/2)),round(ground.scale_x/2.1),.5,(0,0,0))
Wall((0,0,-round(ground.scale_x/2)),round(ground.scale_x/3),.5,(90,0,0))
Wall((0,0,round(ground.scale_x/2)-3),round(ground.scale_x/3),.5,(90,0,0))

global timer,player_hp,timer_enemy

i = 0
i_2 = 0
i_3 = 0
timer = 0
player_hp = 100
timer_enemy = 0
enemy_count = 0
max_enemy = 2
msg_time = 0

def update():
    global i,timer,i_2,player_hp,i_3,timer_enemy,msg_time

    count_text.text = f'Уничтожено танков противника {enemy_count} из {max_enemy}'
    if held_keys['left mouse']:shoot()

    hp_p.alpha = max(0, hp_p.alpha - time.dt)
    msg_time = max(0, msg_time - time.dt)

    if msg_time == 0:message_area.visible = False
    if msg_time > 0:message_area.visible = True

    player.rotation_y += held_keys['d']*3
    player.rotation_y -= held_keys['a']*3

    if i > 60:
        timer = 0
        i = 0
    i += 0.5
    timer_text.text = f'Перезарядка... {round(i*15/100)}0%'

    if i_2 > 60:
        fps_counter.text = f'{str(int(1//time.dt))} fps'
        i_2 = 0
    i_2 += 0.5

    if i_3 > 60:
        timer_enemy = 0
        i_3 = 0
    i_3 += 0.3

    if timer == 0:timer_text.text = 'Готов!'
    hb.value = player_hp

    cup_hit_info = cup.intersects()
    if cup_hit_info.hit and enemy_count == max_enemy: 
        p.visible = True
        win_text.visible = True
        application.pause()
        mouse.visible = True
        mouse.locked = False
        sound_4.stop(destroy=True)
        restart_btn.visible=True
        lamp.visible = False
        message_area.visible = False

    if cup_hit_info.hit and enemy_count != max_enemy:
        set_message('Уничтожьте все танки противника!')

    if player_hp == 0:
        hp_p.visible = True
        loose_text.visible = True
        application.pause()
        mouse.visible = True
        mouse.locked = False
        sound_4.stop(destroy=True)
        restart_btn.visible=True
        lamp.visible = False

def input(key):
    if key == 'scroll up':
        sound_1.play()
        camera.fov = 30
        sound_6.volume = 0.5
        cursor.visible = True

    if key == 'scroll down':
        sound_2.play()
        camera.fov = 90
        sound_6.volume = 1
        cursor.visible = False

    sound_4.volume = 0.6

    if key == 'w':sound_4.play()
    if key == 'w up':sound_4.stop(destroy=True)

    if key == 's':sound_4.play()
    if key == 's up':sound_4.stop(destroy=True)

    if key == 'd':
        sound_7.play()
        sound_8.play()

    if key == 'd up':
        sound_7.stop(destroy=True)
        sound_8.stop(destroy=True)
        sound_9.play()

    if key == 'a':
        sound_7.play()
        sound_8.play()

    if key == 'a up':
        sound_7.stop(destroy=True)
        sound_8.stop(destroy=True)
        sound_9.play()
    
    if key == 'escape':application.quit()

def set_message(message):
    global msg_time
    msg_time = 0
    message_area.text = message
    msg_time = 8

def shoot():
    global timer
    if not gun.on_cooldown and timer == 0:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        sound_11.volume = 0.6
        sound_11.stop(destroy=True)
        sound_11.play()
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
        timer = 5

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='assets/models/tank/Tiger_I',collider='assets/models/tank/Tiger_I',texture='PzVl_Tiger_I.dds',y=0.1,**kwargs)
        self.health_bar = Entity(parent=self, y=4, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.z = -round(ground.scale_x/2)+8

    def shoot(*kwargs):
        global player_hp
        sound_5.volume = 0.6
        sound_5.stop(destroy=True)
        sound_5.play()
        player_hp -= random.randint(5,10)
        hp_p.alpha = 150

    def update(self):
        global timer_enemy
        dist = distance_xz(player.position, self.position)
        if dist > 40:return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at(player.position)
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 60, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 4
                lamp.visible = True
                set_message('В вас целится противник!')
                if timer_enemy == 0:
                    self.shoot()
                    timer_enemy = 5

        else:lamp.visible = False
        if self.hovered:self.color = color.rgb(255,138,138,a=255)
        if not self.hovered:self.color = color.white

    @property
    def hp(self):return self._hp

    @hp.setter
    def hp(self, value):
        global enemy_count
        self._hp = value
        if value <= 0:
            sound_3.volume = 3
            sound_3.play()
            lamp.visible = False
            enemy_count += 1
            destroy(self)
            set_message('Танк противника уничтожен!')
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

enemies = [Enemy(x=x*16) for x in range(max_enemy)]

Sky()
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))

set_message('Поехали!')

app.run()