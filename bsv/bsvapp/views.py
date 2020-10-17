from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.contrib import messages
from django.db import transaction
from django.conf import settings
# Forms
from .forms import MusicModesForm
from .forms import ColorModesForm
from .forms import ColorProgramsForm
# Modules
from .worker import * # Utilizes Celery workers to delegate multiprocessing tasks.


# Celery Task Management
celery_tasks = []
def stop_celery_tasks():    
    if len(celery_tasks) > 0: # Stop Celery tasks if any are running.
        for celery_task in celery_tasks:
            try:
                print('Terminating Celery Task: {}'.format(celery_task))
                celery_task.revoke(terminate=True)
                celery_tasks.remove(celery_task)
            except Exception as e:
                print(e)

# Views
def home(request):
    template = 'home.html'
    if request.method == 'GET':
        #return render(request, template, context)
        return render(request, template)

def music_modes(request):        
    template = 'music_modes.html'
    range_list = []
    for num in range(3, 501):
        range_list.append(num)    
    #print(range_list) # Debugging

    if request.method == 'GET':
        # Default Transition time thresholds.
        minimum = 3
        maximum = 15
        context = {'range_list': range_list, 'minimum': minimum, 'maximum': maximum}
        return render(request, template, context)

    elif request.method == 'POST':
        form = MusicModesForm(request.POST or None)
        if form.is_valid():                                
            stop_celery_tasks() # Stop any Celery Tasks that might be running.
            cd = form.cleaned_data                                                    
            all_modes = cd.get('all_modes')
            flash = cd.get('flash')
            pulse = cd.get('pulse')
            loop = cd.get('loop')
            minimum = cd.get('minimum')
            maximum = cd.get('maximum')
            print(all_modes, flash, pulse, loop, minimum, maximum) # Debugging
            
            # Handle visualization options and errors.
            if all_modes == False and flash == False and pulse == False and loop == False:                 
                messages.error(request, 'ERROR - All visualization options Off.', extra_tags='alert-danger')
                return redirect('music_modes')
            if flash == False and pulse == False and loop == True:
                pulse = True
                loop = True
            
            # Aggregate modes to call the Blinkstickviz class.
            modes = []            
            if all_modes:
                modes.append('all')
            else:
                if flash:
                    modes.append('flash')
                if pulse:
                    modes.append('pulse')
                if loop:
                    modes.append('loop')

            # Execute Celery Worker
            t = start_visualizer.apply_async(args=[minimum, maximum, modes])
            celery_tasks.append(t)
                        
            context = {'all_modes': all_modes, 'flash': flash, 'pulse': pulse, 'loop': loop, 'range_list': range_list, 'minimum': int(minimum), 'maximum': int(maximum)}
            return render(request, template, context)
        else:
            print('ERROR - Form invalid.')
            messages.error(request, 'Form Invalid.', extra_tags='alert-danger')
            return redirect('music_modes')  

