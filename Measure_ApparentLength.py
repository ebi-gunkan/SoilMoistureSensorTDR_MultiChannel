#ライブラリのインポート
import os
import sys
import datetime
import numpy as np
import csv
import subprocess
import time

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./lib'))
sys.path.append(os.path.join(os.path.dirname(__file__),'./config'))

#自作ライブラリのインポート
import SoilMoisture as soil_moisture
import config_data as config_data

#定数の定義
STATUS_OK = 0
STATUS_NG = 1
C_SPEED = config_data.C_SPEED
MEASUREMENT_POINT = 101

#距離データの取得
def Get_DistanceData():
    f = open("./distance_data/distance_domain.csv","r")
    temp = csv.reader(f,delimiter = ",")

    distance_data = []
    for row in temp:
        if row[0] != "":
            distance_data.append(float(row[0]))
    f.close()

    return(distance_data)

#処理概要　土壌表面からの反射波の到達時刻（ns）を取得
#引数　distance_data；時間軸データ、waveform_data：波形データ
#戻り値　土壌水分の範囲、反射波の到達時刻配列（リスト型）
def Detect_SoilSurfaceReflect(distance_data,waveform_data):
    #反射係数の勾配を求める
    gradient = []
    i = 1
    while i <= MEASUREMENT_POINT -2:
        temp_x_array = [distance_data[i-1],distance_data[i],distance_data[i+1]]
        temp_y_array = [waveform_data[i-1],waveform_data[i],waveform_data[i+1]]
        a,b = np.polyfit(temp_x_array,temp_y_array,1)

        gradient.append(a)
        i += 1

    #detect minimum data after soil surface reflect
    temp = waveform_data[12]
    t_min = 12
    i = 13
    while i <= MEASUREMENT_POINT - 1:
        if temp > waveform_data[i]:
            temp = waveform_data[i]
            t_min = i
        i += 1

    #detect A-point
    temp = gradient[0]
    i = 1
    t_A = 1
    while i < t_min:
        if temp < gradient[i]:
            temp = gradient[i]
            t_A = i+1
        i += 1

    #detect B-point
    temp = gradient[0]
    i = t_A
    t_B = i
    while i < t_min:
        if temp > gradient[i]:
            temp = gradient[i]
            t_B = i+1
        i += 1

    #calc tangent-line at t_A
    temp_x_array = [distance_data[t_A-1],distance_data[t_A],distance_data[t_A+1]]
    temp_y_array = [waveform_data[t_A-1],waveform_data[t_A],waveform_data[t_A+1]]
    slope_A,intercept_A = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_A = waveform_data[t_A] - slope_A * distance_data[t_A]

    #calc tangent-line at t_B
    temp_x_array = [distance_data[t_B-1],distance_data[t_B],distance_data[t_B+1]]
    temp_y_array = [waveform_data[t_B-1],waveform_data[t_B],waveform_data[t_B+1]]
    slope_B,intercept_B = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_B = waveform_data[t_B] - slope_B * distance_data[t_B]

    soil_surface_reflect = (intercept_B - intercept_A) / (slope_A - slope_B)
    return soil_surface_reflect

#処理概要　プローブ終端からの反射波の到達時刻（ns）を取得
#引数　distance_data；時間軸データ、waveform_data：波形データ、peak_time_end：土壌表面からの反射波の到達時刻の終わり、theta_range：土壌水分の範囲
#戻り値　反射波の到達時刻配列（リスト型）
def Detect_ProbeEndReflect(distance_data,waveform_data):
    #反射係数の勾配を求める
    gradient = []
    i = 1
    while i <= MEASUREMENT_POINT -2:
        temp_x_array = [distance_data[i-1],distance_data[i],distance_data[i+1]]
        temp_y_array = [waveform_data[i-1],waveform_data[i],waveform_data[i+1]]
        a,b = np.polyfit(temp_x_array,temp_y_array,1)

        gradient.append(a)
        i += 1

    #detect minimum data after soil surface reflect
    temp = waveform_data[12]
    t_min = 12
    i = 13
    while i <= MEASUREMENT_POINT - 1:
        if temp > waveform_data[i]:
            temp = waveform_data[i]
            t_min = i
        i += 1

    #get C-point
    t_C = t_min
    slope_C = 0
    intercept_C = waveform_data[t_C]

    #get D-point
    temp = gradient[t_C-1]
    i = t_C
    t_D = t_C + 1
    while i < MEASUREMENT_POINT - 2:
        if temp < gradient[i]:
            temp = gradient[i]
            t_D = i+1
        i += 1

    #calc tangent-line at t_D
    temp_x_array = [distance_data[t_D-1],distance_data[t_D],distance_data[t_D+1]]
    temp_y_array = [waveform_data[t_D-1],waveform_data[t_D],waveform_data[t_D+1]]
    slope_D,intercept_D = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_D = waveform_data[t_D] - slope_D * distance_data[t_D]

    probe_end_reflect = (intercept_D - intercept_C) / (slope_C - slope_D)

    return probe_end_reflect

#処理概要　伝搬時間tを取得
#引数　distance_data；時間軸データ、waveform_data：波形データ
#戻り値　測定成否、土壌表面からの反射波の到達時刻、プローブ終端からの反射波の到達時刻、伝搬時間(ns)
def Get_Distance(distance_data,waveform_data):
    #土壌表面からの反射波の到達時刻を取得
    soil_surface_reflect = Detect_SoilSurfaceReflect(distance_data,waveform_data)

    #プローブ終端からの反射波の到達時刻を取得
    probe_end_reflect = Detect_ProbeEndReflect(distance_data,waveform_data)

    #calc t
    t = probe_end_reflect - soil_surface_reflect

    return soil_surface_reflect,probe_end_reflect,t

#処理概要　比誘電率を計算
#引数　なし
#戻り値　なし
def Calc_ApparentLength(measured_data):
    #時間軸データ一覧を取得
    distance_data = Get_DistanceData()

    #伝搬時間tを計算
    soil_surface_reflect,probe_end_reflect,t = Get_Distance(distance_data,measured_data)

    #反射位置の特定
    soil_surface_reflect = str(soil_surface_reflect)
    probe_end_reflect = str(probe_end_reflect)

    print("distance to soil surface:" + str(soil_surface_reflect) + " (mm)")
    print("distance to probe end:" + str(probe_end_reflect) +  " (mm)")
    print("distance to probe end:" + str(t) +  " (mm)")

#処理概要　測定実行
#引数　data_point：測定点数
#戻り値　測定成否（0：成功、1：失敗）
def Execute():
    #土壌水分の測定
    ans = 1
    while (ans != 0):
        print("measuring step response...")
        reuslt = subprocess.run(['sudo','chmod','666','/dev/ttyACM0'])
        time.sleep(2)
        ans,temp_array = soil_moisture.Get_SoilMoisture()

    measured_data=[]
    for i in range(101):
        measured_data.append(temp_array[i][0])

    Calc_ApparentLength(measured_data)
    return(ans)

if __name__ == '__main__':
    try:
        ans = Execute()
    except KeyboardInterrupt:
        pass

