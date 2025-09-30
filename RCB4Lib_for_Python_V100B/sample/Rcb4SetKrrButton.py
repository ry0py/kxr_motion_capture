#coding: UTF-8
import sys
sys.path.append('../Rcb4Lib') #Rcb4Libの検索パスを追加

from Rcb4BaseLib import Rcb4BaseLib            #Rcb4BaseLib.pyの中のRcb4BaseLibが使えるように設定

import time                   #timeが使えるように宣言

rcb4 = Rcb4BaseLib()      #rcb4をインスタンス(定義)
        
rcb4.open('/dev/ttyAMA0',115200,1.3)  #(portName,bundrate,timeout(s))
#rcb4.open('/dev/ttyUSB0',115200,1.3)


if rcb4.checkAcknowledge() == True:  #通信が返ってきたとき

    print('Set KRR UP Button')
    #KRCの上ボタンを擬似的に押す
    rcb4.setKrrButtonData(Rcb4BaseLib.KRR_BUTTON.UP.value)
    
    time.sleep(2.0)

    print('Set KRR UP+S1 Button')
    #KRCの上ボタン+S1を擬似的に押す
    buttonData = Rcb4BaseLib.KRR_BUTTON.UP.value | Rcb4BaseLib.KRR_BUTTON.S1.value
    rcb4.setKrrButtonData(buttonData)
    
    time.sleep(3.0)
    
    print('Set KRR STOP(NONE) Button')
    #KRCのボタンを離した状態にする
    rcb4.setKrrButtonData(rcb4.KRR_BUTTON.NONE.value)

else:  #通信が返ってきていないときはエラー
    print ('checkAcknowledge error')
   
   
rcb4.close()

