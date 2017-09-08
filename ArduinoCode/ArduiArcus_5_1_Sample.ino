#define READ_SIZE 16
#define REBOUND_STEPS 1000
#define USE_LIMIT_SWITCH 0
#define DEVICE_NAME "sample"
// #define MS1 6
// #define MS2 7
// #define MS3 8
// #define sleepPin 10
// #define resetPin 9
// #define enablePin 5

const int stepPin = 12; //FORGOT CORRECT PINS
const int dirPin = 11; //FORGOT CORRECT PINS
const int limPinPlus = 4;
const int limPinMinus = 5;

char incomingCmd[READ_SIZE];
char currentcmd[READ_SIZE];
char currentcmdnum[READ_SIZE];

int jogging = 0;
long px = 0;
int moving = 0;
long pxreq = 0;
unsigned int delaytime = 250;
int movdir = 0;
int jogdir = 0;
float spd = 0;

void setup() {
        Serial.begin(57600);     // opens serial port, sets data rate to 9600 bps
        Serial.setTimeout(2);
        pinMode(stepPin,OUTPUT); 
        pinMode(dirPin,OUTPUT);
        pinMode(limPinPlus,INPUT);
        pinMode(limPinMinus,INPUT);
        // pinMode(MS1,OUTPUT);
        // pinMode(MS2,OUTPUT);
        // pinMode(MS3,OUTPUT);
        // pinMode(sleepPin,OUTPUT);
        // pinMode(resetPin,OUTPUT);
        // pinMode(enablePin,OUTPUT);
        
        // digitalWrite(MS1,HIGH);
        // digitalWrite(MS2,HIGH);
        // digitalWrite(MS3,HIGH);
        // digitalWrite(enablePin,LOW);
        // digitalWrite(resetPin,HIGH);
        // digitalWrite(sleepPin,HIGH);
}

void loop() {
  //Read and parse incoming cmd str
  if (Serial.available() > 0) {
    Serial.readBytes(incomingCmd,READ_SIZE);
    parseCmdStr(incomingCmd);
  };

  //Use parsed cmd string and number to decide action:
  if (strcmp(currentcmd,"J+")==0){
    jogging = 1;
    moving = 1;
    jogdir = 1;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"J-")==0){
    jogging = 1;
    moving = 1;
    jogdir = -1;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"PX")==0){
    Serial.println(px);
  }
  else if (strcmp(currentcmd,"PX=")==0){
    px = atol(currentcmdnum);
    pxreq = px;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"L+")==0){
    // Serial.println("L+ cmd not yet implemented");
    jogging = 1;
    jogdir = 1;
    moving = 1;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"L-")==0){
    // Serial.println("L- cmd not yet implemented");s
    jogging = 1;
    jogdir = -1;
    moving = 1;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"STOP")==0){
    jogging = 0;
    moving = 0;
    pxreq = px;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"X")==0){
    pxreq = atol(currentcmdnum);
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"SSPD")==0){
    float delayfloat;
    delayfloat = (float) delaytime;
    float s;
    s = 1000000/2/delayfloat;
    Serial.println(s);
  }
  else if (strcmp(currentcmd,"SSPD=")==0){
    spd = atof(currentcmdnum);
    float delayfloat;
    delayfloat = 1000000/spd/2;
    delaytime = (unsigned int) delayfloat;
    Serial.println("OK");
  }
  else if (strcmp(currentcmd,"DN")==0){
    Serial.println(DEVICE_NAME);
  }

  //Depending on status of jogging,moving,direction variables, do movements:
    if(jogging == 1){
      if(USE_LIMIT_SWITCH ==1){checkLimitSwitches();}
        singleStep(jogdir);
        px+=jogdir;
        pxreq+=jogdir;
    }
    if(moving != 0){
      if(USE_LIMIT_SWITCH ==1){checkLimitSwitches();}
      if(px != pxreq){
        if(px < pxreq){
          singleStep(+1);
          px++;
        }
        else if(px > pxreq){
          singleStep(-1);
          px--;
        }
        else if(px == pxreq){
          moving = 0;
          movdir = 0;
        }
      };
    }
    else if (moving == 0){
      if(USE_LIMIT_SWITCH ==1){checkLimitSwitches();}
      if(px != pxreq){
        moving = 1;
      }
    }
  // }
  // else{
  //   for(int s = 0;s < REBOUND_STEPS;s++){
  //     singleStep(-1);
  //   }
  //   px=0;
  //   moving=0;
  //   jogging=0;
  // }

  memset(currentcmd, 0, READ_SIZE);
  memset(currentcmdnum, 0, READ_SIZE);
  memset(incomingCmd, 0, READ_SIZE);
}

void singleStep(int dir){
  if(movdir != dir){
    if(dir == 1){
     digitalWrite(dirPin,HIGH);
     delayMicroseconds(delaytime);
     movdir = 1;
    }
    else if (dir == -1){
     digitalWrite(dirPin,LOW);
     delayMicroseconds(delaytime);
     movdir = -1;
    }
  };
  digitalWrite(stepPin,HIGH);
  delayMicroseconds(delaytime);
  digitalWrite(stepPin,LOW);
  delayMicroseconds(delaytime);
}


void checkLimitSwitches(){
  if(digitalRead(limPinPlus) != 1 || digitalRead(limPinMinus) != 1){
    int rebound;
    while (digitalRead(limPinPlus) == 0 && digitalRead(limPinMinus) == 1){
      singleStep(-1);
      rebound = -1*REBOUND_STEPS;
    }
    while (digitalRead(limPinPlus) == 1 && digitalRead(limPinMinus) == 0){
      singleStep(+1);
      rebound = 1*REBOUND_STEPS;
    }
    if (digitalRead(limPinPlus) == 0 && digitalRead(limPinMinus) == 0){
      Serial.println("Limit Switch Error: both limits tripped!");
      rebound = 0;
    }
    px=0;
    moving=0;
    jogging=0;
    pxreq=rebound;
  }
}

void parseCmdStr(char *cmd){
  int i=0;
  while (isalpha(cmd[i])){
    i++;
  }
  if(cmd[0]!='X'){
    if(cmd[i]=='+'||cmd[i]=='-'||cmd[i]=='='){
      i++;
    }
  }
  strncpy(currentcmd,incomingCmd,i);
  strncpy(currentcmdnum,incomingCmd+i,READ_SIZE-i);
}