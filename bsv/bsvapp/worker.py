# Utilizes Celery workers to delegate multiprocessing tasks.
from celery.decorators import task
# Modules
from .visualizer import BlinkStickViz
from .color_programs import BlinkStickColors

# Dummy task to verify celery works. Visit /celery URL.
@task(name="sum_two_numbers")
def add(x, y):
    return(x + y)

# Visualizations
@task(name="visualizer", serializer='json')
def start_visualizer(minimum, maximum, modes):
    BlinkStickViz(sensitivity=1.3, rate=44100, chunk=1024, channels=2, max_int=maximum, min_int=minimum, transmit=True, 
            receive=False, network_interface='wlan0', inputonly=False, led_count=32, device=None).main(modes=modes) 

@task(name="start_rotating_rainbow", serializer='json')
def start_rotating_rainbow():
    BlinkStickColors(transmit=True, network_interface='wlan0').rotating_rainbow()    

@task(name="start_rainbow_snake", serializer='json')
def start_rainbow_snake():
    BlinkStickColors(transmit=True, network_interface='wlan0').rainbow_snake()

@task(name="start_breathing", serializer='json')
def start_breathing():
    BlinkStickColors(transmit=True, network_interface='wlan0').breathing()

@task(name="start_snow_storm", serializer='json')
def start_snow_storm():
    BlinkStickColors(transmit=True, network_interface='wlan0').storm(snow=True)

@task(name="start_rain_storm", serializer='json')
def start_rain_storm():
    BlinkStickColors(transmit=True, network_interface='wlan0').storm(snow=False)

@task(name="start_fire_flies", serializer='json')
def start_fire_flies():
    BlinkStickColors(transmit=True, network_interface='wlan0').fire_flies()

@task(name="start_fire", serializer='json')
def start_fire():
    BlinkStickColors(transmit=True, network_interface='wlan0').fire()

@task(name="start_stripes", serializer='json')
def start_stripes():
    BlinkStickColors(transmit=True, network_interface='wlan0').stripes()

@task(name="start_clear_sky", serializer='json')
def start_clear_sky():
    BlinkStickColors(transmit=True, network_interface='wlan0').sky(sunny=True, cloudy=False)

@task(name="start_cloudy_sky", serializer='json')
def start_cloudy_sky():
    BlinkStickColors(transmit=True, network_interface='wlan0').sky(sunny=True, cloudy=True)

@task(name="start_stars", serializer='json')
def start_stars():
    BlinkStickColors(transmit=True, network_interface='wlan0').stars()

@task(name="start_custom_color_mode", serializer='json')
def start_custom_color_mode(mode, colors, duration, blink_duration, flow, lerp, brightness):
    BlinkStickColors(transmit=True, network_interface='wlan0').custom_color_mode(mode, colors, duration, blink_duration, flow, lerp, brightness)

@task(name="start_clear", serializer='json')
def start_clear():
    BlinkStickColors(transmit=True, network_interface='wlan0').clear()    