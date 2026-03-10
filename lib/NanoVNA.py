#ライブラリインポート
import serial
import serial.tools.list_ports
import datetime
import time
import re
import sys
import os

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'../config'))

import config_data as config_data

#処理概要　実数かどうか判定する
#引数　s：判定したい文字列
#戻り値　実数：True、実数以外：False
def isfloat(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

#処理概要　シリアル通信で受信したデータを全て破棄する
#引数　ser_port：シリアルポート、th_to：タイムアウトまでの時間(sec）
#戻り値　なし
def Read_AllDataAndDump(ser_port,th_to):
    tic     = time.time()
    buff    = ser_port.readline()
    # you can use if not ('\n' in buff) too if you don't like re
    while ((time.time() - tic) < -1 * th_to):
       buff += ser.readline()

#処理概要　NanoVNAからTDR波形データを取得する
#戻り値　測定成否（1：失敗、0：成功）、測定データ
def Get_StepResponse():
    try:
        #シリアルポートを開く
        Serial_Port=serial.Serial(port=config_data.DEV_NAME, baudrate=config_data.BAUDRATE, parity= 'N',timeout = 3)

        #dump initial terminal message
        data = "dummy"
        while not (data == "" or data == "ch>"):
            Serial_Port.write('\r\n'.encode('utf-8'))
            data = Serial_Port.readline()
            data = data.strip()
            data = data.decode('utf-8')

        #接続時のレスポンスを読み出して破棄
        data = ""
        Serial_Port.write(('recall ' + str(config_data.RECALL_NO) + '\r\n').encode('utf-8'))
        while data != "ch>":
            data = Serial_Port.readline()
            data = data.strip()
            data = data.decode('utf-8')

        #測定ステータスを失敗として初期化
        status = 1

        #測定データを格納する配列を用意
        result = []
        for i in range(config_data.MEASUREMENT_POINT):
            result.append(99)

        time.sleep(1)	#wait for stabilize
        cnt = 0
        while status == 1:
            #測定コマンド送信
            data = 'data 0\r\n'
            data = data.encode('utf-8')
            Serial_Port.write(data)

            """
            #dump echo back
            data = "dummy"
            while data != "data 0":
                data = Serial_Port.readline()
                data = data.strip()
                data = data.decode('utf-8')
                time.sleep(0.5)
            """

            for i in range(config_data.MEASUREMENT_POINT):
                #測定データを1行分読み出し
                data=Serial_Port.readline()
                data=data.strip()
                data=data.decode('utf-8')
                while isfloat(data) == False:
                    data=Serial_Port.readline()
                    data=data.strip()
                    data=data.decode('utf-8')

                #if data == "":
                #    break

                #測定データが正しいか確認する
                if isfloat(data) == True:
                    if -2 < float(data) and float(data) < 2:
                        result[i] = float(data)

            #測定データの異常チェック
            status = 0
            for i in range(config_data.MEASUREMENT_POINT):
                if result[i] == 99:
                    status = 1
                    break

            cnt += 1

            #異常がありかつ4の倍数回ならリセットかける
            if status == 1:
                print("retry")
                if cnt % 4 == 0:
                    #リセット
                    data = 'reset\r\n'
                    data = data.encode('utf-8')
                    Serial_Port.write(data)

                    data = "dummy"
                    while not (data == "" or data == "ch>"):
                        data = Serial_Port.readline()
                        data=data.strip()
                        data=data.decode('utf-8')

                    time.sleep(3)
                    break

    finally:
        #測定が終了したら切断する
        data = '~.\n'
        data = data.encode('utf-8')
        Serial_Port.write(data)

        if Serial_Port.is_open:
            data = '~.\n'
            data = data.encode('utf-8')
            Serial_Port.write(data)

            Serial_Port.close()

        if status == 1:
            return(1,result)
        else:
            return(0,result)

if __name__ == '__main__':
    ans,data = Get_StepResponse()
    for i in range(config_data.MEASUREMENT_POINT):
        print("data[" + str(i) + "]=" + str(data[i]))

    if ans == 1:
        print("NG")
    else:
        print("OK")
