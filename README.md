### 2020/10 BuRnCycL

**Blinkstick Audio LED Visualizer and Color Controls**

Original Code References (Will Yager & Different55 <burritosaur@protonmail.com>):
 - https://gitgud.io/diff-blinkstick/blinkpulse-visualizer/
 - https://gitgud.io/diff-blinkstick/blinkflash
 - http://yager.io/LEDStrip/LED.html
 - https://github.com/wyager/LEDStrip

### About

This app works in conjunction with https://github.com/burncycl/blinkstick-audio-led-visualizer

It gives a Web Interface to Control LED Visualizations.

### Ansible Automated Installation (use this for Production mode install)

Want to provision a fleet of Raspberry Pi's with Django Blinkstick App transmitting via network? DevOps to the rescue.

* Reference: https://github.com/burncycl/ansible-blinkstick-audio-led-visualizer

```
make bsvapp
```

NOTE: If you don't want to use Ansible, and want to run in Production mode, you'll need  to pilfer the blinkstickviz.service startup script from the Ansible repo.

Reference: https://github.com/burncycl/ansible-blinkstick-audio-led-visualizer/blob/master/roles/django-blinkstickviz/files/blinkstickviz.service

Install in `/etc/systemd/system/blinkstickviz.service` daemon-reload, enable.

### Semi-Automated Installation

#### Prerequisites
```
sudo ./install.sh 
```

#### Enable Virtual Environment + Development Mode
```
source ./init.sh
``` 
Will start pulseaudio

#### Start Django in Development mode.

Starts Celery worker(s) and Django in Development mode
```
./boot_workers.sh
./start.sh
```

### Starting from scratch

#### Bootstrapping Django for the first time.

Inside a blank repository
```
django-admin.py startproject bsv
cd ./bsv
python3 manage.py startapp bsvapp
```

### Important Setting
By default, the django application is in INPUT only mode. Updates downloaded via the internet will overwrite this setting.  

This setting increases stability.

Reference: https://github.com/burncycl/django-blinkstick-audio-led-visualizer/blob/master/bsv/bsv/settings.py#L138

```
# Input only (True = microphone only, False = Utilizes attached blinksticks). Warning: INPUT_ONLY = False could affect stability on Raspberry Pi devices.
INPUT_ONLY = True
```


### TODO
There is redundant networking code in the color_programs and visualizer. I need to break this out into its' own class, and then refactor the aforementioned modules.  
