from blinkstick import blinkstick
from time import sleep, time
from colorsys import hsv_to_rgb
from math import sin, cos, pi
from colour import Color
import sys, pickle, collections, random, math
from socket import *
from os import path
from threading import Thread
import netifaces as ni
from webcolors import hex_to_rgb

class BlinkStickColors:
    def __init__(self, transmit, network_interface):        
        self.data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Start data is OFF. This will get continuously updated with last color displayed in morph flow.
        self.led_count = 32 # LED count defaults to 32. Will be determined by self.get_blinksticks() if otherwise. Tune when using Input Only mode.  
        self.sticks = self.get_blinksticks() # Discover Blinkstick Device.
        self.network_interface = network_interface
        self.auto_discovery_port = 50000
        self.net_identifier = "blinkstickviz" # Identifier to insure we only talk to compatible devices. 
        self.inputonly = False
        self.transmit = transmit
        self.receive_address = '0.0.0.0' # Hard-coded bind to 0.0.0.0 interface. This may need to be adjusted?
        self.receive_port = 12000 # Hard-coded UDP receive/listener port. Adjust this if needed. Didn't bother to make it configurable.
        self.receive_nodes_file = './receive_nodes.list' # Hard-coded filename of receive nodes (IP Addresses) if in transmit mode. List each IP Address on it's own line.  
        if self.transmit == True:            
            self.receive_nodes = [] # Empty list of receive nodes updated by self.get_receive_nodes(). Either updated by hard-coded list or auto-discovery (self.udp_discovery())
            self.get_receive_nodes()

    def get_receive_nodes(self):
        if path.isfile(self.receive_nodes_file):
            with open(self.receive_nodes_file, 'r+') as f:
                ip_addresses = f.readlines()
                for ip_address in ip_addresses:
                    if '.' in ip_address: # Chuck any line that doesn't have a dot in it (i.e. an IP address format 10.9.9.X). 
                        ip_address = ip_address.rstrip('\n')
                        self.receive_nodes.append(ip_address) # Append IP to list of receive nodes. Remove newline.
                        self.udp_acknowledge(ip_address)                
                    else:
                        continue # Skip lines without dots.              
        #else: # If no hard coded IP list is specified, use auto discovery mechanism.
        #print('No Hard-coded IP list provided, Starting Auto Discovery...')
        Thread(target=self.udp_discovery).start() # Threaded Start UDP Discovery.             

    def udp_discovery(self):
        discovery_socket = socket(AF_INET, SOCK_DGRAM) # Create UDP socket.
        discovery_socket.bind(('', self.auto_discovery_port))
        while 1:
            data, addr = discovery_socket.recvfrom(1024) # Wait for a packet
            decoded_data = pickle.loads(data) # De-Serialize the received data.
            if decoded_data.startswith(self.net_identifier):
                receive_node_ip = decoded_data.rsplit(' ', 1)[1]
                if receive_node_ip not in self.receive_nodes: # Update the self.receive_nodes with newly discovered nodes.
                    print('Auto Discovery - Found: {}, on Port: {}'.format(receive_node_ip, self.receive_port))
                    self.receive_nodes.append(receive_node_ip) # Add node to our list of discovered/known receiving nodes. 
                    self.cache_discovered_nodes() # Write the discovered nodes out to a cache for faster discovery.
                self.udp_acknowledge(receive_node_ip)

    def cache_discovered_nodes(self):
        print('Wrote Receive Node IP Addresses to Cache.')
        with open(self.receive_nodes_file, 'w+') as f:
            for ip_address in self.receive_nodes:
                f.write('{}\n'.format(ip_address))
        f.close()  
        
    def udp_acknowledge(self, receive_node_ip): # Tell the receiving node, that we have discovered them, and thus stop broadcasting.                        
            data = pickle.dumps('acknowledged') # Serialize the data for transmission.
            acknowledge_socket = socket(AF_INET, SOCK_DGRAM)
            acknowledge_socket.sendto(data,(receive_node_ip, self.receive_port))
            
    def udp_transmit(self, data):
        data = pickle.dumps(data) # Serialize the data for transmission.
        for receive_node in self.receive_nodes: # Loop over the list of hosts.
            try:
                transmit_socket = socket(AF_INET, SOCK_DGRAM)
                transmit_socket.sendto(data,(receive_node, self.receive_port))
            except Exception as e:
                print('ERROR - Unable to communicate to Receive Node: {} - {}'.format(receive_node, e))
                sys.exit(1)
                
    def send_to_stick(self, data):
        if self.transmit == True: # If we're in transmit mode send the led data via UDP.
            self.udp_transmit(data)        
        if self.inputonly == False: # If input only is False, we'll send data to multiple connected Blinkstick Devices.
            for stick in self.sticks: # Loop over one of more Blinkstick devices sending visualization processed LED data.
                try:
                    stick.set_led_data(0, data)
                except Exception as e:
                    print('ERROR - Blinkstick communication error - {}'.format(e))
                    self.get_blinksticks() # Try to re-init Blinkstick communication when failures occur. This is due to bugs in pyusb library.
    
    def get_blinksticks(self):
        found_blinksticks = []
        led_counts = []
        blinksticks = blinkstick.find_all() # Discover multiple Blinksticks.        
        for stick in blinksticks:
            count = stick.get_led_count()
            led_counts.append(count)       
            found_blinksticks.append(stick)
        
        # Verify we're addressing the same number of LEDs for both sticks.
        led_count = set(led_counts) # Set will deduplicate.
        if len(led_count) == 1: # Should be left with one, if everything is equal.
            for count in led_count:
                self.led_count = int(count)
        else:
            print('ERROR - LED Count is NOT equal between Blinksticks: {} - Values should match.'.format(led_count))
            sys.exit(1)
        return(found_blinksticks)        
    
    def rotating_rainbow(self):
        speed = 1 # 2 is 2x speed, .5 is half speed, you get the idea.
        fps = 50.0 # Frames per second of the animation. 50 is about the upper limit.
        cut = 2 # how much of the spectrum to show. 1 = full spectrum, 2 = 2 full spectrums, .5 is half a spectrum.
        brightness = 1.0 # Brightness of animation from 0 to 1        

        while True:
            data = []
            for i in range(1,self.led_count+1):
                (r, g, b) = hsv_to_rgb(i/float(self.led_count*(1.0/cut))+time()*speed, 1, brightness)
                data = data + [int(g*255), int(r*255), int(b*255)]
                #print(data) # Debugging
            self.send_to_stick(data)
            sleep(1/fps)

    def rainbow_snake(self):        
        fps = 50.0 # FPS of the animation. 50 is about the upper limit.
        speed = 2 # Speed of animation
        type = 1.0 # "1" for hard edges on colors, "1.0" for smooth fading.
        brightness = 1.0 # Brightness of animation, from 0 to 1
                        
        while True:
            data = []
            for i in range(1,self.led_count+1):
                (r, g, b) = hsv_to_rgb((sin(time()/(8.0/speed)+i/(4*type))+1)/2, 1, brightness)
                data= data + [int(g*255), int(r*255), int(b*255)]
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(1/fps) 

    def breathing(self):     
        fps = 50.0 # How many frames per second. 50 is about the upper limit.
        colorin = Color('#b71500')
        colorout = Color('black')                
        
        while True:
            last = colorout
            while last.hex != colorin.hex: # For some reason if I use anything but .hex, they'll never equal the same color.
                last = Color(rgb=((last.red*5+colorin.red)/6, (last.green*5+colorin.green)/6, (last.blue*5+colorin.blue)/6))
                data = [int(last.green*255), int(last.red*255), int(last.blue*255)] * self.led_count                    
                self.send_to_stick(data)
                sleep(1/fps)                
                #print('breathe in', last)
            #print('pause', last)
            sleep(1/fps*7)
            while last.hex != colorout.hex and last.luminance > .004: # For fading to black, this helps a bit since the blinkstick completely blanks out at low brightness levels.
                last = Color(rgb=((last.red*6+colorout.red)/7, (last.green*6+colorout.green)/7, (last.blue*6+colorout.blue)/7))
                data = [int(last.green*255), int(last.red*255), int(last.blue*255)] * self.led_count
                self.send_to_stick(data)
                sleep(1/fps)
                #print('breathe out', last)        
                        
    def storm(self, snow):        
        loop = True # Whether or not the blinkstick loops around on itself. If True, flakes/drops will fall from both ends to the center of the strip.
        rotate = -4 # How much to rotate the animation. On devices like the Flex this lets you put the "top" anywhere along the strip, instead of both ends. They'll fall towards the opposite side of the strip.
        snow = snow # Whether it's snowing or raining
        lightning = False # Currently not implemented.
        lightning_freq = 120
        fps = 50.0 # How many frames per second. 50 is about the upper limit. Any faster and you'll overwhelm the blinkstick.
                
        if snow: # Snow settings
            r = 220
            g = 240
            b = 255
            speed = 1 # Speed of animation
            freq = 25 # How often spawning cycles are in frames.
            odds = 3 # How likely (1/X) a flake will spawn during a cycle.
            low_speed = 1.2 # Lower speed limit
            high_speed = 2.0 # Upper speed limit
        else: # Rain settings
            r = 40
            g = 110
            b = 180
            speed = 10
            freq = 6
            odds = 2
            low_speed = 2.1
            high_speed = 2.2        
                
        flakes = []
        
        class Flake:
            def __init__(self, headstart = False):
                self.position = random.randint(0, 1) # Left or right
                self.speed = random.uniform(low_speed, high_speed) # How fast it falls
                if headstart:
                    self.born = time()-random.uniform(.3, 6.0)
                else:
                    self.born = time() # When it was created.
        
        flakes = flakes + [Flake(True), Flake(True), Flake(True), Flake(True), Flake(True)] # Start off with a few flakes with a headstart.
        counter = 0
        last_strike = 0
        
        while True:
            if loop:
                dat1 = [0]*int(self.led_count/2)*3
                dat2 = [0]*int(self.led_count/2)*3
            else:
                dat1 = [0]*self.led_count*3
            
            for i, flake in enumerate(flakes):
                
                position = (time()-flake.born)*flake.speed*speed
                if (position > self.led_count/2 and loop) or position > self.led_count:
                    del flakes[i]
                    continue
                
                f_pos = position-math.floor(position)
                led1_val = 1-f_pos
                led2_val = f_pos
                led = math.floor(position)
                
                try:
                    if flake.position == 0 or not loop:
                        dat1[led*3] = min(int(g*led1_val)+dat1[led*3], 255)
                        dat1[led*3+1] = min(int(r*led1_val)+dat1[led*3+1], 255) # I wonder if I could use slices to condense this.
                        dat1[led*3+2] = min(int(b*led1_val)+dat1[led*3+2], 255)
                        
                        dat1[led*3+3] = min(int(g*led2_val)+dat1[led*3+3], 255)
                        dat1[led*3+4] = min(int(r*led2_val)+dat1[led*3+4], 255)
                        dat1[led*3+5] = min(int(b*led2_val)+dat1[led*3+5], 255)
                    else:
                        led = int(self.led_count/2)-led
                        dat2[led*3+3] = min(int(g*led1_val)+dat2[led*3+3], 255)
                        dat2[led*3+4] = min(int(r*led1_val)+dat2[led*3+4], 255)
                        dat2[led*3+5] = min(int(b*led1_val)+dat2[led*3+5], 255)
                        
                        dat2[led*3] = min(int(g*led2_val)+dat2[led*3], 255)
                        dat2[led*3+1] = min(int(r*led2_val)+dat2[led*3+1], 255)
                        dat2[led*3+2] = min(int(b*led2_val)+dat2[led*3+2], 255)
                except IndexError:
                    pass
            
            if loop:
                data = collections.deque(dat1 + dat2)
                data.rotate(rotate*3)
            else:
                data = dat1
            
            self.send_to_stick(data)
            sleep(1/fps) # Nap for a bit so we don't overwhelm the blinkstick.
            
            counter = counter + 1
            
            if counter % freq == 0 and random.randint(1,odds) == 1:
                flakes = flakes + [Flake()]
                
            if lightning and (counter % lightning_freq == 0 and random.randint(0, 2)) or (time()-last_strike < 1 and time()-last_strike > .12 and random.randint(0, 50)):
                last_strike = time()
        
        
    def fire_flies(self):
        speed = 1 # Overall speed of the animation.
        ff_speed = 5 # Speed of the fireflies.
        fps = 50.0 # FPS of the animation. 50 is about the upper limit.        
                
        while True:
            data = []
            for i in range(self.led_count):
                x = time()*speed # Base speed control
                y = x+i # For a bit of random color for the flies.
                z = x*ff_speed+i**2  # Firefly speed control
                ff_glow = max((sin(z)+sin(z/3.0)+sin(z/7.0))/5-.4,0) # Flicker. Honestly with this math I just threw stuff at the wall on desmos.com to see what stuck.
                r, g, b = hsv_to_rgb(.10+(sin(y)/32+.03125), 1.0-ff_glow*1.3, ff_glow*5) # Convert to RGB.
                #print(hueplus, r, g, b)
                data = data + [int(g*255), int(r*255), int(b*255)] # Convert to GRB and add to the frame.
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(1/fps) # Nap for a bit so we don't overwhelm the blinkstick.

    def fire(self):
        speed = 2 # Overall speed of the animation
        popspeed = 4 # Speed of the flickers/pops
                
        while True:
            data = []
            for i in range(self.led_count):
                x = time()*speed # Base speed control
                y = x+i # For some variation from LED to LED
                z = x*popspeed+i**2 # For the sporadic flickering
                hue = ((sin(y/.4)+sin(y/.2)+sin(y/.5))/6+.5)*.06 # Main color
                hueplus = max((sin(z)+sin(z/3.0)+sin(z/7.0))/5-.4,0) # Flicker
                r, g, b = hsv_to_rgb(min(hue+hueplus, .07), 1.0-hueplus, sin(z)/8+.875) # Convert to RGB
                #print(hueplus, r, g, b)
                data = data + [int(g*255), int(r*255), int(b*255)] # Convert to GRB and add to the frame.
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(0.02) # Nap for a bit so we don't overwhelm the blinkstick.

    def stripes(self):
        color1 = (0.05, 1, .98) # These are in hsv format
        color2 = (0.08, .95, 1) 
        speed = 10 # Speed of the animation
        width = 15 # Width of the stripes. Lower = wider. 
        fps = 50.0 # FPS of the animation. 50 is about the upper limit.                
        
        while True:
            data = []
            for i in range(self.led_count):
                fac = (math.sin((time())*speed+i*width)/2+.5)
                hue = color1[0]+(color2[0]-color1[0])*fac
                sat = color1[1]+(color2[1]-color1[1])*fac
                val = color1[2]+(color2[2]-color1[2])*fac
                r, g, b = hsv_to_rgb(hue, sat, val)
                data = data + [int(g*255), int(r*255), int(b*255)] # Convert to GRB and add to the frame.
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(1/fps) # Nap for a bit so we don't overwhelm the blinkstick.

    def sky(self, sunny, cloudy):    
        fps = 50.0 # FPS of the animation. 50 is about the upper limit.
        loop = False # Whether or not to put a sun on both ends of the attached LEDs.
        sunny = sunny # If true, draw and display the sun.
        cloudy = cloudy # If true, cut saturation to make it look overcast.
        
        sun1 = [0.11, .9, 1] # These are in hsv format
        sun2 = [0.14, .98, 1] # Color of the sun
        sky1 = [0.6, .7, .7] # Color of the sky 
        sky2 = [0.45, .8, .65] # It'll shift between the two colors.
        
        size1 = 3 # Size of the sun in LEDs
        size2 = 6 # The size changes and creates a glowing, pulsing effect.
        sun_speed = 5 # Speed of the sun animation
        sky_speed = 1 # Speed of the sky animation
                        
        if cloudy: # If it's cloudy, cut the saturation.
            sun1[1] = (sun1[1]+.1)/2
            sun2[1] = (sun2[1]+.1)/2
            sky1[1] = (sky1[1]+.3)/3
            sky2[1] = (sky2[1]+.3)/3
        
        while True:
            data = []
            for i in range(self.led_count):
                sky_color = (math.sin((time())*sky_speed+i)/2+.5)
                sun_color = (math.sin((time())*sun_speed+i*sun_speed*1.5)/2+.5)
                
                size = size1+(size2-size1)*sun_color
                
                if loop:
                    sun_factor = min(max(size-i, 0) + max(size-(self.led_count-i), 0), 1)
                else:
                    sun_factor = min(max(size-i, 0), 1)
                
                sky_hue = sky1[0]+(sky2[0]-sky1[0])*sky_color
                sky_sat = sky1[1]+(sky2[1]-sky1[1])*sky_color
                sky_val = sky1[2]+(sky2[2]-sky1[2])*sky_color
                
                
                hue = sky_hue
                sat = sky_sat
                val = sky_val
                
                r, g, b = hsv_to_rgb(hue, sat, val)
                
                if sun_factor > 0 and sunny:
                    sun_hue = sun1[0]+(sun2[0]-sun1[0])*sun_color
                    sun_sat = sun1[1]+(sun2[1]-sun1[1])*sun_color
                    sun_val = sun1[2]+(sun2[2]-sun1[2])*sun_color
                    
                    sr, sg, sb = hsv_to_rgb(sun_hue, sun_sat, sun_val)
                    
                    r = r+(sr-r)*sun_factor
                    g = g+(sg-g)*sun_factor
                    b = b+(sb-b)*sun_factor
                    
                data = data + [int(g*255), int(r*255), int(b*255)] # Convert to GRB and add to the frame.
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(1/fps) # Nap for a bit so we don't overwhelm the blinkstick.        
        
    def stars(self):  
        fps = 50 # How many frames per second. 50 is about the upper limit. Any faster and you'll overwhelm the blinkstick.
        speed = 50 # Speed of animation
        freq = 200 # How often shooting stars spawn
        odds = 4 # How likely (1/X) a shooting star will spawn during a cycle.
        trail = 3 # How long a shooting's star trail is. Currently not implelemented.
        loop = True # Whether or not this blinkstick is arranged with its LEDs in a loop, like a Flex taped end to end. Or not taped end to end. For this script if you have more than a few LEDs it's pretty well recommended to have this on.
        rotate = -3 # How much to rotate the animation. On devices like the Flex this lets you put the "top" anywhere along the strip. Shooting stars will fall towards the opposite point on the strip. By default the fall from both ends of the strip towards the middle.                
        
        class ShootingStar:
            def __init__(self):
                if loop:
                    self.position = random.randint(0, 1) # Left or right side
                else:
                    self.position = 0
                self.speed = speed # How fast it falls
                headstart = max(random.uniform(-.3,0.3), 0)
                self.born = time()-headstart
                self.lifespan = random.uniform(headstart+.2, headstart+.6)
        
        def generate_stars(): # Generate a night sky full of stars
            sky = []
            last = -999
            for i in range(self.led_count):
                if random.randint(0,3) == 0 and i-last > 1:
                    r, g, b = hsv_to_rgb(0.09, random.uniform(.1, .25), random.uniform(.3, .55))
                    if random.randint(0,1) == 0:
                        sky = sky+[int(g*255),int(r*255),int(b*255)] # reddish star
                    else:
                        sky = sky+[int(g*255),int(b*255),int(r*255)] # bluish star
                    last = i
                else:
                    sky = sky+[0,0,0]
            return sky
        
        stars = []
        
        idata = generate_stars() # This is basically an initial picture of the sky.
        
        counter = 0
        
        while True:
            if loop:
                dat1 = idata[:int(self.led_count/2)*3]
                dat2 = idata[int(self.led_count/2)*3:]
            else:
                dat1 = idata[:] # This slice grabs the whole thing. If we don't use slices, the two just link to the same list and we can't have that.
            
            if len(stars) > 0:
                for i, star in enumerate(stars):
                    position = (time()-star.born)*star.speed
                    if (position > self.led_count/2 and loop) or (position > self.led_count and not loop) or time()-star.born > star.lifespan:
                        del stars[i]
                
                    f_pos = position-math.floor(position)
                    led1_val = 1-f_pos
                    led2_val = f_pos
                    led = math.floor(position)
                    
                    try:
                        if star.position == 0:
                            dat1[led*3] = max(int(100*led1_val), dat1[led*3])
                            dat1[led*3+1] = max(int(105*led1_val), dat1[led*3+1]) # I wonder if I could use slices to condense this.
                            dat1[led*3+2] = max(int(95*led1_val), dat1[led*3+2])
                            
                            dat1[led*3+3] = max(int(100*led2_val), dat1[led*3+3]) # This one's green
                            dat1[led*3+4] = max(int(105*led2_val), dat1[led*3+4]) # Red
                            dat1[led*3+5] = max(int(95*led2_val), dat1[led*3+5])  # and blue. Same pattern for the rest of them.
                            pass
                        else:
                            led = int(self.led_count/2)-led
                            dat2[led*3+3] = max(int(100*led1_val), dat2[led*3+3])
                            dat2[led*3+4] = max(int(105*led1_val), dat2[led*3+4])
                            dat2[led*3+5] = max(int(95*led1_val), dat2[led*3+5])
                            
                            if (position < self.led_count/2): # Since I have no idea what I'm doing, we have to make sure this doesn't wrap around ahead of our shooting star.
                                dat2[led*3] = min(int(100*led2_val), dat2[led*3])
                                dat2[led*3+1] = min(int(105*led2_val), dat2[led*3+1])
                                dat2[led*3+2] = min(int(95*led2_val), dat2[led*3+2])
                    except IndexError:
                        pass
            
            if loop:
                data = collections.deque(dat1 + dat2)
                data.rotate(rotate*3)
            else:
                data = dat1
                
            
            self.send_to_stick(data) # Send off to the blinkstick
            sleep(0.02) # Nap for a bit so we don't overwhelm the blinkstick.
            
            counter = counter + 1
            
            if counter % freq == 0 and random.randint(1,odds) == 1:
                stars = stars + [ShootingStar()]
                print('star added')

    def send_color(self, r, g, b): 
        self.send_to_stick([int(g), int(r), int(b)] * self.led_count)

    def push_color(self, r, g, b, brightness):
        data = [int(g*brightness), int(r*brightness), int(b*brightness)] + list(self.data[:-3])
        self.send_to_stick(data)
        self.data = data # Update data var with last color.

    def clear(self):
        count = 0
        while count <= 100:            
            self.send_color(0, 0, 0)
            sleep(0.5)
            count += 1
                
    def custom_color_mode(self, mode, colors, duration, blink_duration, flow, lerp, brightness):
        # Cast decimals and integers. 
        duration = int(duration)
        blink_duration = float(blink_duration)
        brightness = float(brightness)
        if blink_duration == 0:
            strobe = False
        elif blink_duration > 0:
            strobe = True
            blink_duration = blink_duration
        loop = True
        if mode == 'blink':
            while True:
                for color in colors:
                    (r, g, b) = hex_to_rgb(color)
                    self.send_color(r, g, b)
                    if strobe:
                        sleep(max(.02, blink_duration))
                        self.send_color(0, 0, 0)
                    sleep(max(.02, duration))
                if not loop:
                    break
        if mode == 'morph':
            curcolor = (0, 0, 0) # Start OFF. 
            while True:
                for color in colors:
                    targetcolor = hex_to_rgb(color)
                    start = time()
                    while time()-start < duration:
                        progress = (time()-start)/duration
                        if lerp == 'sine':
                            progress = 1-(cos(pi*progress)+1)/2
                        elif lerp == 'leap':
                            progress = -1*(progress-1)**2+1
                        elif lerp == 'rev':
                            progress = progress**2
                        elif lerp == 'blink':
                            progress = 0
                        (g, r, b) = [a*(1-progress)+b*progress for a, b in zip(curcolor, targetcolor)]
                        if flow:
                            self.push_color(g, r, b, brightness)
                        else:
                            self.send_color(g, r, b)
                        sleep(.02)
                    curcolor = targetcolor
                if not loop:
                    break            
        elif mode == 'single':
            while True:
                (r, g, b) = hex_to_rgb(colors[0]) # Takes the first color if multiple colors are selected.                            
                self.send_color(r, g, b)
                sleep(5) # Keep transmitting data at 5 second intervals incase more blinksticks come online or connections are lost.
        elif mode == 'clear':
            self.clear()
            
