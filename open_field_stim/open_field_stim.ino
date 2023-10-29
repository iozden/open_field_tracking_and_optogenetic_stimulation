
float freq=20;
float pulse_dur=1/freq/2;
float pulse_int=1/freq;
int command;

void setup() {
    pmc_enable_periph_clk(35); //pin 11
    pmc_enable_periph_clk(TC8_IRQn);
    REG_PMC_PCER1 |= PMC_PCER1_PID35;                
    REG_PIOD_ABSR |= PIO_ABSR_P7;     
    REG_PIOD_PDR |= PIO_PDR_P7;          
    TC_Configure(TC2,2,TC_CMR_WAVE | TC_CMR_WAVSEL_UP_RC | TC_CMR_ACPA_CLEAR | TC_CMR_ACPC_SET | TC_CMR_ASWTRG_SET | TC_CMR_TCCLKS_TIMER_CLOCK1);  
    TC_SetRC(TC2,2, VARIANT_MCK/2/freq);
    TC_SetRA(TC2,2,VARIANT_MCK/2*pulse_dur);   

  Serial.begin(115200);
}

void loop() {
  command=Serial.read();
  if (command==49){
    TC2->TC_CHANNEL[2].TC_IER=TC_IER_CPCS;
    TC2->TC_CHANNEL[2].TC_IDR=~TC_IER_CPCS;
    NVIC_EnableIRQ(TC8_IRQn);
    TC2->TC_CHANNEL[2].TC_CCR = TC_CCR_CLKEN | TC_CCR_SWTRG;    
  }
  if (command==48){
    int pulsedur=VARIANT_MCK/2*pulse_dur;
    if (TC2->TC_CHANNEL[2].TC_CV<=pulsedur){TC2->TC_CHANNEL[2].TC_RA=TC2->TC_CHANNEL[2].TC_CV+10;}
    //while (TC2->TC_CHANNEL[2].TC_CV<=pulsedur) {} 
    TC_Stop(TC2,2);  
    NVIC_DisableIRQ(TC8_IRQn);
    //TC2->TC_CHANNEL[2].TC_IDR=TC_IER_CPCS;  // disable interrupt
    TC_GetStatus(TC2, 2);
    TC2->TC_CHANNEL[2].TC_RA=pulsedur;
  }
  
}

void TC8_Handler()
{
  TC_GetStatus(TC2, 2);
}
