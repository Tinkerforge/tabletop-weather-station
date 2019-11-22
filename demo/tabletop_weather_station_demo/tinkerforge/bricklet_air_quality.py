# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-12-21.      #
#                                                           #
# Python Bindings Version 2.1.20                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetAllValues = namedtuple('AllValues', ['iaq_index', 'iaq_index_accuracy', 'temperature', 'humidity', 'air_pressure'])
GetAllValuesCallbackConfiguration = namedtuple('AllValuesCallbackConfiguration', ['period', 'value_has_to_change'])
GetIAQIndex = namedtuple('IAQIndex', ['iaq_index', 'iaq_index_accuracy'])
GetIAQIndexCallbackConfiguration = namedtuple('IAQIndexCallbackConfiguration', ['period', 'value_has_to_change'])
GetTemperatureCallbackConfiguration = namedtuple('TemperatureCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetHumidityCallbackConfiguration = namedtuple('HumidityCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetAirPressureCallbackConfiguration = namedtuple('AirPressureCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletAirQuality(Device):
    """
    Measures IAQ index, temperature, humidity and air pressure
    """

    DEVICE_IDENTIFIER = 297
    DEVICE_DISPLAY_NAME = 'Air Quality Bricklet'
    DEVICE_URL_PART = 'air_quality' # internal

    CALLBACK_ALL_VALUES = 6
    CALLBACK_IAQ_INDEX = 10
    CALLBACK_TEMPERATURE = 14
    CALLBACK_HUMIDITY = 18
    CALLBACK_AIR_PRESSURE = 22


    FUNCTION_GET_ALL_VALUES = 1
    FUNCTION_SET_TEMPERATURE_OFFSET = 2
    FUNCTION_GET_TEMPERATURE_OFFSET = 3
    FUNCTION_SET_ALL_VALUES_CALLBACK_CONFIGURATION = 4
    FUNCTION_GET_ALL_VALUES_CALLBACK_CONFIGURATION = 5
    FUNCTION_GET_IAQ_INDEX = 7
    FUNCTION_SET_IAQ_INDEX_CALLBACK_CONFIGURATION = 8
    FUNCTION_GET_IAQ_INDEX_CALLBACK_CONFIGURATION = 9
    FUNCTION_GET_TEMPERATURE = 11
    FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION = 12
    FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION = 13
    FUNCTION_GET_HUMIDITY = 15
    FUNCTION_SET_HUMIDITY_CALLBACK_CONFIGURATION = 16
    FUNCTION_GET_HUMIDITY_CALLBACK_CONFIGURATION = 17
    FUNCTION_GET_AIR_PRESSURE = 19
    FUNCTION_SET_AIR_PRESSURE_CALLBACK_CONFIGURATION = 20
    FUNCTION_GET_AIR_PRESSURE_CALLBACK_CONFIGURATION = 21
    FUNCTION_GET_SPITFP_ERROR_COUNT = 234
    FUNCTION_SET_BOOTLOADER_MODE = 235
    FUNCTION_GET_BOOTLOADER_MODE = 236
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_SET_STATUS_LED_CONFIG = 239
    FUNCTION_GET_STATUS_LED_CONFIG = 240
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_WRITE_UID = 248
    FUNCTION_READ_UID = 249
    FUNCTION_GET_IDENTITY = 255

    ACCURACY_UNRELIABLE = 0
    ACCURACY_LOW = 1
    ACCURACY_MEDIUM = 2
    ACCURACY_HIGH = 3
    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    BOOTLOADER_MODE_BOOTLOADER = 0
    BOOTLOADER_MODE_FIRMWARE = 1
    BOOTLOADER_MODE_BOOTLOADER_WAIT_FOR_REBOOT = 2
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_REBOOT = 3
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_ERASE_AND_REBOOT = 4
    BOOTLOADER_STATUS_OK = 0
    BOOTLOADER_STATUS_INVALID_MODE = 1
    BOOTLOADER_STATUS_NO_CHANGE = 2
    BOOTLOADER_STATUS_ENTRY_FUNCTION_NOT_PRESENT = 3
    BOOTLOADER_STATUS_DEVICE_IDENTIFIER_INCORRECT = 4
    BOOTLOADER_STATUS_CRC_MISMATCH = 5
    STATUS_LED_CONFIG_OFF = 0
    STATUS_LED_CONFIG_ON = 1
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 2
    STATUS_LED_CONFIG_SHOW_STATUS = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletAirQuality.FUNCTION_GET_ALL_VALUES] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_TEMPERATURE_OFFSET] = BrickletAirQuality.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_TEMPERATURE_OFFSET] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_ALL_VALUES_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_ALL_VALUES_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_IAQ_INDEX] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_IAQ_INDEX_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_IAQ_INDEX_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_TEMPERATURE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_HUMIDITY] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_HUMIDITY_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_HUMIDITY_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_AIR_PRESSURE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_AIR_PRESSURE_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_AIR_PRESSURE_CALLBACK_CONFIGURATION] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_BOOTLOADER_MODE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_BOOTLOADER_MODE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletAirQuality.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAirQuality.FUNCTION_WRITE_FIRMWARE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletAirQuality.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_RESET] = BrickletAirQuality.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAirQuality.FUNCTION_WRITE_UID] = BrickletAirQuality.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAirQuality.FUNCTION_READ_UID] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAirQuality.FUNCTION_GET_IDENTITY] = BrickletAirQuality.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletAirQuality.CALLBACK_ALL_VALUES] = 'i B i i i'
        self.callback_formats[BrickletAirQuality.CALLBACK_IAQ_INDEX] = 'i B'
        self.callback_formats[BrickletAirQuality.CALLBACK_TEMPERATURE] = 'i'
        self.callback_formats[BrickletAirQuality.CALLBACK_HUMIDITY] = 'i'
        self.callback_formats[BrickletAirQuality.CALLBACK_AIR_PRESSURE] = 'i'


    def get_all_values(self):
        """
        Returns all values measured by the Air Quality Bricklet. The values are
        IAQ (Indoor Air Quality) Index, IAQ Index Accuracy, Temperature, Humidity and
        Air Pressure.

        .. image:: /Images/Misc/bricklet_air_quality_iaq_index.png
           :scale: 100 %
           :alt: Air Quality Index description
           :align: center
           :target: ../../_images/Misc/bricklet_air_quality_iaq_index.png

        The values have these ranges and units:

        * IAQ Index: 0 to 500, higher value means greater level of air pollution
        * IAQ Index Accuracy: 0 = unreliable to 3 = high
        * Temperature: in steps of 0.01 °C
        * Humidity: in steps of 0.01 %RH
        * Air Pressure: in steps of 0.01 hPa
        """
        return GetAllValues(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_ALL_VALUES, (), '', 'i B i i i'))

    def set_temperature_offset(self, offset):
        """
        Sets a temperature offset in 1/100°C. A offset of 10 will decrease the measured
        temperature by 0.1°C.

        If you install this Bricklet into an enclosure and you want to measure the ambient
        temperature, you may have to decrease the measured temperature by some value to
        compensate for the error because of the heating inside of the enclosure.

        We recommend that you leave the parts in the enclosure running for at least
        24 hours such that a temperature equilibrium can be reached. After that you can measure
        the temperature directly outside of enclosure and set the difference as offset.

        This temperature offset is used to calculate the relative humidity and
        IAQ index measurements. In case the Bricklet is installed in an enclosure, we
        recommend to measure and set the temperature offset to imporve the accuracy of
        the measurements.
        """
        offset = int(offset)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_TEMPERATURE_OFFSET, (offset,), 'i', '')

    def get_temperature_offset(self):
        """
        Returns the temperature offset as set by
        :func:`Set Temperature Offset`.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_TEMPERATURE_OFFSET, (), '', 'i')

    def set_all_values_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`All Values`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after at least one of the values has changed. If the values didn't
        change within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_ALL_VALUES_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_all_values_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set All Values Callback Configuration`.
        """
        return GetAllValuesCallbackConfiguration(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_ALL_VALUES_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_iaq_index(self):
        """
        Returns the IAQ index and accuracy. The IAQ index goes from
        0 to 500. The higher the IAQ index, the greater the level of air pollution.

        .. image:: /Images/Misc/bricklet_air_quality_iaq_index.png
           :scale: 100 %
           :alt: IAQ index description
           :align: center
           :target: ../../_images/Misc/bricklet_air_quality_iaq_index.png

        If you want to get the value periodically, it is recommended to use the
        :cb:`IAQ Index` callback. You can set the callback configuration
        with :func:`Set IAQ Index Callback Configuration`.
        """
        return GetIAQIndex(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_IAQ_INDEX, (), '', 'i B'))

    def set_iaq_index_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`IAQ Index`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after at least one of the values has changed. If the values didn't
        change within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        The default value is (0, false).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_IAQ_INDEX_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_iaq_index_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set IAQ Index Callback Configuration`.
        """
        return GetIAQIndexCallbackConfiguration(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_IAQ_INDEX_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def get_temperature(self):
        """
        Returns temperature in steps of 0.01 °C.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Temperature` callback. You can set the callback configuration
        with :func:`Set Temperature Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_TEMPERATURE, (), '', 'i')

    def set_temperature_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        The period in ms is the period with which the :cb:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Temperature` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c i i', '')

    def get_temperature_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Temperature Callback Configuration`.
        """
        return GetTemperatureCallbackConfiguration(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION, (), '', 'I ! c i i'))

    def get_humidity(self):
        """
        Returns relative humidity in steps of 0.01 %RH.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Humidity` callback. You can set the callback configuration
        with :func:`Set Humidity Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_HUMIDITY, (), '', 'i')

    def set_humidity_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        The period in ms is the period with which the :cb:`Humidity` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Humidity` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_HUMIDITY_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c i i', '')

    def get_humidity_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Humidity Callback Configuration`.
        """
        return GetHumidityCallbackConfiguration(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_HUMIDITY_CALLBACK_CONFIGURATION, (), '', 'I ! c i i'))

    def get_air_pressure(self):
        """
        Returns air pressure in steps of 0.01 hPa.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Air Pressure` callback. You can set the callback configuration
        with :func:`Set Air Pressure Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_AIR_PRESSURE, (), '', 'i')

    def set_air_pressure_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        The period in ms is the period with which the :cb:`Air Pressure` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Air Pressure` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_AIR_PRESSURE_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c i i', '')

    def get_air_pressure_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Air Pressure Callback Configuration`.
        """
        return GetAirPressureCallbackConfiguration(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_AIR_PRESSURE_CALLBACK_CONFIGURATION, (), '', 'I ! c i i'))

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.

        The errors are divided into

        * ACK checksum errors,
        * message checksum errors,
        * framing errors and
        * overflow errors.

        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.

        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier and CRC are present and correct.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        mode = int(mode)

        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAirQuality.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

AirQuality = BrickletAirQuality # for backward compatibility
