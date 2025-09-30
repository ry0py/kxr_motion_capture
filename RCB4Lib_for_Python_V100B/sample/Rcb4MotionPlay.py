#coding: UTF-8
import sys
sys.path.append('../Rcb4Lib') #Rcb4Libの検索パスを追加

from Rcb4BaseLib import Rcb4BaseLib            #Rcb4BaseLib.pyの中のRcb4BaseLibが使えるように設定
import time                   #timeが使えるように宣言

rcb4 = Rcb4BaseLib()      #rcb4をインスタンス(定義)
        
rcb4.open('/dev/ttyAMA0',115200,1.3)  #(portName,bundrate,timeout(s))
#rcb4.open('/dev/ttyUSB0',115200,1.3)

if rcb4.checkAcknowledge() == True:  #通信が返ってきたとき

    print ('MotionPlay(1)')
    rcb4.motionPlay(1)       #モーション番号1を再生

    while True:     #モーションの再生が終わるまで繰り返し
        motionNum = rcb4.getMotionPlayNum()   #現在再生されているモーション番号を取得
        if motionNum < 0:                     #モーション番号が0より小さい場合はエラー
            print('motion get error',motionNum)
            break
        if motionNum == 0:                    #モーション番号が0のときは再生されていない状態
            print('stop motion or idle')
            break
        
        print('play motion -> ',motionNum)
        time.sleep(0.1)
        
    
else:  #通信が返ってきていないときはエラー
    print ('checkAcknowledge error')
  
   
rcb4.close()
