Arduino OpenERP controller module
=================================

Author: Alessandro Pasotti

Copyright: 2012 - ItOpen

http://www.itopen.it

See also:
http://www.itopen.it/2012/05/24/controlling-arduino-from-openerp/

Introduction
============

This is a simple module for OpenERP which allows to control an Arduino UNO board 
directly connected to the USB port.

Digital I/O, analog I, PWM and servo controls are supported.

This module uses PyFirmata and the firmata firmware http://www.firmata.org.


Dependencies
============

pyfirmata: https://bitbucket.org/tino/pyfirmata/src

Firmata Standard firmware must be loaded on the board.

License
=======

AGPL v.2


To-Do
=====

Support more board models (Arduino Mega is easy to add, 
but I don't have one to test).

Add interrupt-like actions on pin changes to trigger 
OpenERP asctions or views.

Add analog output capabilities.
