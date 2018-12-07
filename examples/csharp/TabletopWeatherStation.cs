using System;
using Tinkerforge;

class TabletopWeatherStation
{
	private static string HOST = "localhost";
	private static int PORT = 4223;

	private static IPConnection ipcon = null;
	private static BrickletLCD128x64 brickletLCD = null;
	private static BrickletAirQuality brickletAirQuality = null;

	static void AllValuesCB(BrickletAirQuality sender, int iaqIndex,
	                        byte iaqIndexAccuracy, int temperature, int humidity,
	                        int airPressure)
	{
		if(brickletLCD != null)
		{
			brickletLCD.WriteLine(2, 0, String.Format("IAQ:      {0,6:###}",    iaqIndex));
			// 0xF8 == ° on LCD 128x64 charset
			brickletLCD.WriteLine(3, 0, String.Format("Temp:     {0,6:##.00} {1}C", temperature/100.0, (char)0xF8));
			brickletLCD.WriteLine(4, 0, String.Format("Humidity: {0,6:##.00} %RH",  humidity/100.0));
			brickletLCD.WriteLine(5, 0, String.Format("Air Pres: {0,6:####.0} mbar", airPressure/100.0));
		}
	}

	static void EnumerateCB(IPConnection sender, string UID, string connectedUID, char position,
	                        short[] hardwareVersion, short[] firmwareVersion,
	                        int deviceIdentifier, short enumerationType)
	{
		if(enumerationType == IPConnection.ENUMERATION_TYPE_CONNECTED ||
		   enumerationType == IPConnection.ENUMERATION_TYPE_AVAILABLE)
		{
			if(deviceIdentifier == BrickletLCD128x64.DEVICE_IDENTIFIER)
			{
				try
				{
					// Initialize newly enumerated LCD128x64 Bricklet
					brickletLCD = new BrickletLCD128x64(UID, ipcon);
					brickletLCD.ClearDisplay();
					brickletLCD.WriteLine(0, 0, "   Weather Station");
					System.Console.WriteLine("LCD 128x64 initialized");
				}
				catch(TinkerforgeException e)
				{
					System.Console.WriteLine("LCD 128x64 init failed: " + e.Message);
					brickletLCD = null;
				}
			}
			else if(deviceIdentifier == BrickletAirQuality.DEVICE_IDENTIFIER)
			{
				try
				{
					// Initialize newly enumaratedy Air Quality Bricklet and configure callbacks
					brickletAirQuality = new BrickletAirQuality(UID, ipcon);
					brickletAirQuality.SetAllValuesCallbackConfiguration(1000, false);
					brickletAirQuality.AllValuesCallback += AllValuesCB;
					System.Console.WriteLine("Air Quality initialized");
				}
				catch(TinkerforgeException e)
				{
					System.Console.WriteLine("Air Quality init failed: " + e.Message);
					brickletAirQuality = null;
				}
			}
		}
	}

	static void ConnectedCB(IPConnection sender, short connectedReason)
	{
		// Eumerate again after auto-reconnect
		if(connectedReason == IPConnection.CONNECT_REASON_AUTO_RECONNECT)
		{
			System.Console.WriteLine("Auto Reconnect");

			while(true)
			{
				try
				{
					ipcon.Enumerate();
					break;
				}
				catch(NotConnectedException e)
				{
					System.Console.WriteLine("Enumeration Error: " + e.Message);
					System.Threading.Thread.Sleep(1000);
				}
			}
		}
	}

	static void Main()
	{
		ipcon = new IPConnection(); // Create IP connection

		// Connect to brickd (retry if not possible)
		while(true)
		{
			try
			{
				ipcon.Connect(HOST, PORT);
				break;
			}
			catch(System.Net.Sockets.SocketException e)
			{
				System.Console.WriteLine("Connection Error: " + e.Message);
				System.Threading.Thread.Sleep(1000);
			}
		}

		ipcon.EnumerateCallback += EnumerateCB;
		ipcon.Connected += ConnectedCB;

		// Enumerate Bricks and Bricklets (retry if not possible)
		while(true)
		{
			try
			{
				ipcon.Enumerate();
				break;
			}
			catch(NotConnectedException e)
			{
				System.Console.WriteLine("Enumeration Error: " + e.Message);
				System.Threading.Thread.Sleep(1000);
			}
		}

		System.Console.WriteLine("Press enter to exit");
		System.Console.ReadLine();
		ipcon.Disconnect();
	}
}