def color_modes(request):    
    duration_range = []
    blink_duration_range = [10, 9.5 , 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.01]        
    brightness_range = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
    for num in range(1, 501):
        duration_range.append(num)    
    template = 'color_modes.html'
    if request.method == 'GET':
        blink_duration_default = 1
        duration_default = 1
        brightness_default = 1
        context = {'duration_range': duration_range, 'duration': duration_default, 'blink_duration_range': blink_duration_range, 'blink_duration': blink_duration_default, 'lerp': 'sine', 'brightness_range': brightness_range, 'brightness': brightness_default}
        return render(request, template, context)            

    elif request.method == 'POST':
        form = ColorModesForm(request.POST or None)
        if form.is_valid(): 
            stop_celery_tasks() # Stop any Celery Tasks that might be running.            
            cd = form.cleaned_data
            single_mode = cd.get('single_mode')
            blink_mode = cd.get('blink_mode')
            duration = cd.get('duration')     
            blink_duration = cd.get('blink_duration')                 
            morph_mode = cd.get('morph_mode')
            flow = cd.get('flow')                        
            sine = cd.get('sine')
            leap = cd.get('leap')
            rev = cd.get('rev')
            blink = cd.get('blink')
            brightness = cd.get('brightness')            
            
            # Debugging
            #print('my_duration: {}'.format(duration))
            #print('blink_duration: {}'.format(blink_duration))       
            #print(single_mode, blink_mode, blink_duration, morph_mode, flow)            
            #print(sine, leap, rev, blink, brightness)
                
            FF0063 = cd.get('FF0063')
            FF005E = cd.get('FF005E')
            FF0003 = cd.get('FF0003')
            FF0000 = cd.get('FF0000')
            FF5C00 = cd.get('FF5C00')
            FF6000 = cd.get('FF6000')
            FF7F00 = cd.get('FF7F00')
            FFBC00 = cd.get('FFBC00')
            FFC000 = cd.get('FFC000')
            FFFF00 = cd.get('FFFF00')
            E1FF00 = cd.get('E1FF00')
            _81FF00 = cd.get('_81FF00')
            _21FF00 = cd.get('_21FF00')
            _00FF00 = cd.get('_00FF00')    
            _00FF9E = cd.get('_00FF9E')
            _00FFFD = cd.get('_00FFFD')
            _00A0FF = cd.get('_00A0FF')
            _0040FF = cd.get('_0040FF')
            _0000FF = cd.get('_0000FF')
            _1F00FF = cd.get('_1F00FF')
            _7F00FF = cd.get('_7F00FF')
            _4B0082 = cd.get('_4B0082')
            _9400D3 = cd.get('_9400D3')
            DF00FF = cd.get('DF00FF')
            FF00C3 = cd.get('FF00C3')
            FF00BE = cd.get('FF00BE')
            CCCCCC = cd.get('CCCCCC')
            FFFFFF = cd.get('FFFFFF')            
#             print(FF0063, FF005E, FF0003, FF0000, FF5C00, 
#                   FF6000, FF7F00, FFBC00, FFC000, FFFF00, 
#                   E1FF00, _81FF00, _21FF00, _00FF00, _00FF9E, 
#                   _00FFFD, _00A0FF, _0040FF, _0000FF, _1F00FF, 
#                   _7F00FF, _4B0082, _9400D3, DF00FF, FF00C3, 
#                   FF00BE, CCCCCC, FFFFFF) # Debugging
            
            if single_mode:
                mode = 'single'
            if blink_mode:
                mode = 'blink'
            if morph_mode:
                mode = 'morph'
            if single_mode == True and blink_mode == True and morph_mode == True:
                messages.error(request, 'ERROR - Select Single Color, Blink, or Morph Mode.', extra_tags='alert-danger')
                return redirect('color_modes')                
            elif single_mode == True and blink_mode == True:
                messages.error(request, 'ERROR - Select Single Color, Blink, or Morph Mode.', extra_tags='alert-danger')
                return redirect('color_modes')                    
            elif single_mode == True and morph_mode == True:
                messages.error(request, 'ERROR - Select Single Color, Blink, or Morph Mode.', extra_tags='alert-danger')
                return redirect('color_modes')
            elif blink_mode == True and morph_mode == True:
                messages.error(request, 'ERROR - Select Single Color, Blink, or Morph Mode.', extra_tags='alert-danger')
                return redirect('color_modes')                                
            elif single_mode == False and blink_mode == False and morph_mode == False:
                messages.error(request, 'ERROR - Please Select a Mode.', extra_tags='alert-danger')
                return redirect('color_modes')
            
            if sine:
                lerp = 'sine'
            elif leap:
                lerp = 'leap'
            elif rev:
                lerp = 'rev'
            elif blink:
                lerp = 'blink'
            else:
                lerp = 'sine'

            # Aggregate colors to call the BlinkStickColors class.
            colors = []            
            if FF0063:
                colors.append('#FF0063')
            if FF005E:
                colors.append('#FF005E')
            if FF0003:
                colors.append('#FF0003')
            if FF0000:
                colors.append('#FF0000')
            if FF5C00:
                colors.append('#FF5C00')
            if FF6000:
                colors.append('#FF6000')
            if FF7F00:
                colors.append('#FF7F00')
            if FFBC00:
                colors.append('#FFBC00')
            if FFC000:
                colors.append('#FFC000')
            if FFFF00:
                colors.append('#FFFF00')
            if E1FF00:
                colors.append('#E1FF00')
            if _81FF00:
                colors.append('#81FF00')
            if _21FF00:
                colors.append('#21FF00')
            if _00FF00:
                colors.append('#00FF00') 
            if _00FF9E:
                colors.append('#00FF9E')
            if _00FFFD:
                colors.append('#00FFFD')
            if _00A0FF:
                colors.append('#00A0FF')
            if _0040FF:
                colors.append('#0040FF')
            if _0000FF:
                colors.append('#0000FF')
            if _1F00FF:
                colors.append('#1F00FF')
            if _7F00FF:
                colors.append('#7F00FF')
            if _4B0082:
                colors.append('#4B0082') 
            if _9400D3:
                colors.append('#9400D3')
            if DF00FF:
                colors.append('#DF00FF')
            if FF00C3:
                colors.append('#FF00C3')
            if FF00BE:
                colors.append('#FF00BE')
            if CCCCCC:
                colors.append('#CCCCCC')
            if FFFFFF:
                colors.append('#FFFFFF')

            # Execute Celery Worker          
            t = start_custom_color_mode.apply_async(args=[mode, colors, duration, blink_duration, flow, lerp, brightness])
            celery_tasks.append(t)
                                    
            context = {'single_mode': single_mode, 'blink_mode': blink_mode, 'duration_range': duration_range, 'duration': int(duration), 'blink_duration_range': blink_duration_range, 'blink_duration': float(blink_duration), 'morph_mode': morph_mode, 'flow': flow, 'lerp': lerp, 'brightness_range': brightness_range, 'brightness': float(brightness)}
            return render(request, template, context)                
                
