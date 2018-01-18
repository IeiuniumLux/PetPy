# PetPy
PetPy is a simple local HTTP server that let you feed your pet remotely. It's built on [MicroPython](http://micropython.org), the lean implementation of the Python 3 standard library that is optimised to run on microcontrollers and in constrained environments. PetPy is simple and hackable enough that can be adapted for other projects or used for testing and learning. It can easly act as a simple interface to receive remote requests to control devices or read analog inputs like the kind used for IOT projects.

## How it works
A food container is attached to a servo and when it turns, a few pellets/kibble/treats drop into the bowl. You can adjust the hole and size of the dispenser depending on whether you are feeding a fish, cat, dog, etc. It serves only one single user connection.

## Authentication
PetPy requires a login first unless the user is detected in the session; which in that case just sends the index.html page. A Cookie is used to store the user session. However, the HttpOnly flag is set so it's not accessible through JavaScript and immune to XSS.

## Behind wifi router
If you want to run PetPy server behind WiFi-router and want it to be accessible from the Internet, then you have to add [port-forwarding](https://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/) rule on your router. This is required in order to forward all of the requests that come to the router within the local network to PetPy server.

## Parts

Below is the list of essential parts you'll need to build the pet feeder.

Part             | Qty 
---------------- | ----
[OpenMV Cam M7](http://openmv.io/products/openmv-cam-m7)<br /> | 1 
[OpenMV Cam WiFi Shield](http://openmv.io/products/wifi-shield "OpenMV Cam WiFi Shield")<br /> | 1 
[OpenMV IR Lens](https://openmv.io/collections/lenses/products/ir-lens "IR Lens")<br /> | 1 
[Clear Acrylic Cement for Bonding Parts](https://www.amazon.com/Glarks-280-Pieces-Phillips-Stainless-Assortment/dp/B01G0KRGXC "Clear Acrylic Cement")<br /> | 1 
[Hitec HS-82MG Metal Gear Micro Servo](https://www.amazon.com/gp/product/B0012YXRJE/ref=ox_sc_act_title_1?smid=A20WEVHROQQX12&psc=1 "HS-82MG Servo")<br /> | 1 
[Barrel Jack to 2-Pin JST Adapter](https://www.frys.com/product/7726848 "Adapter")<br /> | 1 
[3-Inch Diameter Round Tin](https://www.amazon.com/gp/product/B01NCWUE6Y/ref=ox_sc_act_title_1?smid=AZA0I12YMQNES&psc=1 "Round Tin")<br /> *a mini Pringles can should work too* | 1 
[Knurled Thumb Nuts](https://www.ebay.com/itm/321361726270 "Knurled Thumb Nuts")<br /> *optional*| 2 
[4" x 4" Acrylic/Plexiglass Block](https://www.ebay.com/itm/292072330728 "Base")<br /> | 1 
[CAD Parts](stl/ "STL files")<br />*camera mount by Chris Anderson and feeder structure by littleBits* <br />![Parts](/img/3D-parts.png) |

## Resources
[Minifier](http://minifycode.com/html-minifier/ "Minifier")<br />
[CSS Validator](http://jigsaw.w3.org/css-validator/#validate_by_input "Validator")<br />
[Date/Epoch Converter](http://www.esqsoft.com/javascript_examples/date-to-epoch.htm "Converter")<br />
[Router Port Forwarding](https://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/)<br />
[Google Domains](https://domains.google/#/)<br />
[Content Security Policy](https://developers.google.com/web/fundamentals/security/csp/#if_you_absolutely_must_use_it)<br />
[FreeCAD](https://www.freecadweb.org/)<br />
