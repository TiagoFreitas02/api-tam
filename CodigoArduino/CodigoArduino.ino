int temt6000Pin = A0; // Pino analógico do sensor TEMT6000
float light;
int light_value;

unsigned long previousMillis = 0; // Armazena o último tempo de leitura
const long interval = 500; // Intervalo entre leituras (500ms)

void setup() {
  Serial.begin(9600);
  pinMode(temt6000Pin, INPUT);
  pinMode(13, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis(); // Tempo atual
  
  // Verifica se passou o intervalo de tempo
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; // Atualiza o tempo da última leitura
    
    // Leitura do Sensor
    light_value = analogRead(temt6000Pin);
    light = light_value * 0.0976; // Converte para percentagem

    Serial.println((int)light); // envia valor inteiro da luz

    // Ligar ou desligar o LED
    if (light > 60 || light < 30) { 
      digitalWrite(13, HIGH);
    } else {
      digitalWrite(13, LOW);
    }
  }
  

}