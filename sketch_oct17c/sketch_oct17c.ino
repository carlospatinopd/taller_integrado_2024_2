#include <ArduinoJson.h>

const int voltagePin = A0;   // Pin del sensor de voltaje
const int currentPin = A1;   // Pin del sensor de corriente

float voltageValue;  // Variable para el voltaje (0.0 a 25.0)
float currentValue = 10.0;  // Valor constante para la corriente en amperios
float temperatureValue = 25.0; // Valor constante para la temperatura en °C
float pressureValue = 1.0; // Valor constante para la presión en atm

void setup() {
  Serial.begin(9600);  // Iniciar puerto serie
}

void loop() {
  // Lectura del sensor de voltaje
  int voltageSensorValue = analogRead(voltagePin);    
  voltageValue = fmap(voltageSensorValue, 0, 1023, 0.0, 25.275);  // Cambiar escala a 0.0 - 25.0

  // Crear el objeto JSON
  DynamicJsonDocument json(512);
  json["voltaje"] = voltageValue;
  json["corriente"] = currentValue;
  json["temperatura"] = temperatureValue;
  json["presion"] = pressureValue;

  // Serializar el objeto JSON y enviarlo por el puerto serie
  serializeJson(json, Serial);
  Serial.println();  // Nueva línea para que cada mensaje esté separado

  delay(1800);  // Esperar 1 segundo antes de la siguiente lectura
}

// Función para mapear valores float
float fmap(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
