#!/usr/bin/env ruby
# -*- ruby encoding: utf-8 -*-

require 'tinkerforge/ip_connection'
require 'tinkerforge/bricklet_lcd_128x64'
require 'tinkerforge/bricklet_air_quality'
include Tinkerforge

HOST = 'localhost'
PORT = 4223

lcd = nil
air_quality = nil

ipcon = IPConnection.new # Create IP connection

# Connect to brickd (retry if not possible)
while true
  begin
    ipcon.connect HOST, PORT
    break
  rescue Exception => e
    puts 'Connection Error: ' + e
    sleep 1
  end
end

ipcon.register_callback(IPConnection::CALLBACK_ENUMERATE) do |uid, connected_uid, position,
                                                              hardware_version, firmware_version,
                                                              device_identifier, enumeration_type|
  if enumeration_type == IPConnection::ENUMERATION_TYPE_CONNECTED or
     enumeration_type == IPConnection::ENUMERATION_TYPE_AVAILABLE
    if device_identifier == BrickletLCD128x64::DEVICE_IDENTIFIER
      begin
        lcd = BrickletLCD128x64.new uid, ipcon
        lcd.clear_display
		lcd.write_line 0, 0, '   Weather Station'
        puts 'LCD 128x64 initialized'
      rescue Exception => e
        lcd = nil
        puts 'LCD 128x64 init failed: ' + e
      end
    elsif device_identifier == BrickletAirQuality::DEVICE_IDENTIFIER
      begin
        air_quality = BrickletAirQuality.new uid, ipcon
        air_quality.set_all_values_callback_configuration 1000, false
        air_quality.register_callback(BrickletAirQuality::CALLBACK_ALL_VALUES) do |iaq_index,
                                                                                   iaq_index_accuracy,
                                                                                   temperature, humidity,
                                                                                   air_pressure|
          if lcd != nil
            lcd.write_line 2, 0, 'IAQ:      %6d' % (iaq_index)
            # 0xF8 == ° on LCD 128x64 charset
            lcd.write_line 3, 0, 'Temp:     %6.2f %sC' % [(temperature/100.0), (0xF8.chr)]
            lcd.write_line 4, 0, 'Humidity: %6.2f %%RH' % (humidity/100.0)
            lcd.write_line 5, 0, 'Air Pres: %6.2f mbar' % (air_pressure/100.0)
          end
        end
        puts 'Air Quality initialized'
      rescue Exception => e
        air_quality = nil
        puts 'Air Quality init failed: ' + e
      end
    end
  end
end

ipcon.register_callback(IPConnection::CALLBACK_CONNECTED) do |connected_reason|
  # Eumerate again after auto-reconnect
  if connected_reason == IPConnection::CONNECT_REASON_AUTO_RECONNECT
    puts 'Auto Reconnect'
    while true
      begin
        ipcon.enumerate
        break
      rescue Exception => e
        puts 'Enumerate Error: ' + e
        sleep 1
      end
    end
  end
end

# Enumerate Bricks and Bricklets (retry if not possible)
while true
  begin
    ipcon.enumerate
    break
  rescue Exception => e
    puts 'Enumerate Error: ' + e
    sleep 1
  end
end

puts 'Press key to exit'
$stdin.gets
ipcon.disconnect
