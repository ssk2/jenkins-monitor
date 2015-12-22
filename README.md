# jenkins-monitor

A Jenkins monitor for the Mesosphere office. This application assumes your Jenkins server is reachable and that you are running a 32x32 display.

Inspired by [sloth](https://github.com/teabot/sloth).

## Assembly

The following components are used in the monitor:
+ [Raspberry Pi 2](https://www.adafruit.com/products/2358)
+ [Adafruit RGB LED HAT](https://www.adafruit.com/product/2345)
+ [32x32 RGB LED Matrix Panel - 6mm pitch](https://www.adafruit.com/products/1484) (you can use a smaller pitch if you like)
+ 5V, 2A DC power adapter for the HAT, 5V, 2A micro-usb adapter for the RPi
+ Wireless adapter (if you don't want to use Ethernet)

The [Adafruit tutorial](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/overview) is comprehensive.

![monitor](/img/wallmount.jpg)

## Setup

1. Clone this repo:
    ```
    git clone git@github.com:ssk2/jenkins-monitor.git
    ```
2. Initialise [the submodule](https://github.com/adafruit/rpi-rgb-led-matrix):
    ```
    git submodule init
    ```
3. Update the module:
    ```
    git submodule update
    ```
4. Make the Adafruit shared object file:
    ```
    cd adafruit && make clean rgbmatrix.so && cd ../
    ```
5. Create an `__init__.py` file so we can import the newly created file:
    ```
    touch adafruit/__init__.py
    ```
6. Run the script:
    ```
    sudo python jenkins-monitor.py
    ```

### Resizing Images

Images must be 32x32 in size. You can use `imagemagick` to resize them from the command line:
```sh
sudo apt-get install imagemagick
mogrify -resize 32x32 image.jpg
```