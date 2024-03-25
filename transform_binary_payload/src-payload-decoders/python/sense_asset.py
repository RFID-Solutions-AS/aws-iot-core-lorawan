import base64

def dict_from_payload(base64_input: str, fport: int = None):
    """ Decodes a base64-encoded binary payload into JSON.
            Parameters
            ----------
            base64_input : str
                Base64-encoded binary payload
            fport: int
                FPort as provided in the metadata. Please note the fport is optional and can have value "None", if not provided by the LNS or invoking function. 

                If  fport is None and binary decoder can not proceed because of that, it should should raise an exception.

            Returns
            -------
            JSON object with key/value pairs of decoded attributes

        """

    decoded = base64.b64decode(base64_input)


    match fport:
        case None:
            return
        
        case 2:
            #    Data frame
            #   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
            #   |------|--------|--------|------|------|------|------|------|------|
            #   |   0  |                      Hardware Version                     |
            #   |------|-----------------------------------------------------------|            
            #   |   1  |                      Firmware Version                     |
            #   |------|-----------------------------------------------------------|
            #   |   2  |                      Battery Voltage                      |
            #   |------|-----------------------------------------------------------|

            hw_version = decoded[0]
            sw_version = decoded[1]
            battery = decoded[2]/10+2.9

            return {
                "port": fport,
                "hw_version": hw_version,
                "sw_version": sw_version,
                "battery": battery
            }
        
        case 3:
            #    Data frame 
            #   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
            #   |------|--------|--------|------|------|------|------|------|------|
            #   |   0  |                                                           |
            #   |   1  |                                                           |
            #   |   2  |                        Latitude                           |
            #   |   3  |                                                           |
            #   |------|-----------------------------------------------------------|
            #   |   4  |                                                           |
            #   |   5  |                                                           |
            #   |   6  |                        Longitude                          |
            #   |   7  |                                                           |
            #   |------|-----------------------------------------------------------|
            #   |   8  |           HDOP                |         PDOP              |
            #   |------|-------------------------------|---------------------------|
            #   |   9  |           SATs                |         VDOP              |
            #   |------|-------------------------------|---------------------------|

            latitude = int.from_bytes(decoded[0:4], byteorder='big', signed=True)/1000000
            longitude = int.from_bytes(decoded[4:8], byteorder='big', signed=True)/1000000
            pdop = decoded[8] & 0b00001111
            hdop = (decoded[8] & 0b11110000) >> 4
            vdop = (decoded[9] & 0b00001111)
            sats = (decoded[9] & 0b11110000) >> 4

            return {
                "port": fport,
                "latitude": latitude,
                "longitude": longitude,
                "pdop": pdop,
                "hdop": hdop,
                "vdop": vdop,
                "sats": sats
            }
        
        case 4:
            #    Data frame
            #   | byte |  bit7  |  bit6  | bit5 | bit4 | bit3 | bit2 | bit1 | bit0 |
            #   |------|--------|--------|------|------|------|------|------|------|
            #   |   0  |                                                           |
            #   |   1  |                                                           |
            #   |   2  |                      MAC Address                          |
            #   |   3  |                                                           |
            #   |   4  |                                                           |
            #   |   5  |                                                           |
            #   |------|-----------------------------------------------------------|
            #   |   6  |                      RSSI                                 |
            #   |------|-----------------------------------------------------------|
            #   |   7  |   Total tags discovered       |    Index                  |

            ble_mac = decoded[0:6].hex()
            ble_rssi = int.from_bytes(decoded[6:7], byteorder='big', signed=True)
            index = decoded[7] & 0b00001111
            total = (decoded[7] & 0b11110000) >> 4

            return {
                "port": fport,
                "ble_mac": ble_mac,
                "ble_rssi": ble_rssi,
                "index": index,
                "total": total
            }
        
        case _:
            return {
                "port": fport,
                "data": decoded.hex()
            }