#coding: UTF-8
"""
シンプルなUDP受信スクリプト - ポート12351
"""
import socket

# UDPソケット作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12351))

print("UDP受信開始 - ポート12351")
print("Ctrl+Cで停止")

try:
    count = 0
    while True:
        data, addr = sock.recvfrom(1024)
        count += 1
        print(f"[{count}] {addr}: {data}")
        
        # UTF-8テキストとして表示を試行
        try:
            text = data.decode('utf-8')
            print(f"    テキスト: {text}")
        except:
            print(f"    バイナリ: {data.hex()}")
        print()
        
except KeyboardInterrupt:
    print("\n受信停止")
finally:
    sock.close()