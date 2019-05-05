# ElegooRemote
Resources for using the Elegoo IR remote on a Raspberry Pi

## LIRC Installation and Setup
This section is mostly based on [this GitHub Gist](https://gist.github.com/prasanthj/c15a5298eb682bde34961c322c95378b). If you are having difficulties, then I strongly encourage reading the comments there. There are some good insights to various issues.

LIRC seems to be unpredictable, hopefully this guide will work for you. I have tried to highlight some of the gotchas and issues that I ran into along the way.

In this guide, I am setting up LIRC on a Raspberry Pi Zero. This should be similar for other flavours of Raspberry Pi, but your mileage may vary.

### Install LIRC
Install LIRC using `apt-get`.

    sudo apt-get update
    sudo apt-get install lirc

Prepare the `/etc/modules` file.

    sudo nano /etc/modules

In this file, specify the LIRC modules and the relevant GPIO pin for the remote. In this case, the data pin of the IR receiver is connected to GPIO18 on the Raspberry Pi.

Add the following lines to `/etc/modules`:

    lirc_dev
    lirc_rpi gpio_in_pin=18

Specify the hardware configuration in the `/etc/lirc/hardware.conf` file.

    sudo nano /etc/lirc/hardware.conf

Add the following lines to the `/etc/lirc/hardware.conf` file:

    LIRCD_ARGS="--uinput --listen"
    LOAD_MODULES=true
    DRIVER="default"
    DEVICE="/dev/lirc0"
    MODULES="lirc_rpi"

> Note that the driver is `default` and that the device is `/dev/lirc0`. This can be useful for debugging.

Specify the boot configuration in `/boot/config.txt`. 

    sudo nano /boot/config.txt

Uncomment or update the specification of `dtoverlay` in `/boot/config.txt` so that it is:

    dtoverlay=lirc-rpi,gpio_in_pin=18

Specify the default device and driver in the LIRC options in the `/etc/lirc/lirc_options.conf` file.

    sudo nano /etc/lirc/lirc_options.conf

Update the specifications for `driver` and `device`. These should match the hardware configuration earlier.

    driver = default
	device = /dev/lirc0

Check that service stops and starts. Note that the commands are `lircd`, not `lirc`! Any issues here should hopefully highlight that something above has not been set up correctly.

    sudo /etc/init.d/lircd stop
    sudo /etc/init.d/lircd start

> For different flavours of the Raspberry Pi OS, you might find that the way of starting and stopping services is different.



If all is well, then reboot the Raspberry Pi.

    sudo reboot
	
## Set up remote using LIRC

To check that the driver is working, stop the `lircd` service and try some button presses using `mode2`.

    sudo /etc/init.d/lird stop
    mode2 --device=/dev/lirc0

Press a few buttons on the IR remote, you should see output like the following:

    pulse 560
    space 1706
    pulse 535

> If you get errors mentioning "partial reads" or similar, then try explicitly specifying the default driver using the `--driver` flag
> 
>     mode2 --device=/dev/lirc0 --driver=default

If explicitly specifying the driver helps, then the `/etc/lirc/lirc_options.conf` might be incorrectly configured. Refer to the previous section.

To record the commands for your remote, use the `irrecord` command.

> Before starting, it helps if you turn off any unnecessary lights in the room that you are in. I found that in my well lit living room I could not record commands correctly.

    sudo /etc/init.d/lircd stop
    sudo irrecord --device=/dev/lirc0 ~/lircd.conf

> If you need to specify the default driver for some reason, you can use the same flags as the `mode2` command.
> 
>     sudo irrecord --device=/dev/lirc0 --driver=default ~/lircd.conf

Carefully follow the instructions provided by the software.

When it comes to recording the codes for each key, you must use names from the namespace. You can find an exhaustive list [here](https://gist.github.com/unforgiven512/0c232f4112b63021a8e0df6eedfb2ff3).

When you have finished recording you should have a `.conf` file in your home directory. For example, if you specified the remote name `elegoo`, then the filename is `elegoo.lirc.conf`. View the configuration file in a text editor.

    sudo nano ~/elegoo.lirc.conf

If you notice that the codes are in two parts, where one is identical for each button, then manually remove the column of duplicates. For example, if you see like this in your `.conf` file:

    begin codes
        KEY_POWER                0x219E48B7 0x7E825B6C
        KEY_HOME                 0x219E609F 0x7E825B6C
        KEY_UP                   0x219EA05F 0x7E825B6C
        ...

then change it to this:

    begin codes
        KEY_POWER                0x219E48B7
        KEY_HOME                 0x219E609F
        KEY_UP                   0x219EA05F
        ...
        
Copy the configuration file to the `/etc/lirc/` directory and start the `lircd` service.

    sudo cp ~/elegoo.lircd.conf /etc/lirc/lircd.conf
    sudo /etc/init.d/lircd start

Test that the Raspberry Pi can receive the IR code using the `irw` command.

	irw

Press a few buttons on the remote that you configured earlier. You should see output like the following:

    0000000000ff02fd 00 KEY_PLAY elegoo
    0000000000ff02fd 01 KEY_PLAY elegoo
    0000000000ff02fd 02 KEY_PLAY elegoo
    0000000000ffe21d 00 KEY_STOP elegoo
    0000000000ffe21d 01 KEY_STOP elegoo
    0000000000ffe21d 02 KEY_STOP elegoo

## Python Interface
To use the IR remote in Python, use the [Python bindings for LIRC](https://pypi.org/project/python-lirc/) (`python3-lirc`) library.

Install `python3-lirc` using `apt-get`.

    sudo apt-get install python3-lirc

### Prepare LIRCRC configuration
To use `python3-lirc`, you must first set up a valid `.lircrc` configuration file. Create a file `.lircrc` in the home directory.

    sudo nano ~/.lircrc

Specify the configurations for each button you want to use between `begin` and `end` tags. Specify the particular button using the `button` variable, the program that will handle the button press using the `program` variable, and any data to send to the program using the `config` variable.

The example below specifies two buttons (`KEY_VOLUMEUP` and `KEY_VOLUMEDOWN`) for the program `myprogram` and sends the data `"up"` and `"down"`, respectively.

    begin
    button = KEY_VOLUMEUP
    prog = myprogram
    config = up
    end

    begin
    button = KEY_VOLUMEDOWN
    prog = myprogram
    config = down
    end

### Use IR receiver in Python
To use these commands in Python, import the `lirc` library using `import lirc`. To load the configuration, use the `init()` function and specify the program name. To get the response from the remote, use the `nextcode()` function.

This Python example imports the `lirc` library, loads the configuration for `myprogram`, reads the next button press on the remote, and prints returned text.

    import lirc
    sockid = lirc.init("myprogram")
    r = lirc.nextcode()
    print(r)
