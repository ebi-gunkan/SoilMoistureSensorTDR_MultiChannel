# -*- coding: utf-8 -*-

#ライブラリのインポート
import os
import sys
import datetime
import RPi.GPIO as GPIO
import time

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./lib'))
sys.path.append(os.path.join(os.path.dirname(__file__),'./config'))

#自作ライブラリのインポート
import NanoVNA as nanovna
import config_data as config_data

#RFスイッチモジュールのセレクタ
SELECTOR_C = 14		#bit2
SELECTOR_B = 15		#bit1
SELECTOR_A = 18		#bit0

def Initialize_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SELECTOR_C,GPIO.OUT)
    GPIO.setup(SELECTOR_B,GPIO.OUT)
    GPIO.setup(SELECTOR_A,GPIO.OUT)

    GPIO.output(SELECTOR_C,0)
    GPIO.output(SELECTOR_B,0)
    GPIO.output(SELECTOR_A,0)

def Control_ChSelector(ch):
    GPIO.output(SELECTOR_C,(ch >> 2) & 0x01)
    GPIO.output(SELECTOR_B,(ch >> 1) & 0x01)
    GPIO.output(SELECTOR_A,ch & 0x01)

#処理概要　測定データをテキストファイルに書き出す
#引数　measured_data：測定データ、data_point：測定点数
#戻り値　なし
def Record_MeasurementData(ch,measured_data,file_name):
    data_point = config_data.MEASUREMENT_POINT

    #ファイルがなければ新規作成
    if not os.path.isfile("./raw_data/" + file_name):
        f = open("./raw_data/" + file_name,"w")
        f.write("date,t(ns)\r\n")
        f.close()

    #書き込みデータを作成
    now = datetime.datetime.now()
    f = open("./raw_data/" + file_name,"a")
    f.write(now.strftime('%04Y/%m/%d %H:%M:%S') + str("\n"))
    for i in range(len(measured_data)):
        f.write(str(measured_data[i]) + "\n")
    f.close()

#処理概要　測定実行
#引数　data_point：測定点数
#戻り値　測定成否（0：成功、1：失敗）
def Execute():
    Initialize_GPIO()

    #書き込み先のファイル名を取得（chX_yyyymmddhh00.txt）
    now = datetime.datetime.now()
    file_name_base = "_" \
                + format(now.year,"#04d") \
                + format(now.month,"#02d") \
                + format(now.day,"#02d") + "_" \
                + format(now.hour,"#02d") \
                + format(now.minute,"#02d") + ".txt"

    #8ch分測定を実施
    ans = 0
    for ch in range(8):
        #測定開始通知
        print("ch" + format(ch,"#01d") + ":measurement start")

        #RFスイッチモジュールのセレクタ制御
        Control_ChSelector(ch)
        time.sleep(2)

        #ステップ応答の測定
        temp,step_response = nanovna.Get_StepResponse()
        ans = ans + temp
        if temp == 0:
            #ステップ応答の記録
            file_name = "ch" + format(ch,"#01d") + file_name_base
            Record_MeasurementData(ch,step_response,file_name)

        #測定終了通知
        print("ch" + format(ch,"#01d") + ":measurement finish")

    GPIO.cleanup()

    return(ans)

if __name__ == '__main__':
    try:
        ans = Execute()
        sys.stdout.write(str(ans))
    except KeyboardInterrupt:
        pass
