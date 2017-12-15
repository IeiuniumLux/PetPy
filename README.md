# PetPy
PetPy is a simple local HTTP server that lets you feed your pet remotely. The server receives a HTTP signal through the browser to activte the feeder. A food container (with a small hole in its side) is attached to a servo and when it turns, a few pellets/kibble/treats drop into the bowl. You can adjust the hole and size of the container accordingly depending on whether you are feeding a cat, dog, or fish.

## Technology
PetPy is built on [MicroPython](http://micropython.org), the lean implementation of the Python 3 standard library that is optimised to run on microcontrollers and in constrained environments. The JPEG image is updated on the client using AJAX short polling and the CSS style sheet used to customize the single HTML page, it's served using the [GitHub Pages](https://pages.github.com/).

## Parts

Below is the list of essential parts you'll need to build the pet feeder.

Part             | Qty 
---------------- | ----
[OpenMV Cam M7](http://openmv.io/products/openmv-cam-m7)<br /> | 1 
[OpenMV Cam WiFi Shield](http://openmv.io/products/wifi-shield "OpenMV Cam WiFi Shield")<br /> | 1 
[OpenMV Cam Wide Angle Lens](http://openmv.io/products/ultra-wide-angle-lens "OpenMV Cam Wide Angle Lens")<br /> | 1 
[Clear Acrylic Cement for Bonding Parts](https://www.amazon.com/Glarks-280-Pieces-Phillips-Stainless-Assortment/dp/B01G0KRGXC "Clear Acrylic Cement")<br /> | 1 
[Hitec HS-82MG Metal Gear Micro Servo](https://www.amazon.com/gp/product/B0012YXRJE/ref=ox_sc_act_title_1?smid=A20WEVHROQQX12&psc=1 "HS-82MG Servo")<br /> | 1 
[3-Inch Diameter Round Tin](https://www.amazon.com/gp/product/B01NCWUE6Y/ref=ox_sc_act_title_1?smid=AZA0I12YMQNES&psc=1 "Round Tin")<br /> *A mini Pringles can should work too* | 1 
[Barrel Jack to 2-Pin JST Adapter](https://www.frys.com/product/7726848 "Adapter")<br /> | 1 
[4" x 4" Acrylic/Plexiglass Block](https://www.ebay.com/itm/292072330728 "Base")<br /> | 1 
[CAD Parts](stl/ "STL files")<br />*OpenMV mount by Chris Anderson and Feeder by littleBits* |

![Parts](/img/3D-parts.png)

## Resources
[HTML Minifier](https://kangax.github.io/html-minifier/ "Minifier")<br />
[CSS & Javascript Minifier](http://cnvyr.io/online "css/javascript minifier")<br />
[CSS Validator](http://jigsaw.w3.org/css-validator/#validate_by_input "Validator")<br />
[Date/Epoch Converter](http://www.esqsoft.com/javascript_examples/date-to-epoch.htm "Converter")<br />
[Epoch & Unix Timestamp Conversion Tools](https://www.epochconverter.com/ "Converter 2")<br />

## Final Thoughts
It's nice to see that a pyboard like the OpenMV, can easly act as a simple control interface so a web page can send remote requests to control devices; or read analog inputs like the kind used for IOT projects. However, it is not intended to serve hundreds of connections or users since there's not much memory in the micropython boards and not a lot of processing power either. For this project in particular, PetPy is really meant to just serve one user connection, but it's simple and hackable enough to be used for testing, local development, and learning. Finally, notice that I have little to no HTML, CSS, and Javascript experience so the code can definitely be improved.
