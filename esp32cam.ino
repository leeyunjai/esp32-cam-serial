#include "esp_camera.h"

#define PWDN_GPIO_NUM 32
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

void setup() {
  // 속도를 115200으로 변경
  Serial.begin(115200);
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12; // 품질을 약간 높임 (10~15 권장)
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("ERR:0x%x\n", err);
    while(1);
  }
}

void loop() {
  camera_fb_t *fb = esp_camera_fb_get();
  
  if (fb) {
    // 헤더 5바이트 + 사이즈 4바이트 + 데이터
    // 'S', 'T', 'A', 'R', 'T' 를 바이너리로 직접 전송
    uint8_t header[5] = {'S', 'T', 'A', 'R', 'T'};
    Serial.write(header, 5);
    
    uint32_t size = fb->len;
    Serial.write((uint8_t*)&size, 4);
    
    // 실제 데이터 전송
    Serial.write(fb->buf, fb->len);
    
    esp_camera_fb_return(fb);
    
    // 디버깅용 (파이썬 콘솔에 찍히는지 확인용)
    // Serial.println("DEBUG_SENT"); 
  }
  delay(100); 
}