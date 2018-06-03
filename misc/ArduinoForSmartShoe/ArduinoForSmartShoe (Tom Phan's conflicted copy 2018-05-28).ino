volatile uint16_t instantRead = 0;
volatile uint16_t tmpUInt = 0;
byte pendingBytes[17] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,13};
volatile uint8_t currentAnalogChannel = 0;
volatile uint8_t tmpUShort = 0;

void setup() { 
  
  cli();//stop interrupts
  
  //Initialize ADC 
  ADMUX = 0;
  ADCSRA = 0b10001111;//ADEN|ADIE|XTAL/128
  //Initialize TMR1
  TCCR1A &= 0b00001100;
  TCCR1B &= 0b00101000;
  TCCR1B |= 0b00001000;
  TIMSK1 &= 0b11011010;
  TIMSK1 |= 0b00000010;
  OCR1A = 19999;
  TCNT1 = 0;
  //Initialize TMR2
  TCCR2A &= 0b00001110;
  TCCR2A |= 0b00000010;
  TCCR2B &= 0b00110000;
  TIMSK2 &= 0b11111010;
  TIMSK2 |= 0b00000010;
  OCR2A = 124;
  TCNT2 = 0;
  sei();//enable interrupts
  
  Serial.begin(250000);  

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }

  pinMode(9,OUTPUT);
  digitalWrite(9,LOW);
  startTMR1();
}

ISR(TIMER1_COMPA_vect) {  
  startTMR2();
}

ISR(TIMER2_COMPA_vect) {  
  digitalWrite(9,HIGH);
  ADMUX = (ADMUX & 0xF8)|currentAnalogChannel;
  ADCSRA |= 0b01000000;
  ++currentAnalogChannel;
}

ISR(ADC_vect){
  instantRead = ADCL | (ADCH << 8);
  tmpUInt = instantRead/43;
  pendingBytes[tmpUShort] = byte(tmpUInt + 48);
  pendingBytes[++tmpUShort] = byte(instantRead - tmpUInt*43 + 48);
  ++tmpUShort;
  if (currentAnalogChannel > 7) {
    stopTMR2();
  }
  digitalWrite(9,LOW);
}

void startTMR1() {
  TCCR1B |= 0b00000010;
}

void stopTMR1() {
  TCCR1B &= 0b11111000;
  TCNT1 = 0;
}

void startTMR2() {
  TCCR2B |= 0b00000011;
}

void stopTMR2() {
  TCCR2B &= 0x11111000;
  TCNT2 = 0;
  currentAnalogChannel = 0;
  tmpUShort = 0;
  Serial.write(pendingBytes,17);
}

void loop() {

}
