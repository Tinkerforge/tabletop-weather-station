#include <stdio.h>

#include "ip_connection.h"
#include "bricklet_lcd_128x64.h"
#include "bricklet_air_quality.h"

#define HOST "localhost"
#define PORT 4223

void millisleep(uint32_t msec); // defined in ip_connection.c

typedef struct {
	IPConnection ipcon;
	LCD128x64 lcd;
	bool lcd_created;
	AirQuality air_quality;
} TabletopWeatherStation;

void cb_all_values(int32_t iaq_index, uint8_t iaq_index_accuracy, int32_t temperature,
                   int32_t humidity, int32_t air_pressure, void *user_data) {
	TabletopWeatherStation *tws = (TabletopWeatherStation *)user_data;

	if(tws->lcd_created) {
		char text[30] = {'\0'};

		sprintf(text, "IAQ:      %6d", iaq_index);
		lcd_128x64_write_line(&tws->lcd, 2, 0, text);

		// 0xF8 == ° on LCD 128x64 charset
		sprintf(text, "Temp:     %6.2f %cC", temperature/100.0, 0xF8);
		lcd_128x64_write_line(&tws->lcd, 3, 0, text);
		sprintf(text, "Humidity: %6.2f %%RH", humidity/100.0);
		lcd_128x64_write_line(&tws->lcd, 4, 0, text);
		sprintf(text, "Air Pres: %6.2f hPa", air_pressure/100.0);
		lcd_128x64_write_line(&tws->lcd, 5, 0, text);
	}
}

void cb_connected(uint8_t connected_reason, void *user_data) {
	TabletopWeatherStation *tws = (TabletopWeatherStation *)user_data;

	// Eumerate again after auto-reconnect
	if(connected_reason == IPCON_CONNECT_REASON_AUTO_RECONNECT) {
		printf("Auto Reconnect\n");

		while(true) {
			int rc = ipcon_enumerate(&tws->ipcon);
			if(rc < 0) {
				fprintf(stderr, "Could not enumerate: %d\n", rc);
				millisleep(1000);
				continue;
			}
			break;
		}
	}
}

void cb_enumerate(const char *uid, const char *connected_uid,
                  char position, uint8_t hardware_version[3],
                  uint8_t firmware_version[3], uint16_t device_identifier,
                  uint8_t enumeration_type, void *user_data) {
	TabletopWeatherStation *tws = (TabletopWeatherStation *)user_data;
	int rc;

	// avoid unused parameter warning
	(void)connected_uid; (void)position; (void)hardware_version; (void)firmware_version;

	if(enumeration_type == IPCON_ENUMERATION_TYPE_CONNECTED ||
	   enumeration_type == IPCON_ENUMERATION_TYPE_AVAILABLE) {
		if(device_identifier == LCD_128X64_DEVICE_IDENTIFIER) {
			lcd_128x64_create(&tws->lcd, uid, &tws->ipcon);
			lcd_128x64_clear_display(&tws->lcd);
			lcd_128x64_write_line(&tws->lcd, 0, 0, "   Weather Station");
			tws->lcd_created = true;
			printf("LCD 128x64 initialized\n");
		} else if(device_identifier == AIR_QUALITY_DEVICE_IDENTIFIER) {
			air_quality_create(&tws->air_quality, uid, &tws->ipcon);
			air_quality_register_callback(&tws->air_quality,
			                              AIR_QUALITY_CALLBACK_ALL_VALUES,
			                              (void *)cb_all_values,
			                              (void *)tws);
			rc = air_quality_set_all_values_callback_configuration(&tws->air_quality, 1000, false);

			if(rc < 0) {
				fprintf(stderr, "Air Quality init failed: %d\n", rc);
			} else {
				printf("Air Quality initialized\n");
			}
		}
	}
}

int main() {
	TabletopWeatherStation tws;

	tws.lcd_created = false;
	ipcon_create(&tws.ipcon); // Create IP connection

	// Connect to brickd (retry if not possible)
	while(true) {
		int rc = ipcon_connect(&tws.ipcon, HOST, PORT);
		if(rc < 0) {
			fprintf(stderr, "Could not connect to brickd: %d\n", rc);
			millisleep(1000);
			continue;
		}
		break;
	}

	ipcon_register_callback(&tws.ipcon,
	                        IPCON_CALLBACK_ENUMERATE,
	                        (void *)cb_enumerate,
	                        (void *)&tws);

	ipcon_register_callback(&tws.ipcon,
	                        IPCON_CALLBACK_CONNECTED,
	                        (void *)cb_connected,
	                        (void *)&tws);

	// Enumerate Bricks and Bricklets (retry if not possible)
	while(true) {
		int rc = ipcon_enumerate(&tws.ipcon);
		if(rc < 0) {
			fprintf(stderr, "Could not enumerate: %d\n", rc);
			millisleep(1000);
			continue;
		}
		break;
	}

	printf("Press key to exit\n");
	getchar();
	ipcon_destroy(&tws.ipcon);
	return 0;
}
