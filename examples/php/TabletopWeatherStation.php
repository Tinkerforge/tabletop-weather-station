<?php

require_once('Tinkerforge/IPConnection.php');
require_once('Tinkerforge/BrickletLCD128x64.php');
require_once('Tinkerforge/BrickletAirQuality.php');

use Tinkerforge\IPConnection;
use Tinkerforge\BrickletLCD128x64;
use Tinkerforge\BrickletAirQuality;

class WeatherStation
{
	const HOST = 'localhost';
	const PORT = 4223;

	public function __construct()
    {
		$this->brickletLCD = null;
		$this->brickletAirQuality = null;
		$this->ipcon = new IPConnection(); // Create IP connection

		// Connect to brickd (retry if not possible)
		while(true) {
			try {
				$this->ipcon->connect(self::HOST, self::PORT);
				break;
			} catch(Exception $e) {
				sleep(1);
			}
		}

		$this->ipcon->registerCallback(IPConnection::CALLBACK_ENUMERATE,
		                               array($this, 'cb_enumerate'));
		$this->ipcon->registerCallback(IPConnection::CALLBACK_CONNECTED,
		                               array($this, 'cb_connected'));

		// Enumerate Bricks and Bricklets (retry if not possible)
		while(true) {
			try {
				$this->ipcon->enumerate();
				break;
			} catch(Exception $e) {
				sleep(1);
			}
		}
	}

	function cb_all_values($iaq_index, $iaq_index_accuracy, $temperature, $humidity, $air_pressure)
	{
		if($this->brickletLCD != null) {
			$this->brickletLCD->writeLine(2, 0, sprintf("IAQ:      %6d", $iaq_index));
			// 0xF8 == ° on LCD 128x64 charset
			$this->brickletLCD->writeLine(3, 0, sprintf("Temp:     %6.2f %cC", $temperature/100.0, 0xF8));
			$this->brickletLCD->writeLine(4, 0, sprintf("Humidity: %6.2f %%RH", $humidity/100.0));
			$this->brickletLCD->writeLine(5, 0, sprintf("Air Pres: %6.2f hPa", $air_pressure/100.0));
		}
	}

	function cb_enumerate($uid, $connectedUid, $position, $hardwareVersion,
	                      $firmwareVersion, $deviceIdentifier, $enumerationType)
	{
		if($enumerationType == IPConnection::ENUMERATION_TYPE_CONNECTED ||
		   $enumerationType == IPConnection::ENUMERATION_TYPE_AVAILABLE) {
			if($deviceIdentifier == BrickletLCD128x64::DEVICE_IDENTIFIER) {
				try {
					// Initialize newly enumerated LCD128x64 Bricklet
					$this->brickletLCD = new BrickletLCD128x64($uid, $this->ipcon);
					$this->brickletLCD->clearDisplay();
					$this->brickletLCD->writeLine(0, 0, "   Weather Station");
					echo "LCD 128x64 initialized\n";
				} catch(Exception $e) {
					$this->brickletLCD = null;
					echo "LCD 128x64 init failed: $e\n";
				}
			} else if($deviceIdentifier == BrickletAirQuality::DEVICE_IDENTIFIER) {
				try {
					// Initialize newly enumaratedy Air Quality Bricklet and configure callbacks
					$this->brickletAirQuality = new BrickletAirQuality($uid, $this->ipcon);
					$this->brickletAirQuality->setAllValuesCallbackConfiguration(1000, true);
					$this->brickletAirQuality->registerCallback(BrickletAirQuality::CALLBACK_ALL_VALUES,
					                                            array($this, 'cb_all_values'));
					echo "Air Quality initialized\n";
				} catch(Exception $e) {
					$this->brickletAirQuality = null;
					echo "Air Quality init failed: $e\n";
				}
			} 
		}
	}

	function cb_connected($connectedReason)
	{
		// Eumerate again after auto-reconnect
		if($connectedReason == IPConnection::CONNECT_REASON_AUTO_RECONNECT) {
			echo "Auto Reconnect\n";

			while(true) {
				try {
					$this->ipcon->enumerate();
					break;
				} catch(Exception $e) {
					sleep(1);
				}
			}
		}
	}
}

$weatherStation = new WeatherStation();
echo "Press ctrl+c to exit\n";
$weatherStation->ipcon->dispatchCallbacks(-1);

?>
