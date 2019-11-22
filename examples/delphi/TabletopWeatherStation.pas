program TabletopWeatherStation;

{$ifdef MSWINDOWS}{$apptype CONSOLE}{$endif}
{$ifdef FPC}{$mode OBJFPC}{$H+}{$endif}

uses
  SysUtils, IPConnection, Device, BrickletLCD128x64, BrickletAirQuality;

const
  HOST = 'localhost';
  PORT = 4223;

type
  TTabletopWeatherStation = class
  private
    ipcon: TIPConnection;
    brickletLCD: TBrickletLCD128x64;
    brickletAirQuality: TBrickletAirQuality;
  public
    constructor Create;
    destructor Destroy; override;
    procedure ConnectedCB(sender: TIPConnection; const connectedReason: byte);
    procedure EnumerateCB(sender: TIPConnection; const uid: string;
                          const connectedUid: string; const position: char;
                          const hardwareVersion: TVersionNumber;
                          const firmwareVersion: TVersionNumber;
                          const deviceIdentifier: word; const enumerationType: byte);
    procedure AllValuesCB(sender: TBrickletAirQuality; const iaqIndex: longint;
                          const iaqIndexAccuracy: byte; const temperature: longint;
                          const humidity: longint; const airPressure: longint);
    procedure Execute;
  end;

var
  tws: TTabletopWeatherStation;

constructor TTabletopWeatherStation.Create;
begin
  ipcon := nil;
  brickletLCD := nil;
  brickletAirQuality := nil;
end;

destructor TTabletopWeatherStation.Destroy;
begin
  if (brickletLCD <> nil) then brickletLCD.Destroy;
  if (brickletAirQuality <> nil) then brickletAirQuality.Destroy;
  if (ipcon <> nil) then ipcon.Destroy;
  inherited Destroy;
end;

procedure TTabletopWeatherStation.ConnectedCB(sender: TIPConnection; const connectedReason: byte);
begin
  { Eumerate again after auto-reconnect }
  if (connectedReason = IPCON_CONNECT_REASON_AUTO_RECONNECT) then begin
    WriteLn('Auto Reconnect');
    while (true) do begin
      try
        ipcon.Enumerate;
        break;
      except
        on e: Exception do begin
          WriteLn('Enumeration Error: ' + e.Message);
          Sleep(1000);
        end;
      end;
    end;
  end;
end;

procedure TTabletopWeatherStation.EnumerateCB(sender: TIPConnection; const uid: string;
                                              const connectedUid: string; const position: char;
                                              const hardwareVersion: TVersionNumber;
                                              const firmwareVersion: TVersionNumber;
                                              const deviceIdentifier: word; const enumerationType: byte);
begin
  if ((enumerationType = IPCON_ENUMERATION_TYPE_CONNECTED) or
      (enumerationType = IPCON_ENUMERATION_TYPE_AVAILABLE)) then begin
    if (deviceIdentifier = BRICKLET_LCD_128X64_DEVICE_IDENTIFIER) then begin
      try
        { Initialize newly enumerated LCD128x64 Bricklet }
        brickletLCD := TBrickletLCD128x64.Create(UID, ipcon);
        brickletLCD.ClearDisplay;
		brickletLCD.WriteLine(0, 0, '   Weather Station');
        WriteLn('LCD 128x64 initialized');
      except
        on e: Exception do begin
          WriteLn('LCD 128x64 init failed: ' + e.Message);
          brickletLCD := nil;
        end;
      end;
    end
    else if (deviceIdentifier = BRICKLET_AIR_QUALITY_DEVICE_IDENTIFIER) then begin
      try
	    { Initialize newly enumaratedy Air Quality Bricklet and configure callbacks }
        brickletAirQuality := TBrickletAirQuality.Create(uid, ipcon);
        brickletAirQuality.SetAllValuesCallbackConfiguration(1000, true);
        brickletAirQuality.OnAllValues := {$ifdef FPC}@{$endif}AllValuesCB;
        WriteLn('Air Quality initialized');
      except
        on e: Exception do begin
          WriteLn('Air Quality init failed: ' + e.Message);
          brickletAirQuality := nil;
        end;
      end;
    end
  end;
end;

procedure TTabletopWeatherStation.AllValuesCB(sender: TBrickletAirQuality; const iaqIndex: longint;
                                              const iaqIndexAccuracy: byte; const temperature: longint;
                                              const humidity: longint; const airPressure: longint);
var text: string;
begin
  if (brickletLCD <> nil) then begin
    text := Format('IAQ:      %6d', [iaqIndex]);
    brickletLCD.WriteLine(2, 0, text);

	{ $F8 == ° on LCD 128x64 charset }
    text := Format('Temp:     %6.2f %sC', [temperature/100.0, '' + char($F8)]);
    brickletLCD.WriteLine(3, 0, text);
    text := Format('Humidity: %6.2f %%RH', [humidity/100.0]);
    brickletLCD.WriteLine(4, 0, text);
    text := Format('Air Pres: %6.2f hPa', [airPressure/100.0]);
    brickletLCD.WriteLine(5, 0, text);
  end;
end;

procedure TTabletopWeatherStation.Execute;
begin
  ipcon := TIPConnection.Create; { Create IP connection }

  { Connect to brickd (retry if not possible) }
  while (true) do begin
    try
      ipcon.Connect(HOST, PORT);
      break;
    except
      on e: Exception do begin
        WriteLn('Connection Error: ' + e.Message);
        Sleep(1000);
      end;
    end;
  end;
  ipcon.OnEnumerate := {$ifdef FPC}@{$endif}EnumerateCB;
  ipcon.OnConnected := {$ifdef FPC}@{$endif}ConnectedCB;

  { Enumerate Bricks and Bricklets (retry if not possible) }
  while (true) do begin
    try
      ipcon.Enumerate;
      break;
    except
      on e: Exception do begin
        WriteLn('Enumeration Error: ' + e.Message);
        Sleep(1000);
      end;
    end;
  end;
  WriteLn('Press key to exit');
  ReadLn;
end;

begin
  tws := TTabletopWeatherStation.Create;
  tws.Execute;
  tws.Destroy;
end.
