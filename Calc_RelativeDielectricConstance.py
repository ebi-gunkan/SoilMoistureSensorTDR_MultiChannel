#ライブラリのインポート
import os
import sys
import datetime
import csv
import glob
import numpy as np

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./config'))

#自作ライブラリのインポート
import config_data as config_data

#定数の定義（configファイルからの読み込み）
C_SPEED = config_data.C_SPEED
PROBE_LENGTH = config_data.PROBE_LENGTH
MEASUREMENT_POINT = config_data.MEASUREMENT_POINT

#処理概要　時間軸データが格納されたCSVファイルから読み出して配列に格納
#引数　measurement_point：測定点数
#戻り値　時間軸データ配列（リスト型）
def Get_TimeDomainData(measurement_point):
    f = open("./time_domain_data/time_domain.csv","r")
    temp = csv.reader(f,delimiter = ",")

    time_domain_data = []
    for row in temp:
        if row[0] != "":
            time_domain_data.append(float(row[0]))
    f.close()

    return(time_domain_data)

#処理概要　測定した波形データが格納されたファイルから読み出して配列に格納
#引数　file_name：ファイル名
#戻り値　測定日時、波形データ配列（リスト型）
def Get_WaveFormDataArray(file_name):
    #時間軸データ読み出し
    f = open(file_name,"r")
    data = f.readlines()
    f.close()

    #日時データ読み出し
    datetime_data = data[1].replace("\n","")
    datetime_data = datetime_data.replace("/","-")
    datetime_data = datetime.datetime.strptime(datetime_data,'%Y-%m-%d %H:%M:%S')

    #波形データ読み出し
    waveform_data = []
    for i in range(len(data)-2):
        waveform_data.append(0)
        waveform_data[i] = data[i+2].replace('\n','')
    return(datetime_data,waveform_data)

#処理概要　土壌表面からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　土壌水分の範囲、反射波の到達時刻配列（リスト型）
def Detect_SoilSurfaceReflect(time_domain_data,waveform_data):
    #反射係数の勾配を求める
    gradient = []
    i = 1
    while i <= MEASUREMENT_POINT -2:
        temp_x_array = [time_domain_data[i-1],time_domain_data[i],time_domain_data[i+1]]
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
    temp_x_array = [time_domain_data[t_A-1],time_domain_data[t_A],time_domain_data[t_A+1]]
    temp_y_array = [waveform_data[t_A-1],waveform_data[t_A],waveform_data[t_A+1]]
    slope_A,intercept_A = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_A = waveform_data[t_A] - slope_A * time_domain_data[t_A]

    #calc tangent-line at t_B
    temp_x_array = [time_domain_data[t_B-1],time_domain_data[t_B],time_domain_data[t_B+1]]
    temp_y_array = [waveform_data[t_B-1],waveform_data[t_B],waveform_data[t_B+1]]
    slope_B,intercept_B = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_B = waveform_data[t_B] - slope_B * time_domain_data[t_B]

    soil_surface_reflect = (intercept_B - intercept_A) / (slope_A - slope_B)
    return soil_surface_reflect

#処理概要　プローブ終端からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ、peak_time_end：土壌表面からの反射波の到達時刻の終わり、theta_range：土壌水分の範囲
#戻り値　反射波の到達時刻配列（リスト型）
def Detect_ProbeEndReflect(time_domain_data,waveform_data):
    #反射係数の勾配を求める
    gradient = []
    i = 1
    while i <= MEASUREMENT_POINT -2:
        temp_x_array = [time_domain_data[i-1],time_domain_data[i],time_domain_data[i+1]]
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
    temp_x_array = [time_domain_data[t_D-1],time_domain_data[t_D],time_domain_data[t_D+1]]
    temp_y_array = [waveform_data[t_D-1],waveform_data[t_D],waveform_data[t_D+1]]
    slope_D,intercept_D = np.polyfit(temp_x_array,temp_y_array,1)
    intercept_D = waveform_data[t_D] - slope_D * time_domain_data[t_D]

    probe_end_reflect = (intercept_D - intercept_C) / (slope_C - slope_D)

    if waveform_data[t_C] < 0.3:
        return "#N/A"
    else:
        return probe_end_reflect

#処理概要　伝搬時間tを取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　測定成否、土壌表面からの反射波の到達時刻、プローブ終端からの反射波の到達時刻、伝搬時間(ns)
def Get_t(time_domain_data,waveform_data):
    #土壌表面からの反射波の到達時刻を取得
    soil_surface_reflect = Detect_SoilSurfaceReflect(time_domain_data,waveform_data)

    #プローブ終端からの反射波の到達時刻を取得
    probe_end_reflect = Detect_ProbeEndReflect(time_domain_data,waveform_data)

    #calc t
    t = probe_end_reflect - soil_surface_reflect

    if probe_end_reflect == "#N/A":
        soil_surface_reflect = "#N/A"
        t = "#N/A"

    return soil_surface_reflect,probe_end_reflect,t

#処理概要　比誘電率を計算
#引数　なし
#戻り値　なし
def Calc_RelativeDielectricConstance():
    #8ch分土壌水分を求める
    for ch in range(8):

        #波形データ一覧を取得
        files = sorted(glob.glob("./raw_data/ch" + format(ch,"#01d") + "_*.txt"))

        result = []
        for i in range(len(files)):
            #波形データ一覧を取得
            datetime_data,waveform = Get_WaveFormDataArray(files[i])

            #時間軸データ一覧を取得
            time_domain = Get_TimeDomainData(MEASUREMENT_POINT)

            #伝搬時間tを計算
            soil_surface_reflect,probe_end_reflect,t = Get_t(time_domain,waveform)

            #比誘電率を計算
            if t == "#N/A":
                result.append([str(datetime_data),"#N/A","#N/A","#N/A")
            else:
                e = str(((C_SPEED * t * (10 ** (-9))) / (2 * PROBE_LENGTH)) ** 2)
                soil_surface_reflect = str(soil_surface_reflect)
                probe_end_reflect = str(probe_end_reflect)
                result.append([str(datetime_data),soil_surface_reflect,probe_end_reflect,e])

        #CSVファイルに書き出し
        f = open("./relative_dielectric_constant_data/ch" + format(ch,"#01d") + "_result.csv","w")
        writer = csv.writer(f)

        print("relative dielectric donstant data has saved as result.csv in directory 'relative_dielectric_constant_data'")
        print("data of ch" + format(ch,"#01d") +":")
        writer.writerow(["datetime","reflect time at soil surface(ns)","reflect time at probe end(ns)","relative dielectrice constant(-)"])
        for i in range(len(result)):
            writer.writerow([result[i][0],result[i][1],result[i][2],result[i][3]])
            print([result[i][0],result[i][1],result[i][2],result[i][3]])
        f.close()

if __name__ == '__main__':
    Calc_RelativeDielectricConstance()
