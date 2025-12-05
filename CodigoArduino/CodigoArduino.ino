/*
 * Sistema de Monitorização de Luminosidade - Firmware Arduino
 * 
 * Hardware necessário:
 *   - Arduino UNO/Nano ou compatível
 *   - Sensor TEMT6000 (sensor de luz ambiente)
 *   - LED indicador (usando LED onboard no pino 13)
 *   
 * Protocolo de comunicação:
 *   - Serial: 9600 baud
 *   - Formato: valor inteiro (0-100) seguido de newline
 *   - Intervalo: 500ms entre leituras
 *   
 * LED Indicador (pino 13):
 *   - Acende quando luz está fora do intervalo normal (30-60%)
 *   - Útil para indicar condições anormais de luminosidade
 */

// ============================================================
// CONFIGURAÇÃO DE PINOS E CONSTANTES
// ============================================================

const int SENSOR_PIN = A0;     // Pino analógico do sensor TEMT6000
const int LED_PIN = 13;        // LED indicador (onboard)
const long INTERVALO = 500;    // Intervalo entre leituras em ms

// Limites para o LED indicador (fora deste intervalo, LED acende)
const int LUZ_MIN_NORMAL = 30;
const int LUZ_MAX_NORMAL = 60;

// Fator de conversão: ADC (0-1023) → Percentagem (0-100)
// 1023 * 0.0976 ≈ 100
const float FATOR_CONVERSAO = 0.0976;

unsigned long tempoAnterior = 0; // Último tempo de leitura (para timing não-bloqueante)
int valorADC = 0;                // Valor raw do ADC (0-1023)
float luzPercentagem = 0;        // Valor convertido em percentagem

// Modo de controlo do LED
// 0 = AUTOMÁTICO (controlado pelo sensor)
// 1 = MANUAL ON (ligado)
// 2 = MANUAL OFF (desligado)
int modoLED = 0;  // Inicia em modo automático

void setup() {
  // Inicializar comunicação serial
  Serial.begin(9600);
  
  // Configurar pinos
  pinMode(SENSOR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Estado inicial do LED: desligado
  digitalWrite(LED_PIN, LOW);
  
  // Pequeno delay para estabilização do sensor
  delay(100);
}

// ============================================================
// LOOP PRINCIPAL
// ============================================================

void loop() {
  // --------------------------------------------------------
  // VERIFICAR COMANDOS RECEBIDOS VIA SERIAL
  // --------------------------------------------------------
  // Verificar se há comandos recebidos do computador
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();  // Remover espaços e newline
    
    // Processar comandos de controlo do LED
    if (comando == "LED:ON") {
      modoLED = 1;  // Modo manual ON
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED_ON ATIVADO");  // Confirmação
    }
    else if (comando == "LED:OFF") {
      modoLED = 2;  // Modo manual OFF
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED_OFF ATIVADO");  // Confirmação
    }
    else if (comando == "LED:AUTO") {
      modoLED = 0;  // Voltar ao modo automático
      Serial.println("LED_AUTO ATIVADO");  // Confirmação
    }
  }
  
  // --------------------------------------------------------
  // LEITURA DO SENSOR E ENVIO DE DADOS
  // --------------------------------------------------------
  unsigned long tempoAtual = millis();
  
  // Verificar se passou o intervalo de tempo (timing não-bloqueante)
  if (tempoAtual - tempoAnterior >= INTERVALO) {
    tempoAnterior = tempoAtual;
    
    // Leitura do sensor
    valorADC = analogRead(SENSOR_PIN);
    luzPercentagem = valorADC * FATOR_CONVERSAO;
    
    // Enviar valor via Serial (sempre, independente do modo do LED)
    Serial.println((int)luzPercentagem);
    
    // --------------------------------------------------------
    // CONTROLO DO LED (conforme o modo)
    // --------------------------------------------------------
    if (modoLED == 0) {
      // MODO AUTOMÁTICO: LED controlado pelo sensor
      if (luzPercentagem < LUZ_MIN_NORMAL || luzPercentagem > LUZ_MAX_NORMAL) {
        digitalWrite(LED_PIN, HIGH); // LED ON: condição anormal
      } else {
        digitalWrite(LED_PIN, LOW);  // LED OFF: condição normal
      }
    }
    // Se modoLED == 1 ou 2, o LED já está configurado pelos comandos acima
    // (mantém o estado manual até novo comando)
  }
}