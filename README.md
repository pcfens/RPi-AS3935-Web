RPi-AS3935-Web
==============

A simple webpage designed to display information read from the
[AMS Franklin Lightning Sensor](http://www.ams.com/eng/Products/RF-Products/Lightning-Sensor/AS3935).

The website makes use of the [RaspberryPi-AS3935 library](https://github.com/pcfens/RaspberryPi-AS3935).

## Getting Started

### Connecting the AS3935

In my test setup I connected my breakout board to the Pi as shown

| AS3935 Pin | Raspberry Pi Pin |
| ---------: | :--------------- |
| 4 (GND)    | 25 (Ground)      |
| 5 (VDD)    | 1 (3v3 Power)    |
| 10 (IRQ)   | 11 (GPIO 17)     |
| 11 (I2CL)  | 5 (SCL)          |
| 13 (I2CD)  | 3 (SDA)          |


### Kernel Modules

To run this webserver you'll need to have the correct kernel modules loaded.  Adafruit has a nice
[tutorial](http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
set up, though depending on the breakout board that you use, you may 
not see anything show up when you run `i2cdetect`.

### Python libraries

To directly access the hardware, you'll need to install the `python-smbus` package available in
the repositories on Raspbian.

Other dependencies can be installed using `sudo pip install -r requirements.txt`. `sudo` is required
unless you use a virtualenv and write udev rules so that the I2C bus is accessible by an
unprivilged user.

### Configuring the Server

Copy the `settings.cfg.sample` file to `settings.cfg` and edit the appropriate
portions to match your setup. Each setting has comments to help.

## Running the Server

After everything is done, you can start the server by running `sudo python lightning_web.py`. If
everything starts without any errors, you can visit http://<raspberry pi>:<port>/ to interact
with the sensor (the default port is 5000).

An upstart/systemd job to start the server on boot will likely come later - we're just not there
yet (feel free to submit a PR).

### Scaling

Running the server this way does not scale well beyond a few connections. If you need to
support more users, I'd suggest looking in to gunicorn, and possibly nginx (keep in
mind that you need special settings to support WebSockets).

If you still have scaling issues (how many people care about lightning at your house anyway?),
then things need to be re-designed. At this point you should probably be pushing the data
to real server(s) that can re-distribute it as needed.


