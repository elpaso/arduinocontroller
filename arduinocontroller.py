# -*- coding: utf-8 -*-
from osv import fields, osv

# Add 1 because crappy OE doesn't distinguish empty from 0
PINMODE_INPUT = 0+1          
PINMODE_OUTPUT = 1+1         
PINMODE_ANALOG = 2 +1        
PINMODE_PWM = 3+1            
PINMODE_SERVO = 4+1          

PIN_RANGE = {
    PINMODE_INPUT: (0, 1023),
    PINMODE_OUTPUT: (0, 1),
    PINMODE_ANALOG: (0, 1),
    PINMODE_PWM: (0, 255),
    PINMODE_SERVO: (0, 180),
}


DEBUG=True

if DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass


class arduinocontroller_board(osv.osv):
    """ Arduino board with configuration """

    # store device connections
    device_store = {}
    device_iterator_store = {}
    
    digital_pindir_values = [(PINMODE_INPUT, 'Input'), (PINMODE_OUTPUT, 'Output')]
    pwm_pindir_values = [(PINMODE_INPUT, 'Input'), (PINMODE_OUTPUT, 'Output'), (PINMODE_PWM, 'PWM Output'), (PINMODE_SERVO, 'Servo Output')]
    _name = "arduinocontroller.board"
    _description = "Arduino board"
    _rec_name = 'device'
    _columns = {
    
        'device': fields.char('Device', size=64, required=True),
        'model': fields.selection([('uno', 'Arduino uno')], 'Model', default='uno', required=True),
        'note' : fields.text('Notes'),
        'online': fields.boolean('Online'),

        # Digital
        
        'pind2dir': fields.selection(digital_pindir_values, 'Digital Pin 2 direction'),
        'pind3dir': fields.selection(pwm_pindir_values, 'Digital Pin 3 direction (PWM)'),
        'pind4dir': fields.selection(digital_pindir_values, 'Digital Pin 4 direction'),
        'pind5dir': fields.selection(pwm_pindir_values, 'Digital Pin 5 direction (PWM)'),
        'pind6dir': fields.selection(pwm_pindir_values, 'Digital Pin 6 direction (PWM)'),
        'pind7dir': fields.selection(digital_pindir_values, 'Digital Pin 7 direction'),
        'pind8dir': fields.selection(digital_pindir_values, 'Digital Pin 8 direction'),
        'pind9dir': fields.selection(pwm_pindir_values, 'Digital Pin 9 direction (PWM)'),
        'pind10dir': fields.selection(pwm_pindir_values, 'Digital Pin 10 direction (PWM)'),
        'pind11dir': fields.selection(pwm_pindir_values, 'Digital Pin 11 direction (PWM)'),
        'pind12dir': fields.selection(digital_pindir_values, 'Digital Pin 12 direction'),
        'pind13dir': fields.selection(digital_pindir_values, 'Digital Pin 13 direction'),
        
        
        'pind2value': fields.integer('Digital Pin 2 value'),
        'pind3value': fields.integer('Digital Pin 3 value'),
        'pind4value': fields.integer('Digital Pin 4 value'),
        'pind5value': fields.integer('Digital Pin 5 value'),
        'pind6value': fields.integer('Digital Pin 6 value'),
        'pind7value': fields.integer('Digital Pin 7 value'),
        'pind8value': fields.integer('Digital Pin 8 value'),
        'pind9value': fields.integer('Digital Pin 9 value'),
        'pind10value': fields.integer('Digital Pin 10 value'),
        'pind11value': fields.integer('Digital Pin 11 value'),
        'pind12value': fields.integer('Digital Pin 12 value'),
        'pind13value': fields.integer('Digital Pin 13 value'),

        # Analog
        
        'pina0active': fields.boolean('Analog Pin 0 active'),
        'pina1active': fields.boolean('Analog Pin 1 active'),
        'pina2active': fields.boolean('Analog Pin 2 active'),
        'pina3active': fields.boolean('Analog Pin 3 active'),
        'pina4active': fields.boolean('Analog Pin 4 active'),
        'pina5active': fields.boolean('Analog Pin 5 active'),
      
        'pina0value': fields.float('Analog Pin 0 value'),
        'pina1value': fields.float('Analog Pin 1 value'),
        'pina2value': fields.float('Analog Pin 2 value'),
        'pina3value': fields.float('Analog Pin 3 value'),
        'pina4value': fields.float('Analog Pin 4 value'),
        'pina5value': fields.float('Analog Pin 5 value'),
       
    }

    _defaults = {
        'device': '/dev/ttyACM0',
        'model': 'uno',
        }

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Set defaults
        """
        if context is None:
            context = {}

        dbg('Default get called')
        
        
        # Digital pins        
        for i in range(2, 14):
            context['default_pind%ddir' % i] = context.get('pind%ddir' % i, PINMODE_OUTPUT)
            context['default_pind%dvalue' % i] = context.get('pind%dvalue' % i, 0)

        # Analog pins        
        for i in range(0, 6):
            context['default_pina%dactive' % i] = context.get('pina%dactive' % i, False)

        v = super(arduinocontroller_board, self).default_get(cr, uid, fields_list, context)
        return v
            

    # Let's support multiple configurations for the same device!
    #_sql_constraints = [('unique_model_device', 'unique(model, device)', 'Model and device must be unique')]

    def in_range(self, pin, mode, value, fail_silently=True):
        """ Constraints the var in range """
        if mode == PINMODE_INPUT:
            return value
        bottom , top = PIN_RANGE[mode]
        res = bottom <= value <= top
        if not res and not fail_silently:
            raise osv.except_osv('Value is out of range', 'Please check that value for pin %s is in range %d-%d.' % (pin, bottom, top))
        if res:
            return value
        if value < bottom:
            return bottom
        return top
        

    def onchange_pin(self, cr, uid, ids, pin, mode, value):
        """ Check range """
        self.in_range(pin, int(mode), value, False)
        return {'value': {pin: value}}
        

    def onchange_online(self, cr, uid, ids, online, device):
        """ Connect to the device and report status """        
        v={}
        if ids and online:
            try:
                from pyfirmata import Arduino, util
            except ImportError:
                return {'warning' : {'title' : 'Attention!', 'message' : 'Pyfirmata is not installed, arduino operations are disabled. You can install pyfirmata from hg clone ssh://hg@bitbucket.org/tino/pyfirmata'}}
            board = self._get_board(device)
            if not board:
                 return {'warning' : {'title' : 'Attention!', 'message' : 'Cannot communicate with Arduino, please check your connections and settings on device %s.' % device}}            
            
        return {'value':v}
        

    def _setup_board(self, board, device, **kwargs):
        """
        Set the board up and read/write values from the board
        @return values
        """
        from pyfirmata import Arduino, util
        try:
            self.device_iterator_store[device]
        except:
            self.device_iterator_store[device] = util.Iterator(board)
            self.device_iterator_store[device].start()        
             
        v = {}
        # Digital pins        
        for i in range(2, 14):
            if 'pind%ddir' % i in kwargs and 'pind%dvalue' % i in kwargs:
                try:
                    pinmode = int(kwargs['pind%ddir' % i])
                    pinvalue = kwargs['pind%dvalue' % i]
                    pinvalue = self.in_range(i, pinmode, pinvalue)
                    board.digital[i].mode = pinmode-1  # less 1: crappy OE
                    dbg('DIGITAL %d Setting mode to : %d' % (i, pinmode))
                    v['pind%dvalue' % i] = pinvalue
                    if pinmode == PINMODE_INPUT:
                        v['pind%dvalue' % i] = board.digital[i].read()
                        dbg('DIGITAL %d reads %s' % (i, v['pind%dvalue' % i]))                 
                    elif pinmode == PINMODE_PWM:
                        dbg('DIGITAL PWM %d writes %s' % (i, pinvalue))
                        board.digital[i].write(pinvalue/255.0) # 0-1
                    elif pinmode == PINMODE_SERVO:
                        dbg('DIGITAL SERVO %d writes %s' % (i, pinvalue))
                        board.digital[i].write(pinvalue)
                    elif pinmode == PINMODE_OUTPUT:
                        dbg('DIGITAL OUTPUT %d writes %s' % (i, pinvalue))
                        board.digital[i].write(pinvalue)                       
                except:
                    raise
                
        # Analog pins
        # TODO: writing      
        for i in range(0, 6):
            if 'pina%dactive' % i in kwargs and kwargs['pina%dactive' % i]:
                board.analog[i].mode = PINMODE_INPUT-1 # less 1: crappy OE
                try:
                    #board.analog[i].enable_reporting()
                    v['pina%dvalue' % i] = board.analog[i].read()
                    dbg('ANALOG %d reads %s' % (i, v['pina%dvalue' % i]))    
                except:
                    # TODO: better error handling
                    raise
            else:
                # TODO: something or delete the branch
                pass
                
        return v
        

    def _get_board(self, device):
        """
        Returns device connection, creates one if necessary
        @returns boolean true if board is online
        """
        from pyfirmata import Arduino, util   
        try:
            return self.device_store[device]
        except KeyError:
            try:
                board = Arduino(device)
                self.device_store[device] = board
                return board
            except util.serial.SerialException:
                return False
        

    def write(self, cr, uid, ids, vals, context=None):
        """
        Update record(s) exist in {ids}, with new value provided in {vals}

        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param ids: list of record ids to update
        @param vals: dict of new values to be set
        @param context: context arguments, like lang, time zone

        @return: Returns True on success, False otherwise
        """

        from pyfirmata import util
        record = self.browse(cr, uid, ids[0], context=context)               
        try:
            if record.online:
                # Merge values into vals
                parms = dict([(k, getattr(vals, k, getattr(record, k, None))) for k in self._columns if k.startswith('pin')])
                board = self._get_board(record.device)
                if board:
                    parms.update(vals)
                    vals.update(self._setup_board(board, record.device, **parms))
        except util.serial.SerialException:
            raise osv.except_osv('Device is set online but cannot communicate with Arduino', 'Please check your connections and settings on device %s.' % record.device)
            
        res = super(arduinocontroller_board, self).write(cr, uid, ids, vals, context=context)
        return res

    def refresh_board(self, cr, uid, ids, context=None):
        """ Re-read values from the board """
        record = self.browse(cr, uid, ids[0], context=context)
        if not record.online:
            raise osv.except_osv('Device is offline','Device is offline, check the online flag.')
        board = self._get_board(record.device)
        if not board:
            raise osv.except_osv('Cannot communicate with Arduino', 'Please check your connections and settings on device %s.' % record.device)
        return True


        

arduinocontroller_board()

