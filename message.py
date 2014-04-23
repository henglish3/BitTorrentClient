import struct
import binascii

class WireMessage(object):
    PL = '!IB' # "Prefix Length" (req'd by protocol)
    MESSAGE_TYPES = {
        -1: 'keep_alive',
        0: ('choke', PL, 1),
        1: ('unchoke', PL, 1),
        2: ('interested', PL, 1),
        3: ('not interested', PL, 1),
        4: ('have', PL+'I', 5),
        5: ('bitfield', PL),
        6: ('request', PL+'III', 13),
        7: ('piece', PL+'II'),
        8: ('cancel', PL+'III', 13),
        9: ('port', PL+'BB', 3)
    }

    @classmethod
    def decode(cls, buf, pstr='BitTorrent protocol'):
        
        if len(buf) < 4:
            raise Exception('Not enough bytes to form a protocol message.')

        # Check for Keep Alive message
        try:
            keep_alive = struct.unpack("!I", buf[:4])[0]
            assert keep_alive == 0
            buf = buf[4:]
            return (cls.MESSAGE_TYPES[-1], None), buf
        except AssertionError:
            pass
		
        total_message_length, msg_id = struct.unpack("!IB", buf[:5])
        
        buf = buf[5:]

        fmt = '!' + cls.MESSAGE_TYPES[msg_id][1][3:]
        args_and_payload_length = total_message_length - 1 
        args_and_payload = buf[:args_and_payload_length]


        payload_length = args_and_payload_length 
        if msg_id == 7 or msg_id == 5: 
            if msg_id == 7:
                payload_length -= 8
            fmt += str(payload_length) + "s" 


        args = None
        args = (x for x in struct.unpack(fmt, args_and_payload))
        
        buf = buf[args_and_payload_length:] 
        	
        try:
            return (cls.MESSAGE_TYPES[msg_id][0], args), buf
        except IndexError:
            raise Exception('Index error'.format(msg_id))

    @classmethod
    def construct_msg(cls, msg_id, *args):
        fmt = cls.MESSAGE_TYPES[msg_id][1]
        length = None
        try:
            length = cls.MESSAGE_TYPES[msg_id][2]
        except IndexError, e:
            if msg_id == 5:
                # bitfield
                length = len(args[0])
                fmt += str(length) + 's'
            elif msg_id == 7:
                # piece
                length = len(args[2])
                fmt += str(length) + 's'
            else:
                raise Exception(
                        'No length for unexpected msg id {}'.format(msg_id)
                        )
            length += 1
        packed = None
        assert msg_id != 0
        try:
            if len(args) == 0:
                packed = struct.pack(fmt, length, msg_id)
            else:
                packed = struct.pack(fmt, length, msg_id, *args)
        except struct.error, e:
            raise Exception('At struct error, args was', args, \
                ', msg_id was', msg_id, \
                ', fmt was', fmt, \
                ' and length was', length)
        return packed
