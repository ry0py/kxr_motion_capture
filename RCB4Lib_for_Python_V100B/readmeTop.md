# Rcb4Lib
---
## Overview
近藤科学製RCB4をRaspberryPi等から動かすpythonのライブラリです。
This library is for connecting a Kondo Kagaku RCB4 from python.


## Description
近藤科学製RCB4(ロボット用コントロールボード)をpythonで動かすためのライブラリです。  
This library is for connecting a RCB4 (Kondo kagaku robot control board) using python.

RaspberryPi等からpython経由で
- RCB4内に保存されているのモーションデータを再生
  Motion data preserved by RCB4 is played.

- Rcb4に接続されているサーボモータに角度指令を送ることができる
  Posiotn order can be sent to servo motor which leads to RCB4.

...etc


## Contents
root/
 ├Rcb4Lib
 |    └ Rcb4BaseLib.py
 ├sample
 |    ├Rcb4AckTest.py
 |    |     .....
 |    └ (sample ...etc)
 ├readmeTop.md (this file)
 └FunctionList V100B(See to index.html)

## Requirement
- Python 3  (check to Python3.5.3)
  + serial(pySerial)
  + Enum
  + struct

## Usage
* ダウンロードし解凍が終わったら「Rcb4Lib」「sample」をフォルダごとコピーしてください。

  Please do copying every the folder of「Rcb4Lib」and「sample」 at the optional place.

  ※サンプルプログラムは相対パスで設定しています。

  ※A sample program establishes Rcb4Lib by a relative path.

* RCB4と接続に関しては[弊社HP](https://kondo-robot.com/))をご覧ください。

  Please check the [OurHomePage](https://kondo-robot.com/) to connect with RCB4.

* サンプルプログラムを実行してみてください

  Please execute a sample program.


## Licence
RCB4Libフォルダ内をご覧ください。

Please check in the RCB4Lib folder.

## Author
近藤科学株式会社  02/2019
Kondo Kagaku co.,ltd.
近藤科学ホームページ:(<http://kondo-robot.com/>)
