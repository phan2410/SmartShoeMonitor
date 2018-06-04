volatile uint16_t instantRead = 0;
volatile uint16_t tmpUInt = 0;
byte pendingBytes[17] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,13};
volatile uint8_t currentAnalogChannel = 0;
volatile uint8_t tmpUShort = 0;
bool LedState = HIGH;
uint16_t LedOnMSec = 0;
uint16_t LedOffMSec = 0;
int incomingByte;
int stateCode;
bool isBeingCommanded = false;
uint8_t NumOfCommandBytes = 0;

void setup() {   
  cli();//stop interrupts  
  //Initialize ADC 
  ADMUX = 0;
  ADCSRB &= 0b11111000;//ADC Free Running Mode
  ADCSRA &= 0xF8;
  ADCSRA |= 0b10000100;//ADEN|XTAL/16
  //Initialize TMR1
  TCCR1A &= 0b00001100;
  TCCR1B &= 0b00101000;
  TCCR1B |= 0b00001000;
  TIMSK1 &= 0b11011010;
  TIMSK1 |= 0b00000010;
  OCR1A = 19999;
  TCNT1 = 0;
  sei();//enable interrupts
  Serial.begin(250000);
  while (!Serial);//waiting for serial initialization
  pinMode(9,OUTPUT);
  pinMode(10,OUTPUT);
  digitalWrite(9,LOW);
  digitalWrite(10,LOW);
  startTMR1();
}

ISR(TIMER1_COMPA_vect) {  
  ADCSRA |= 0b01111000;//ADSC|ADATE|ADIF|ADIE
}

ISR(ADC_vect) {
  digitalWrite(10,HIGH);
  instantRead = ADCL | (ADCH << 8);
  ADMUX = (ADMUX & 0xF8)|((++currentAnalogChannel) & 0x07);
  tmpUInt = instantRead/43;
  pendingBytes[tmpUShort] = byte(tmpUInt + 48);
  pendingBytes[++tmpUShort] = byte(instantRead - tmpUInt*43 + 48);
  ++tmpUShort;
  if (currentAnalogChannel == 8) {
    ADCSRA &= 0b10010111;//ADSC|ADATE|ADIE
    Serial.write(pendingBytes,17);
    currentAnalogChannel = 0;
    tmpUShort = 0; 
  }  
  digitalWrite(10,LOW);
}

void startTMR1() {
  TCCR1B |= 0b00000010;
}

void stopTMR1() {
  TCCR1B &= 0b11111000;
  TCNT1 = 0;
}

void loop() {

}
