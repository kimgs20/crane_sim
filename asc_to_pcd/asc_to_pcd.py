#!/usr/bin/env python  
# coding: utf-8

from sys import argv
def count_lines(filename):
    file_origin = open(filename, "r")
    length = len(file_origin.readlines())
    return length

def convert(filename):
    print("======================================")
    print ("the input file name is: %r" %filename)

    height_m = filename.split('_')[2]
    height = float(filter(str.isdigit, height_m)) # asc 파일 명에서 명시한 높이값 추출
    # print("height of LiDAR: %f" %height)

    f_prefix = filename.split('.')[0]
    output_filename = '{prefix}.pcd'.format(prefix=f_prefix)

    output = open(output_filename,"w+")     # pcd를 쓰는 객체

    file = open(filename,"r")               # asc를 읽는 객체
    length = count_lines(filename)
    print("original length: %d" %length)
    skip_interval = round(length * 0.000025) # point data 숫자를 감소시키기 위한 출력 간격 지정, 
                                             # length에 곱하는 숫자가 클수록 저장 간격이 커지므로 출력되는 point 수가 작아짐
    print("skip interval: %d" %skip_interval)
    count = 0
    k = 0
    while True:                             # 읽고 쓰는 loop
        try:
            line = file.readline()
            line = line[:-3]
            splited = line.split(',')       # x, y, z는 COMMA 로 구분함
            newline = str(-float(splited[0]))+' '+str(-float(splited[1]))+' '+str(height-float(splited[2]))+'\n'
                                                # 원점 기준으로 point들을 반전시키고, 파일명에서 명시한 높이 만큼 상승시킴
            z = height - float(splited[2])      # z>0 이면 지면 보다 높은 높이
            w = float(splited[2])               # w>0 이면 LiDAR 보다 낮은 높이
            if (z>0.0 and w>0.0) and k%skip_interval==0:   # 지면과 LiDAR사이 point만 새로운 pcd data로 출력
                # if(float(splited[0])**2+float(splited[1])**2+float(splited[2])**2<3**2):        # LiDAR로 부터 3m 이내의 측정점 제거
                #     continue
                output.write(newline)
                count += 1
            k=k+1
        except:
            break
    print("number of points: %d" %count)
    print("======================================")
    print("")
    file.close()
    output.close()

    fp = open(output_filename,'r+')         # pcd file header를 데이터 앞부분에 쓰기 위한 객체
    list = ['# .PCD v.7 - Point Cloud Data file format\n','VERSION .7\n','FIELDS x y z\n','SIZE 4 4 4\n','TYPE F F F\n','COUNT 1 1 1\n', "VIEWPOINT 0 0 0 1 0 0 0\n"]
    lines = fp.readlines()
    fp.seek(0)
    fp.writelines(list)
    fp.write('WIDTH ')
    fp.write(str(count))
    fp.write('\nHEIGHT ')
    fp.write(str(1))
    fp.write('\nPOINTS ')
    fp.write(str(count))
    fp.write('\nDATA ascii\n')
    fp.writelines(lines)
    fp.close()
 
import os
items = os.listdir(".")
newlist = []
for names in items:                         # asc_to_pcd.py python file이 있는 directory 내의 모든 asc file에 대하여 반복
    if names.endswith(".asc"):
        newlist.append(names)
for i in newlist:
    count_lines(i)
    convert(i)