//***************************************************************************
/*
  keyestudio 4wd BT Car
  Lição Modificada: Sensor de Estacionamento (35cm)
  Saída em formato JSON
*/
//***************************************************************************

#include <SoftwareSerial.h>

// Define os pinos para o Serial "virtual" (Bluetooth)
SoftwareSerial btSerial(2, 3); // Arduino RX (2), Arduino TX (3)

// Define os pinos para o Sensor Ultrassônico
int trigPin = 12;    // Trigger
int echoPin = 13;    // Echo
long duration, cm;

void setup() {
  // Inicia a porta Serial (para debug no Monitor Serial do PC)
  Serial.begin(9600);
  
  // Inicia a porta Serial do Bluetooth
  btSerial.begin(9600); 

  // Define os pinos do sensor como entrada/saída
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // Dispara o pulso do sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Lê a duração do pulso de retorno
  duration = pulseIn(echoPin, HIGH);

  // Converte o tempo em uma distância em cm
  cm = (duration / 2) / 29.1;

  // --- Lógica do Sensor de Estacionamento ---
  
  String estado; // Variável para guardar o estado
  
  // Verifica se a distância é válida (maior que 0) E se está dentro do limite (<= 35cm)
  if (cm > 0 && cm <= 35) {
    estado = "ocupado";
  } else {
    // Se não (cm = 0 ou cm > 35), o parque está LIVRE
    estado = "livre";
  }

  // --- Criar e Enviar a String JSON ---
  String jsonData = "{";
  jsonData += "\"parque_id\":\"a1\",";
  jsonData += "\"estado\":\"" + estado + "\"";
  jsonData += "}";

  // 1. Envia para o Monitor Serial USB
  Serial.println(jsonData);

  // 2. Envia por Bluetooth
  btSerial.println(jsonData);

  // Atraso para não sobrecarregar a porta serial
  delay(250);
}
//***************************************************************************