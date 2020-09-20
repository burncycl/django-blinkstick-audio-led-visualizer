from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.contrib import messages
from django.db import transaction
# Forms
from .forms import MusicModeForm
# Modules
from .visualizer import BlinkStickViz
# External Dependencies
from threading import Thread
import multiprocessing
from time import sleep

processes = [] # Holds list of Processes, so that we can terminate them if the visualization program is changed.

def start_visualizer(minimum, maximum, modes):
    BlinkStickViz(sensitivity=1.3, rate=44100, chunk=1024, channels=2, max_int=maximum, min_int=minimum, transmit=True, 
            receive=False, network_interface='wlan0', inputonly=False, led_count=32, device=None).main(modes=modes)    

def home(request):
    template = 'home.html'
    if request.method == 'GET':
        #return render(request, template, context)
        return render(request, template)

def music_mode(request):        
    template = 'music_mode.html'
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
        form = MusicModeForm(request.POST or None)
        if form.is_valid():
            cd = form.cleaned_data            
            
            # Stop running process, if exists. 
            if processes:
                for process in processes:
                    print('Stopping Process: {}.'.format(process.name))
                    try:            
                        process.terminate()
                        process.join()                        
                    except Exception as e:
                        print(e)
                                                    
            flash = cd.get('flash')
            pulse = cd.get('pulse')
            loop = cd.get('loop')
            minimum = cd.get('minimum')
            maximum = cd.get('maximum')
            print(flash, pulse, loop, minimum, maximum) # Debugging
            
            # Handle visualization options and errors.
            if flash == False and pulse == False and loop == False:                 
                messages.error(request, 'All visualization options Off. Please select at least one.', extra_tags='alert-danger')
                return redirect('music_mode')
            if flash == False and pulse == False and loop == True:
                pulse = True
                loop = True
            
            # Aggregate modes to call the Blinkstickviz class.
            modes = []            
            if flash:
                modes.append('flash')
            if pulse:
                modes.append('pulse')
            if loop:
                modes.append('loop')

            # Execute the visualizer on a process, that way we can kill it when new instructions are posted.
            p = multiprocessing.Process(name='visualizer', target=start_visualizer, args=[minimum, maximum, modes])
            processes.append(p)
            p.start()
            
            context = {'flash': flash, 'pulse': pulse, 'loop': loop, 'range_list': range_list, 'minimum': int(minimum), 'maximum': int(maximum)}
            return render(request, template, context)
        else:
            print('ERROR - Form not valid.')
            messages.error(request, 'Form Invalid.', extra_tags='alert-danger')
            return redirect('music_mode')  

    
def color_mode(request):
    template = 'color_mode.html'
    if request.method == 'GET':
        #return render(request, template, context)
        return render(request, template)