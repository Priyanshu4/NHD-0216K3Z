from smbus import SMBus

class NHD_0216K3Z:
    ''' Class for controlling NHD-0216K3Z-FL-GBW-V3 LCD Display over I2C.
        Datasheet:
        https://www.hawkusa.com/sites/hawk-dev.ent.c-g.io/files/hawk_item/NWHVN/Series%20Serial%20Displays/NHD-0216K3Z-FL-GBW-V3/spec/NHD-0216K3Z-FL-GBW-V3.pdf
    '''
        
    special_chars = {
        # User Defined Custom Characters
        '\0': 0x00,
        '\1': 0x01,
        '\2': 0x02,
        '\3': 0x03,
        '\4': 0x04,
        '\5': 0x05,
        '\6': 0x06,
        '\7': 0x07,
        
        # Other Non-Ascii Special Characters
        # There are more special characters allowed by the device that are not included here
        # To use a character supported by the display which is not listed here, use write_char_from_code
        # Full list of character codes can be found in the datasheet
        '¥':  0x5C,
        '→':  0x7E,
        '←':  0x7F,
        '°':  0xDF,
        'α':  0xE0,
        'ä':  0xE1,
        'ñ':  0xEE,
        'ö':  0xEF,
        'β':  0xE2,
        'Ɛ':  0xE3,
        'μ':  0xE4,
        'σ':  0xE5,
        'ρ':  0xE6,
        '√':  0xE8,
        '¢':  0xEC,
        'θ':  0xF2,
        '∞':  0xF3,
        'Ω':  0xF4,
        'Σ':  0xF6,
        'π':  0xF7,
        '÷':  0xFD,
        '■':  0xFF
        }
        
    def __init__(self, i2c_bus, i2c_addr):
        ''' Initializes the NHD_0216K3Z object
            i2c_bus must be an SMBus object or an int representing the device I2C bus ID 
            i2c_addr is the address of the NHD_0216K3Z       
        '''
        if isinstance(i2c_bus, SMBus):
            self.i2c_bus = i2c_bus
        elif isinstance(i2c_bus, int):
            self.i2c_bus = SMBus(i2c_bus)
        else:
            raise TypeError('i2c_bus must be of type SMBus or int (device bus ID)')
        self.i2c_addr = i2c_addr
        
    def _send_cmd(self, cmd, *params):
        ''' Sends a command to the LCD.
            cmd is an int representing one byte.
            Additional parameters are one byte integer parameters of the command.
        '''
        self.i2c_bus.write_byte(self.i2c_addr, 0xFE)
        self.i2c_bus.write_byte(self.i2c_addr, cmd)
        for byte in params:
            self.i2c_bus.write_byte(self.i2c_addr, byte)

    def _get_char_code(self, char):
        ''' Given a character, this returns its corresponding byte code for the display.
        '''
        if char in self.special_chars:
            return self.special_chars[char]
        ascii_code = ord(char)
        if ascii_code >= 32 and ascii_code <= 125 and ascii_code != 92:
            return ascii_code
        else:
            raise ValueError(char + ' is an unsupported character')
     
    def write_char_from_code(self, code):
        ''' Writes a character to the display given its byte code.
            Byte codes of characters can be found in the datasheet.
        '''
        if code < 0 or code > 0xFF:
            raise ValueError('Code must be an int between 0 and 0xFF')
        self.i2c_bus.write_byte(self.i2c_addr, code)

    def write(self, msg):
        ''' Writes to the display wherever the cursor currently is.
            To use any of the 8 loaded custom characters in your msg, use '\0' through '\7'.
        '''
        for char in msg:
            char_code = self._get_char_code(char)
            self.i2c_bus.write_byte(self.i2c_addr, char_code)

    def write_line(self, msg, line, centered = False):
        ''' Writes a message on the given line (1 or 2).
            Also clears any existing characters on the line.
            If centered is True, the message is centered on the line.
            Returns whether or not the message fits on the line.
            To use any of the 8 loaded custom characters in your msg, use '\0' through '\7'.
        '''
        self.clear_line(line)
        length = len(msg)
        start_col = 1
        if centered:
            start_col = 1 + (16 - length) // 2
        self.set_cursor_pos(line, start_col)
        self.write(msg)
        return length <= 16
              
    def disp_msg(self, msg, preserve_words = False):
        ''' Clears the screen, resets cursor position, and writes a message.
            Automatically overflows to second line.
            If preserve_words is true, words are not split between lines.
            Returns whether or not the message fits on the screen.
            To use any of the 8 loaded custom characters in your msg, use '\0' through '\7'.
        '''
        self.clear_screen()
        self.home_cursor()
        msg_fits = True
        if preserve_words:
            i = 0
            words = msg.split()
            for word in words:
                if i != 16 and i != 0:
                    self.write(' ')
                if i + len(word) > 16:
                    self.set_cursor_pos(2, 1)
                self.write(word)
                i = i + len(word) + 1
            msg_fits = i <= 33
        else:
            for i in range(len(msg)):
                if i == 16:
                    self.set_cursor_pos(2, 1)
                char = msg[i]
                self.write(char)
            msg_fits = len(msg) <= 32
        return msg_fits
                           
    def display_on(self):
        self._send_cmd(0x41)
        
    def display_off(self):
        self._send_cmd(0x42)
        
    def set_cursor_pos(self, line, column):
        ''' Sets cursor position given line (1 or 2) and column (between 1 and 16)
        '''
        if column < 1 or column > 16 or line < 1 or line > 2:
            raise ValueError('Cursor can not be placed off screen. Column should be between 1 and 16. Line should be 1 or 2.')
        pos = (line - 1) * 0x40 + (column - 1)
        self._send_cmd(0x45, pos)
        
    def home_cursor(self):
        ''' Sets cursor to line 1 column 1.
        '''
        self._send_cmd(0x46)
        
    def underline_cursor(self, enabled):
        ''' Enables or disables the underline cursor.
        '''
        if enabled:
            self._send_cmd(0x47)
        else:
            self._send_cmd(0x48)
            
    def shift_cursor_left(self, spaces = 1):
        for i in range(spaces):
            self._send_cmd(0x49)
            
    def shift_cursor_right(self, spaces = 1):
        for i in range(spaces):
            self._send_cmd(0x4A)
            
    def blinking_cursor(self, enabled):
        ''' Enables or disables the blinking cursor.
        '''
        if enabled:
            self._send_cmd(0x4B)
        else:
            self._send_cmd(0x4C)
        
    def backspace(self):
        self._send_cmd(0x4E)
        
    def clear_line(self, line):
        ''' Clears a line (1 or 2) of the display.
            Sets the cursor position the the start of the line.
        '''
        self.set_cursor_pos(line, 1)
        self.write(" " * 16)
        self.set_cursor_pos(line, 1)

    def clear_screen(self):
        self._send_cmd(0x51)
        
    def set_contrast(self, contrast):
        ''' Sets the display contrast to a value between 1 and 50.
        '''
        if contrast < 1 or contrast > 50:
            raise ValueError('Contrast must be between 1 and 50.')
        else:
            self._send_cmd(0x52, contrast)
    
    def set_backlight_brightness(self, brightness):
        ''' Sets the backlight brightness to a value between 1 and 8.
        '''
        if brightness < 1 or brightness > 8:
            raise ValueError('Brightness must be between 1 and 8.')
        else:
            self._send_cmd(0x53, brightness)
            
    def load_custom_character(self, custom_char_slot, bitmap):
        ''' Loads a custom character's bitmap into the NHD_0216K3Z.
            The NHD_0216K3Z has 8 custom character slots (0 to 7).
            custom_char_slot should be an int from 0 to 7.
            Each custom character is a 5 by 8 bitmap.
            The bitmap should be a list of eight integers which are 5 bits each.
            See this example for the inverse question mark character ¿
             Binary     Hex
             0b00100    0x04
             0b00000    0x00
             0b00100    0x04
             0b01000    0x08
             0b10000    0x10
             0b10001    0x11
             0b01110    0x0E
             0b00000    0x00
            To use a custom character after it is loaded, use '\0' through '\7' in
            any write or display function.
        '''
        if custom_char_slot < 0 or custom_char_slot > 7:
            raise ValueError('Custom character slot must be between 0 and 7')
        if len(bitmap) != 8 or not all(i < 0x1F and i >= 0 for i in bitmap):
            raise ValueError('Bitmap must be list of 8 integers between 0x00 and 0x1F')
        self._send_cmd(0x54, custom_char_slot, *bitmap)
        
    def disp_custom_chars(self):
        ''' Displays all 8 currently loaded custom characters.
        '''
        self.write_line('\0\1\2\3\4\5\6\7', 1)
        self.write_line('01234567', 2)
        
    def shift_display_left(self, spaces = 1):
        for i in range(spaces):
            self._send_cmd(0x55)
        
    def shift_display_right(self, spaces = 1):
        for i in range(spaces):
            self._send_cmd(0x56)
    
    def change_rs232_baud_rate(self, baud_rate):
        ''' Changes the baud rate of the device for rs232 communication.
        '''
        self._send_cmd(0x61, baud_rate)
        
    def change_i2c_address(self, new_addr):
        ''' Changes the i2c address of the physical device.
            Then, this updates the address stored in this object as well.
        '''
        self._send_cmd(0x62, new_addr)
        self.i2c_addr = new_addr
  
    def disp_firmware_version(self):
        self._send_cmd(0x70)
        
    def disp_rs232_baud_rate(self):
        self._send_cmd(0x71)
        
    def disp_i2c_address(self):
        self._send_cmd(0x72)
    
        
    
        
        

        
