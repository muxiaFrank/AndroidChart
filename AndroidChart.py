#!/usr/bin/python
# -*- coding: UTF-8 -*-
import subprocess
import os
import re
import time
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

PATH = lambda p: os.path.abspath(
  os.path.join(os.path.dirname(__file__), p)
)
import datetime, logging

dev_model_list = []
dev_list = []
men_list = []

device_dict = {}


def get_devices():
  # 返回 device model 和 device id
  rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
  n = len(rt) - 2
  print("当前已连接待测手机数为：" + str(n))
  for i in range(n):
    nPos = rt[i + 1].index("\t")
    dev = rt[i + 1][:nPos]
    # phone_model = os.popen("adb -s " + dev + ' shell cat /system/build.prop | find "ro.product.model="').readlines()  # 获取手机型号
    # dev_model = phone_model[0][17:].strip('\r\n')
    # dev_model_list.append(dev_model)
    dev_list.append(dev)
    # device_dict.update({dev:dev_model})
  return dev_list


def get_men(pkg_name, dev):
  cmd = "adb -s " + dev + " shell dumpsys meminfo " + pkg_name
  print(cmd)
  men_list = []

  men_s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()

  for info in men_s:
    if str(men_s).find("Pss") > 0:
      list = info.split()[::-1]
      if len(info.split()) and info.split()[0].decode() == "Pss":
        Pss_position = list.index(b'Pss')
      elif len(info.split()) and info.split()[0].decode() == "Native" and info.split()[1].decode() == 'Heap':
        men_list.append(round(int(list[Pss_position].decode()) / 1024, 2))
      elif len(info.split()) and info.split()[0].decode() == "Dalvik" and info.split()[1].decode() == 'Heap':
        men_list.append(round(int(list[Pss_position].decode()) / 1024, 2))
    else:
      list = info.split()[::-1]
      if len(info.split()) and list[0].decode() == "Free":
        Size_position = list.index(b'Size')
      elif len(info.split()) and info.split()[0].decode() == "Native":
        men_list.append(int(list[Size_position].decode()))
      elif len(info.split()) and info.split()[0].decode() == "Dalvik" and info.split()[1].decode() == 'Heap':
        men_list.append(int(list[Size_position].decode()))
  mem = men_list
  print("----men----")
  logging.info(mem)
  # writeInfo(men, PATH("../info/" + dev + "_men.pickle"))
  return mem


def get_battery(dev):
  battery = []
  adb_battery = "adb -s " + dev + " shell dumpsys battery"
  print(adb_battery)
  _battery = subprocess.Popen(adb_battery, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.readlines()
  for info in _battery:
    if info.split()[0].decode() == "level:":
      battery.append(int(info.split()[1].decode()))
  battery2 = battery[0]
  print("-----battery------")
  print(battery2)
  # writeInfo(battery2, PATH("../info/" + dev + "_battery.pickle"))
  return battery2


def get_pid(pkg_name, dev):
  # print("----get_pid-------")
  pid = subprocess.Popen("adb -s " + dev + " shell ps | grep " + pkg_name, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).stdout.readlines()
  # print(pid)

  for item in pid:
    if item.split()[8].decode() == pkg_name:
      return item.split()[1].decode()


def get_flow(pid, type, dev):
  # pid = get_pid(pkg_name)
  upflow = downflow = 0
  if pid is not None:
    cmd = "adb -s " + dev + " shell cat /proc/" + pid + "/net/dev"
    print(cmd)
    _flow = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).stdout.readlines()
    for item in _flow:
      if type == "wifi" and item.split()[0].decode() == "wlan0:":  # wifi
        # 0 上传流量，1 下载流量
        upflow = int(item.split()[9].decode())
        downflow = int(item.split()[1].decode())
      if type == "gprs" and item.split()[0].decode() == "rmnet0:":  # gprs
        upflow = int(item.split()[9].decode())
        downflow = int(item.split()[1].decode())
  print("------flow---------")
  print(upflow, downflow)
  # writeFlowInfo(upflow, downflow, PATH("../info/" + dev + "_flow.pickle"))


def get_cpu(dev, pid):
  cmd = "adb -s " + dev + " shell top  -d 1 -n 1 | grep %s" % pid

  print(cmd)

  cpu_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()

  print cpu_info

  for i in cpu_info:
    nowTime = datetime.datetime.now().strftime('%m-%d %H:%M:%S')

    cpu = i.split()[2].decode()
    cpu = int(cpu.split("%")[0])

  print "----cpu----{}".format(cpu)

  return [nowTime, round(cpu,2) / 100]


if __name__ == '__main__':

  PATH = os.getcwd()

  rows = []

  columns = ['time', 'cpu', 'Native Heap', 'Dalvik Heap']

  mem_list = []

  cpu_list = []

  device_list = get_devices()

  package_name = sys.argv[1]

  pid = get_pid(package_name, device_list[0])

  print(device_list)

  for item in range(20):

    for i in dev_list:
      devices = i

      cpu_info = get_cpu(devices, pid)

      print cpu_info

      print 111111111111111

      cpu_list += cpu_info

      cpu_avg = sum(cpu_list[1::2]) / int(item + 1) * 100

      cpu_avg = "{}%".format(round(cpu_avg), 2)

      mem_info = get_men(package_name, devices)

      mem_list += mem_info

      Native_Heap_avg = round(int(sum(mem_list[::2])) / int(item + 1), 2)

      Dalvik_Heap_avg = round(int(sum(mem_list[1::2])) / int(item + 1), 2)

      app_info = cpu_info + mem_info

      info = dict(zip(columns, app_info))

      rows.append(info)

      chartData = {
        'columns': columns,
        'cpu_avg': cpu_avg,
        'Native_AVG': Native_Heap_avg,
        'Dalvik_AVG': Dalvik_Heap_avg,
        'rows': rows
      }

    chartData = json.dumps(chartData)

    with open('{}/static/data.json'.format(PATH), 'w') as f:
      f.write(str(chartData))

  """os.popen("adb kill-server adb")
  os.popen("adb start-server")
  time.sleep(2)
  dev = "7N2SSE158U004185"
  package_name = "com.quvideo.slideplus"
  pid = get_pid(package_name,dev)
  print(pid)
  cpu_kel = get_cpu_kel(dev)
  print(cpu_kel)
  get_battery(devices)
  get_men(package_name, devices)
  get_fps(package_name, devices)
  get_flow(pid, "wifi", devices)
  cpu_rate(pid,cpu_kel, devices)"""
