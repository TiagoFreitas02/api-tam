
const int SENSOR_PIN = A0;  
const int LED_PIN = 13;        
const long INTERVALO = 500;   

const int LUZ_MIN_NORMAL = 30;
const int LUZ_MAX_NORMAL = 60;

const float FATOR_CONVERSAO = 0.0976;

unsigned long tempoAnterior = 0;
int valorADC = 0;                
float luzPercentagem = 0;        

int modoLED = 0; 

void setup() {
  Serial.begin(9600);
  
  pinMode(SENSOR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  

  digitalWrite(LED_PIN, LOW);
  
  delay(100);
}

void loop() {

  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Remover espaços e newline
    
    // Processar comandos LED
    if (comando == "LED:ON") {
      modoLED = 1;  // Modo manual ON
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED_ON ATIVADO"); 
    }
    else if (comando == "LED:OFF") {
      modoLED = 2;  // Modo manual OFF
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED_OFF ATIVADO"); 
    }
    else if (comando == "LED:AUTO") {
      modoLED = 0;  // Voltar ao modo automático
      Serial.println("LED_AUTO ATIVADO"); 
    }
  }
  
  unsigned long tempoAtual = millis();
  
  if (tempoAtual - tempoAnterior >= INTERVALO) {
    tempoAnterior = tempoAtual;
    
    // Leitura do sensor
    valorADC = analogRead(SENSOR_PIN);
    luzPercentagem = valorADC * FATOR_CONVERSAO;
    
    // Enviar valor via Serial
    Serial.println((int)luzPercentagem);
    
    if (modoLED == 0) {
      if (luzPercentagem < LUZ_MIN_NORMAL || luzPercentagem > LUZ_MAX_NORMAL) {
        digitalWrite(LED_PIN, HIGH); 
      } else {
        digitalWrite(LED_PIN, LOW); 
      }
    }

  }
}