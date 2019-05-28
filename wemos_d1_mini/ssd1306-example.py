import ssd1306
from machine import I2C, Pin

i2c = I2C(-1, Pin(5), Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

oled.text("E185/185 B60/60", 1, 1, 1)
oled.text("X164 Y168 Z045.9", 1, 9, 1)
oled.text("F100% P30% 03:55", 1, 17, 1)
oled.text("Heating done.", 1, 25, 1)
oled.contrast(0)
oled.show()