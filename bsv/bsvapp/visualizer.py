import pyaudio as pa
import numpy as np
from blinkstick import blinkstick
from bsvapp import notes_scaled_nosaturation
from time import sleep, time
from colorsys import hsv_to_rgb
import argparse, sys, random, pickle
from os import path
from threading import Thread
from socket import *
import argparse, sys, random, pickle
import netifaces as ni


class BlinkStickViz:
    def __init__(self, sensitivity, rate, chunk, channels, max_int, min_int, transmit, receive, network_interface, inputonly, led_count, device=None):
        # Declare variables, not war.        

        # Network modes for remote Blinkstick communication. By default, both transmit and receive modes set to False.
        self.network_interface = network_interface
        self.auto_discovery_port = 50000
        self.net_identifier = "blinkstickviz" # Identifier to insure we only talk to compatible devices. 
        self.inputonly = inputonly # Facilitates bypassing Blinkstick device, and handling input only device. Default to False.            
        self.transmit = transmit
        self.receive = receive
        self.acknowledged = False # By default we haven't been acknowledged, as a discovered device.        
        if inputonly == True:
            self.transmit = True        
        self.receive_address = '0.0.0.0' # Hard-coded bind to 0.0.0.0 interface. This may need to be adjusted?
        self.receive_port = 12000 # Hard-coded UDP receive/listener port. Adjust this if needed. Didn't bother to make it configurable.
        self.receive_nodes_file = './receive_nodes.list' # Hard-coded filename of receive nodes (IP Addresses) if in transmit mode. List each IP Address on it's own line.  
        if self.transmit == True:            
            self.receive_nodes = [] # Empty list of receive nodes updated by self.get_receive_nodes(). Either updated by hard-coded list or auto-discovery (self.udp_discovery())
            self.get_receive_nodes()        
        
        # PyAudio Variables.
        self.device = device
        self.paud = pa.PyAudio()
        self.format = pa.paInt16
        self.channels = channels # This may need to be lowered depending on the device used.
        self.rate = rate # This may need to be tuned to 48000Hz
        self.chunk = chunk # This may need to be tuned to 512, 2048, or 4096.

        # Visualization Variables.
        self.loop = None # Pulse from both ends of the strip. Default None, self.main() sets this.
        self.sensitivity = sensitivity # Sensitivity to sound.
        self.sample_rate = 1024 # Haven't seen this tuned. But perhaps?
        self.wait_interval_max = int(max_int) # Max time in seconds visualization will run before switching.
        self.wait_interval_min = int(min_int) # Minimum time in seconds visualization will run before switching.
        self.stop = False  # Tells visualization to stop running. Facilitates switching to another visualization. Default to False.

        # Init Blinkstick, Audio input, and Analyze/Read Audio. Create leds object, so we can loop over in the visualization methods.
        self.led_count = led_count # LED count defaults to 32. Will be determined by self.get_blinksticks() if otherwise. Tune when using Input Only mode.  
        if self.inputonly == False: # Facilitates bypassing Blinkstick device, and handling input only device.    
            self.sticks = self.get_blinksticks() # Discover Blinkstick Device.
        elif inputonly== True:
            print('Input Only Mode. Bypassing Blinkstick Discovery (i.e. this device is just a microphone).')
        if self.receive == False: # If not in UDP receive mode, go ahead an Init the audio device and read the stream. 
            self.audio_stream = self.input_device() # Init microphone as input source/stream.
            self.audio = self.read_audio(self.audio_stream, num_samples=self.sample_rate) # Read the audio stream.
        if self.transmit == True: # Tell us if we're in transmit mode after audio init. Looks better.
            print('UDP Transmit Mode to {}, on Port: {}'.format(self.receive_nodes, self.receive_port))
            if len(self.receive_nodes) == 0:
                print('Auto Discovery - Awaiting Announcement from network attached Blinkstick devices.')
        
    # Utilize multiple Blinksticks on the same parent device. Note: This won't run well on Raspberry Pi. Beefer CPU required.
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
        return(found_blinksticks)

    def input_device(self): # i.e. Microphone
        if self.device is not None: # Use non-default device.
            audio_stream = self.paud.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                frames_per_buffer=self.chunk,
                input= True,
                input_device_index=self.device,
                )
        else: # Otherwise, use the default.
            audio_stream = self.paud.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                frames_per_buffer=self.chunk,
                input= True,
                )
        return(audio_stream)

    # Convert the audio data to numbers, num_samples at a time.
    def read_audio(self, audio_stream, num_samples):
        while True:
            # Read all the input data.
            samples = audio_stream.read(num_samples, exception_on_overflow=False)
            # Convert input data to numbers
            samples = np.frombuffer(samples, dtype=np.int16).astype(np.float)
            samples_l = samples[::2]
            samples_r = samples[1::2]
            yield samples_l, samples_r

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
          
    def udp_announce(self):                
        try:        
            announce_socket = socket(AF_INET, SOCK_DGRAM) # Create UDP socket.
            announce_socket.bind(('', 0))
            announce_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # Broadcast socket.
        except Exception as e:
            print('ERROR - Unable to bind to address - {}'.format(e))
        try:
            my_ip = ni.ifaddresses(self.network_interface)[ni.AF_INET][0]['addr']
        except Exception as e:
            print('ERROR - Problem with Network Interface. Perhaps you did not define the proper NIC? (Default: eth0)')        
        
        # Time between announcements based on whether we've been acknowledged.
        short_announce_interval = 1
        long_announce_interval = 10

        while 1:
            if self.acknowledged == True: # If we've been acknowledged, stop announcing.
                print('Auto Discovery - Discovered! Announcing to network every {}s...'.format(long_announce_interval))
                sleep(long_announce_interval)
            elif self.acknowledged == False:
                print('Auto Discovery - Announcing to network every {}s...'.format(short_announce_interval))
                sleep(short_announce_interval)
            # Perform Announcement.
            data = '{} {}'.format(self.net_identifier, my_ip)
            data = pickle.dumps(data) # Serialize the data for transmission.
            announce_socket.sendto(data, ('<broadcast>', self.auto_discovery_port))          

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

    def udp_receive_handler(self):
        Thread(target=self.udp_receive).start() # UDP Receive Mode data on separate thread.
        Thread(target=self.udp_announce).start() # UDP Broadcast announce we're on the network and ready to receive data via separate thread.        

    def udp_receive(self):               
        print('UDP Receive Mode. Listening on: {}, Port: {}'.format(self.receive_address, self.receive_port))
        try:    
            receive_socket = socket(AF_INET, SOCK_DGRAM) # Create UDP socket.
            receive_socket.setsockopt(SOL_SOCKET, SO_RCVBUF, self.chunk) # Set receive buffer size to self.chunk. Prevents visual lag.
            receive_socket.bind((self.receive_address, self.receive_port))
        except Exception as e:
            print('ERROR - Unable to bind to address - {}'.format(e))
             
        while 1:
            data = receive_socket.recv(self.chunk)
            decoded_data = pickle.loads(data) # De-Serialize the received data.
            if 'acknowledged' in decoded_data:  
                self.acknowledged = True
            else:
                self.send_to_stick(decoded_data) # Send the data to our Blinksticks.
  
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
                          
    def main(self, modes):
        # Start with more complex conditional for the mode and move to simpler.
        if 'all' in modes:
            print('All - Pulse, Flash, and Loop (randomly).')
            self.random_visualization_handler(loop='random')
        elif 'pulse' in modes and 'flash' in modes and 'loop' in modes:
            print('Pulse with Loop (static) and Flash.')
            self.random_visualization_handler(loop=True)
        elif 'pulse' in modes and 'flash' in modes:
            print('Pulse and Flash')
            self.random_visualization_handler(loop=False)
        elif 'pulse' in modes and 'loop' in modes:
            print('Pulse with Loop.')
            self.loop = True
            self.pulse_visualization()
        elif 'flash' in modes and 'loop' in modes: # Note: flash visualization doesn't use loop. So even if it's specified, it won't matter.
            print('Flash only. Loop has no affect.')
            self.flash_visualization()
        elif 'pulse' in modes:
            print('Pulse only.')
            self.pulse_visualization()
        elif 'flash' in modes:
            print('Flash only.')
            self.flash_visualization()

    def random_visualization_handler(self, loop):
        visualizations = [self.pulse_visualization, self.flash_visualization] # If you create more visualization functions, add them to this list.
        wait_interval = random.randint(self.wait_interval_min, self.wait_interval_max)
        while True:
            self.stop = False # Always start the loop with stop Default to False
            # Loop Handler
            if loop == True:
                self.loop = True
            elif loop == False:
                self.loop = False
            elif loop == 'random':
                self.loop = random.choice([True, False])
            visualization_picked = random.choice(visualizations)
            print('Waiting: {}s, Loop: {}, Visualization: {}'.format(wait_interval, self.loop, visualization_picked))
            t = Thread(target=visualization_picked) # Threading facilitates addressing multiple Blinksticks on the same parent device. 
            t.start()
            sleep(wait_interval)
            self.stop = True
            t.do_run = False
            t.join()
            wait_interval = random.randint(self.wait_interval_min, self.wait_interval_max)

    def led_data(self):        
        return(notes_scaled_nosaturation.process(self.audio, num_leds=self.led_count, num_samples=self.sample_rate, sample_rate=self.rate, sensitivity=self.sensitivity)) # Return the processed audio stream to the visualizer functions.

    def pulse_visualization(self):
        leds = self.led_data()
        
        if self.loop:
            data = [0]*int(self.led_count/2)*3
            data2 = [0]*int(self.led_count/2)*3
        else:
            data = [0]*self.led_count*3

        sent = 0
        for frame in leds:
            brightest = 0
            for i, led in enumerate(frame):
                if led > frame[brightest]:
                    brightest = i

            hue = brightest/48.0
            color = hsv_to_rgb(hue, 1, min(frame[brightest]*1.2, 1))

            del data[-1]
            del data[-1]
            del data[-1] # I feel dirty having written this.
            if self.loop:
                del data2[0]
                del data2[0]
                del data2[0]

            color = [int(color[1]*255), int(color[0]*255), int(color[2]*255)]
            data = color + data

            if self.loop: # finaldata exists because if I try to do the seemingly sane thing it breaks.
                data2 = data2 + color
                finaldata = data+data2
            else:
                finaldata = data

            now = time()
            if now-sent < .02:
                sleep(max(0, .02-(now-sent)))

            sent = time()
            self.send_to_stick(finaldata)
            if self.stop == True: # Handle stopping the thread, so another visualization can be executed.
                break

    def flash_visualization(self):
        leds = self.led_data()
        
        last_frame = [0]*self.led_count # For smooth transitions, we need to know what things looked like last frame.
        sent = 0
        for frame in leds:
            data = []
            size = []

            brightness = 0
            brightest = 0
            totalsize = 0

            for i in range(self.led_count): # First pass, let's get an idea of how loud things are.
                brightness = brightness + frame[i]
                if frame[i] > frame[brightest]:
                    brightest = i

            for i in range(self.led_count): # Second pass, let's try and figure out the rough size of each section.
                if brightness == 0:
                    frame[i] = 1
                    size.append(1)
                    totalsize = totalsize + 1
                    continue
                try:
                    size.append(int(frame[i]/brightness*self.led_count))
                    totalsize = totalsize+size[-1]
                except ValueError:
                    pass

            if brightness == 0:
                brightness = self.led_count

            while totalsize < self.led_count:
                for i in range(self.led_count):
                    if totalsize < self.led_count and size[i] > 0:
                        size[i] = size[i] + 1
                        totalsize = totalsize + 1
                    elif totalsize == self.led_count:
                        break

            for i in range(self.led_count):
                hue = i/(self.led_count*1.75)
                r, g, b = hsv_to_rgb(hue, 1, min((last_frame[i]*2.6+frame[i]*1.3)/3, 1))
                data = data+[int(g*255), int(r*255), int(b*255)]*int(size[i])

            now = time()
            if now-sent < .02:
                sleep(max(0, .02-(now-sent)))

            sent = time()
            self.send_to_stick(data)
            last_frame = frame
            if self.stop == True: # Handle stopping the thread, so another visualization can be executed.
                break
