import com.tinkerforge.IPConnection;
import com.tinkerforge.BrickletLCD128x64;
import com.tinkerforge.BrickletAirQuality;

class WeatherListener implements IPConnection.EnumerateListener,
                                 IPConnection.ConnectedListener,
                                 BrickletAirQuality.AllValuesListener {
	private IPConnection ipcon = null;
	private BrickletLCD128x64 brickletLCD = null;
	private BrickletAirQuality brickletAirQuality = null;

	public WeatherListener(IPConnection ipcon) {
		this.ipcon = ipcon;
	}

	public void allValues(int iaqIndex, int iaqIndexAccuracy, int temperature,
	                      int humidity, int airPressure) {
		if(brickletLCD != null) {
			try {
				brickletLCD.writeLine(2, 0, String.format("IAQ:      %6d", iaqIndex));
				brickletLCD.writeLine(3, 0, String.format("Temp:     %6.2f %cC", temperature/100.0, 0xF8));
				brickletLCD.writeLine(4, 0, String.format("Humidity: %6.2f %%RH", humidity/100.0));
				brickletLCD.writeLine(5, 0, String.format("Air Pres: %6.2f hPa", airPressure/100.0));
			} catch(com.tinkerforge.TinkerforgeException e) {
				System.out.println("Error during writeLine: " + e);
			}
		}
    }

	public void enumerate(String uid, String connectedUid, char position,
	                      short[] hardwareVersion, short[] firmwareVersion,
	                      int deviceIdentifier, short enumerationType) {
		if(enumerationType == IPConnection.ENUMERATION_TYPE_CONNECTED ||
		   enumerationType == IPConnection.ENUMERATION_TYPE_AVAILABLE) {
			if(deviceIdentifier == BrickletLCD128x64.DEVICE_IDENTIFIER) {
				try {
					// Initialize newly enumerated LCD128x64 Bricklet
					brickletLCD = new BrickletLCD128x64(uid, ipcon);
					brickletLCD.clearDisplay();
					brickletLCD.writeLine(0, 0, "   Weather Station");
					System.out.println("LCD 128x64 initialized");
				} catch(com.tinkerforge.TinkerforgeException e) {
					brickletLCD = null;
					System.out.println("LCD 128x64 init failed: " + e);
				}
			} else if(deviceIdentifier == BrickletAirQuality.DEVICE_IDENTIFIER) {
				try {
					// Initialize newly enumaratedy Air Quality Bricklet and configure callbacks
					brickletAirQuality = new BrickletAirQuality(uid, ipcon);
					brickletAirQuality.setAllValuesCallbackConfiguration(1000, false);
					brickletAirQuality.addAllValuesListener(this);
					System.out.println("Air Quality initialized");
				} catch(com.tinkerforge.TinkerforgeException e) {
					brickletAirQuality = null;
					System.out.println("Air Quality init failed: " + e);
				}
			}
		}
	}

	public void connected(short connectedReason) {
		// Eumerate again after auto-reconnect
		if(connectedReason == IPConnection.CONNECT_REASON_AUTO_RECONNECT) {
			System.out.println("Auto Reconnect");

			while(true) {
				try {
					ipcon.enumerate();
					break;
				} catch(com.tinkerforge.NotConnectedException e) {
				}

				try {
					Thread.sleep(1000);
				} catch(InterruptedException ei) {
				}
			}
		}
	}
}

public class TabletopWeatherStation {
	private static final String HOST = "localhost";
	private static final int PORT = 4223;
	private static IPConnection ipcon = null;
	private static WeatherListener weatherListener = null;

	public static void main(String args[]) {
		ipcon = new IPConnection();

		// Connect to brickd (retry if not possible)
		while(true) {
			try {
				ipcon.connect(HOST, PORT);
				break;
			} catch(com.tinkerforge.TinkerforgeException e) {
			}

			try {
				Thread.sleep(1000);
			} catch(InterruptedException ei) {
			}
		}

		weatherListener = new WeatherListener(ipcon);
		ipcon.addEnumerateListener(weatherListener);
		ipcon.addConnectedListener(weatherListener);

		// Enumerate Bricks and Bricklets (retry if not possible)
		while(true) {
			try {
				ipcon.enumerate();
				break;
			} catch(com.tinkerforge.NotConnectedException e) {
			}

			try {
				Thread.sleep(1000);
			} catch(InterruptedException ei) {
			}
		}

		try {
			System.out.println("Press key to exit"); System.in.read();
		} catch(java.io.IOException e) {
		}

		try {
			ipcon.disconnect();
		} catch(com.tinkerforge.NotConnectedException e) {
		}
	}
}
