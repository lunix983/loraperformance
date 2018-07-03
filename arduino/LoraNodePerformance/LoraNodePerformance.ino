#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <SPI.h>
#include <RH_RF95.h>
#include <DHT.h>
#include <TrueRandom.h>



RH_RF95 rf95;
TinyGPS gps;

int nodeID = 52;
float frequency = 868.0;
int count = 0;
float flat, flon;
unsigned long age;
SoftwareSerial ss(3, 4); 
int loraSetup = 1;

#define DHTPIN 7
#define DHTTYPE DHT11
//#define dht_dpin A0 // Use A0 pin as Data pin for DHT11. 
int dht_dpin = 7;
DHT dht(DHTPIN, DHTTYPE);
long expid; 
int txpower = 13;


struct message{
  int idnode;
  unsigned long experimentid;
  int sequencenum;
  unsigned long time;
  int snr;
  int rssi;
  float lat;
  float lon;
  float delay;
  int status;
  float umidity;
  float temp;
  int lorasetup;
  int txpower;
}data, datarcv;

byte tx_buf[sizeof(data)] = {0};


void setup()
{
  Serial.begin(9600);  // Serial to print out GPS info in Arduino IDE
  ss.begin(9600); // SoftSerial port to get GPS data. 
  while (!Serial) {
     ;
  };

  Serial.println("Progetto Tesi Lunix. Lora Node performance Signal measurement.");
  if (!rf95.init())
  {
        Serial.println("RF95 init failed");
  }
  else 
  {
       Serial.println("RF95 init done.");
  }
  setLoraSetup();
  Serial.print("LoRa End Node ID: "); Serial.println(nodeID);
  
  Serial.print("Exp ID: "); Serial.println(expid);
  data.idnode = nodeID;
  data.experimentid = customRandom();  
  data.lorasetup = loraSetup;
  data.txpower = txpower;
  
  
} // end setup



// SMART DELAY
static void smartdelay(unsigned long ms)
{
  Serial.println("... smartdelay ...");
  unsigned long start = millis();
  do 
  {
    while (ss.available())
    {
      //ss.print(Serial.read());
      gps.encode(ss.read());
    }
  } while (millis() - start < ms);
}


void printData(){
  Serial.print("SEQUENCE: ");  Serial.println(data.sequencenum );
  Serial.print("EXPERIMENT-ID: ");  Serial.println(data.experimentid);
  Serial.print("MILLIS: ");  Serial.println(data.time );
  Serial.print("LAT: ");  Serial.println(data.lat, 6);
  Serial.print("LON: ");  Serial.println(data.lon, 6);
  Serial.print("RSSI: ");  Serial.println(data.rssi);
  Serial.print("SNR: ");  Serial.println(data.snr);
  Serial.print("DELAY: ");  Serial.println(data.delay );
  Serial.print("TEMP: ");  Serial.println(data.temp );
  Serial.print("UMIDITY: ");  Serial.println(data.umidity );
  Serial.print("LORA SETUP: ");  Serial.println(data.lorasetup);
  Serial.print("TX POWER : ");  Serial.println(data.txpower);
  //Serial.print();  Serial.println();
 
}

unsigned long customRandom(){
  int i;
  unsigned long uuid  = TrueRandom.random(1000);
  for (int i=0; i<3; i++)
  {  
    uuid = uuid * TrueRandom.random(100);
  }
  return uuid;
}

void setLoraSetup(){
  // Setup ISM frequency
  rf95.setFrequency(frequency);
  // Setup Power,dBm
  rf95.setTxPower(txpower);
        switch (loraSetup) {
          case 1:
            rf95.setSignalBandwidth(125000);
            rf95.setCodingRate4(5);
            rf95.setSpreadingFactor(7);
            Serial.println("Lora setup 1");
            break;
          case 2:
            rf95.setSignalBandwidth(500000);
            rf95.setCodingRate4(5);
            rf95.setSpreadingFactor(7);
            Serial.println("Lora setup 2");
            break;
          case 3:
            rf95.setSignalBandwidth(31250);
            rf95.setCodingRate4(8);
            rf95.setSpreadingFactor(9);
            Serial.println("Lora setup 3");
            break;
          case 4:
            rf95.setSignalBandwidth(125000);
            rf95.setCodingRate4(8);
            rf95.setSpreadingFactor(12); 
            Serial.println("Lora setup 4");
            break;
        }
}


void loop()
{ 

  int j;
 
  
  
  gps.f_get_position(&flat, &flon, &age);
  pinMode(dht_dpin,OUTPUT);//Set A0 to output
  digitalWrite(dht_dpin,HIGH);//Pull high A0
  
  smartdelay(500);
  
  data.umidity = dht.readHumidity(); // Read temperature Humidity
  data.temp = dht.readTemperature(); // Read temperature as Celsius (the default)
  //data.idnode = nodeID;
  data.sequencenum = count;
  data.lat = flat;
  data.lon = flon;
  data.time = millis();
  data.rssi = rf95.lastRssi();
  data.snr = rf95.lastSNR();
  printData();
  memcpy(tx_buf, &data, sizeof(data) );

  Serial.print("DATA SIZE:"); Serial.println(sizeof(data)); 
  rf95.send((uint8_t *)tx_buf, sizeof(data));

  rf95.waitPacketSent();
    // Now wait for a reply
  uint8_t rx_buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(rx_buf);


  if (rf95.waitAvailableTimeout(3000))
  {
      if (rf95.recv(rx_buf, &len))
      {
        memcpy(&datarcv, rx_buf, sizeof(datarcv)); 
        data.delay = (float)(millis() - datarcv.time) /2 ;
        if (datarcv.status == 1){
          Serial.print("Message from gateway: ");  Serial.println(datarcv.status);
          Serial.print("SEQUENCE REPLAY: ");  Serial.println(datarcv.sequencenum );
          Serial.print("TIME REPLAY: ");  Serial.println(datarcv.time );
          Serial.print("DELAY REPLAY: ");  Serial.println(datarcv.delay );          
        }
         
        
      }
      else
      {
         Serial.println("recv failed");
      }
           
  } // end if waitAvailableTimeout
  else
  {
    Serial.println("No reply, is LoraGateway running?");
  }
 
  count++;
  delay(3000);
  Serial.println("-------------------------------------");
} // end loop

