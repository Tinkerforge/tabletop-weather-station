Imports System
Imports Tinkerforge

Module WeatherStation
    Const HOST As String = "localhost"
    Const PORT As Integer = 4223

    Private ipcon As IPConnection = Nothing
    Private brickletLCD As BrickletLCD128x64 = Nothing
    Private brickletAirQuality As BrickletAirQuality = Nothing

    Sub AllValuesCB(ByVal sender As BrickletAirQuality, ByVal iaqIndex As Integer, _
                    ByVal iaqIndexAccuracy As Byte, ByVal temperature As Integer, _
                    ByVal humidity As Integer, ByVal airPressure As Integer)
        If brickletLCD IsNot Nothing Then
			brickletLCD.WriteLine(2, 0, String.Format("IAQ:      {0,6:###}",    iaqIndex))
			' 0xF8 == ° on LCD 128x64 charset
			brickletLCD.WriteLine(3, 0, String.Format("Temp:     {0,6:##.00} {1}C", temperature/100.0, Chr(&HF8)))
			brickletLCD.WriteLine(4, 0, String.Format("Humidity: {0,6:##.00} %RH",  humidity/100.0))
			brickletLCD.WriteLine(5, 0, String.Format("Air Pres: {0,6:####.0} mbar", airPressure/100.0))
        End If
    End Sub

    Sub EnumerateCB(ByVal sender As IPConnection, ByVal uid As String, _
                    ByVal connectedUid As String, ByVal position As Char, _
                    ByVal hardwareVersion() As Short, ByVal firmwareVersion() As Short, _
                    ByVal deviceIdentifier As Integer, ByVal enumerationType As Short)
        If enumerationType = IPConnection.ENUMERATION_TYPE_CONNECTED Or _
           enumerationType = IPConnection.ENUMERATION_TYPE_AVAILABLE Then
            If deviceIdentifier = BrickletLCD128x64.DEVICE_IDENTIFIER Then
                Try
					' Initialize newly enumerated LCD128x64 Bricklet
                    brickletLCD = New BrickletLCD128x64(UID, ipcon)
                    brickletLCD.ClearDisplay()
					brickletLCD.WriteLine(0, 0, "   Weather Station")
                    System.Console.WriteLine("LCD 128x64 initialized")
                Catch e As TinkerforgeException
                    System.Console.WriteLine("LCD 128x64 init failed: " + e.Message)
                    brickletLCD = Nothing
                End Try
            Else If deviceIdentifier = BrickletAirQuality.DEVICE_IDENTIFIER Then
                Try
				    ' Initialize newly enumaratedy Air Quality Bricklet and configure callbacks
                    brickletAirQuality = New BrickletAirQuality(UID, ipcon)
                    brickletAirQuality.SetAllValuesCallbackConfiguration(1000, false)
                    AddHandler brickletAirQuality.AllValuesCallback, AddressOf AllValuesCB
                    System.Console.WriteLine("Air Quality initialized")
                Catch e As TinkerforgeException
                    System.Console.WriteLine("Air Quality init failed: " + e.Message)
                    brickletAirQuality = Nothing
                End Try
            End If
        End If
    End Sub

    Sub ConnectedCB(ByVal sender As IPConnection, ByVal connectedReason as Short)
		' Eumerate again after auto-reconnect
        If connectedReason = IPConnection.CONNECT_REASON_AUTO_RECONNECT Then
            System.Console.WriteLine("Auto Reconnect")
            while True
                Try
                    ipcon.Enumerate()
                    Exit While
                Catch e As NotConnectedException
                    System.Console.WriteLine("Enumeration Error: " + e.Message)
                    System.Threading.Thread.Sleep(1000)
                End Try
            End While
        End If
    End Sub

    Sub Main()
        ipcon = New IPConnection() ' Create IP connection

		' Connect to brickd (retry if not possible)
        while True
            Try
                ipcon.Connect(HOST, PORT)
                Exit While
            Catch e As System.Net.Sockets.SocketException
                System.Console.WriteLine("Connection Error: " + e.Message)
                System.Threading.Thread.Sleep(1000)
            End Try
        End While

        AddHandler ipcon.EnumerateCallback, AddressOf EnumerateCB
        AddHandler ipcon.Connected, AddressOf ConnectedCB

		' Enumerate Bricks and Bricklets (retry if not possible)
        while True
            try
                ipcon.Enumerate()
                Exit While
            Catch e As NotConnectedException
                System.Console.WriteLine("Enumeration Error: " + e.Message)
                System.Threading.Thread.Sleep(1000)
            End Try
        End While

        System.Console.WriteLine("Press key to exit")
        System.Console.ReadLine()
        ipcon.Disconnect()
    End Sub
End Module