def color_programs(request):
    template = 'color_programs.html'
    if request.method == 'GET':
        #return render(request, template, context)
        return render(request, template)
    
    elif request.method == 'POST':
        form = ColorProgramsForm(request.POST or None)
        if form.is_valid():
            stop_celery_tasks() # Stop any Celery Tasks that might be running.
            cd = form.cleaned_data                                                                                                
            rotating_rainbow = cd.get('rotating_rainbow')
            rainbow_snake = cd.get('rainbow_snake')
            breathing = cd.get('breathing')
            snow_storm = cd.get('snow_storm')
            rain_storm = cd.get('rain_storm')
            fire_flies = cd.get('fire_flies')
            fire = cd.get('fire')
            stripes = cd.get('stripes')
            clear_sky = cd.get('clear_sky')
            cloudy_sky = cd.get('cloudy_sky')
            stars = cd.get('stars')
            if rotating_rainbow:
                t = start_rotating_rainbow.apply_async()
                celery_tasks.append(t)                
            if rainbow_snake:
                t = start_rainbow_snake.apply_async()
                celery_tasks.append(t)                
            if breathing:
                t = start_breathing.apply_async()
                celery_tasks.append(t)                
            if snow_storm:
                t = start_snow_storm.apply_async()
                celery_tasks.append(t)                
            if rain_storm:
                t = start_rain_storm.apply_async()
                celery_tasks.append(t)                
            if fire_flies:
                t = start_fire_flies.apply_async()
                celery_tasks.append(t)                
            if fire:
                t = start_fire.apply_async()
                celery_tasks.append(t)                
            if stripes:
                t = start_stripes.apply_async()
                celery_tasks.append(t)                
            if clear_sky:
                t = start_clear_sky.apply_async()
                celery_tasks.append(t)                
            if cloudy_sky:
                t = start_cloudy_sky.apply_async()
                celery_tasks.append(t)                
            if stars:
                t = start_stars.apply_async()
                celery_tasks.append(t)
            return render(request, template)            

def off(request):
    if request.method == 'GET':
        stop_celery_tasks()
        t = start_clear.delay()    
        celery_tasks.append(t)    
        return redirect('home')   

def celery_stop(request):
    stop_celery_tasks()    
    return HttpResponse("Stopping Celery Tasks")

def celery_start(request):
    stop_celery_tasks()
    add.delay(7, 8)
    return HttpResponse("Sent Test Celery Task to Worker")
