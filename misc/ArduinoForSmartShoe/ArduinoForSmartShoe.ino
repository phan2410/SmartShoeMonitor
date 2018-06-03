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
  OCR2A = 71;
  TCNT2 = 0;
  sei();//enable interrupts
  Serial.begin(250000);
  while (!Serial);//waiting for serial initialization
  pinMode(LED_BUILTIN, OUTPUT);
}

ISR(TIMER1_COMPA_vect) {  
  TCCR2B |= 0b00000011;//start TMR2
}

ISR(TIMER2_COMPA_vect) {  
  ADMUX = (ADMUX & 0xF8)|currentAnalogChannel;
  ADCSRA |= 0b01000000;//start ADC conversion
  if (++currentAnalogChannel == 8) {
    TCCR2B &= 0x11111000;//stop TMR2
    TCNT2 = 0;
  }
}

ISR(ADC_vect) {
  instantRead = ADCL | (ADCH << 8);
  tmpUInt = instantRead/43;
  pendingBytes[tmpUShort] = byte(tmpUInt + 48);
  pendingBytes[++tmpUShort] = byte(instantRead - tmpUInt*43 + 48);
  ++tmpUShort;
  if (currentAnalogChannel == 8) {
    Serial.write(pendingBytes,17);
    currentAnalogChannel = 0;
    tmpUShort = 0;    
  }
}

void startTMR1() {
  TCCR1B |= 0b00000010;
}

void stopTMR1() {
  TCCR1B &= 0b11111000;
  TCNT1 = 0;
}

void loop() {
  if (Serial.available() != 0) {
    incomingByte = Serial.read();
    if (isBeingCommanded) {
      ++NumOfCommandBytes;
    }
    if (incomingByte == 54) {
      isBeingCommanded = true;
      NumOfCommandBytes = 1;      
    } else if (incomingByte == 99) {
      if (NumOfCommandBytes == 3) {
        if (stateCode == 9) {
          stopTMR1();
          LedOnMSec = 9;
          LedOffMSec = 567;
        } else if (stateCode == 18) {
          stopTMR1();
          LedOnMSec = 180;
          LedOffMSec = 180;
        } else if (stateCode == 27) {
          startTMR1();
          LedOnMSec = 45;
          LedOffMSec = 45;        
        } else if (stateCode == 36) {
          stopTMR1();
          LedOnMSec = 0;
          LedOffMSec = 0;          
        } 
      }
      isBeingCommanded = false;
    } else {
      stateCode = incomingByte;
    }
  } 
  if (LedOnMSec) {
    LedState = !LedState;
    digitalWrite(LED_BUILTIN, LedState);
    if (LedState) {
      delay(LedOnMSec);
    } else {
      delay(LedOffMSec);
    }
  }
}
