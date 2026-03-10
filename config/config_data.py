START_FREQ = 50000                   #NanoVNAのSTART周波数:50kHz
STOP_FREQ = 1000000000               #NanoVNAのSTOP周波数:1GHz
MEASUREMENT_POINT = 101              #NanoVNAの測定点数：51
RECALL_NO = 3                        #NanoVNAのキャリブレーションデータ番号：0
DEV_NAME = '/dev/ttyACM0'            #ラズパイ側で認識されるNanoVNAのデバイス名
BAUDRATE = 57600                     #NanoVNAとの通信におけるボーレート
C_SPEED = 299792458                  #光速（m/s）
PROBE_LENGTH = 118 /1000              #プローブ長(m)

if __name__ == '__main__':
    pass
