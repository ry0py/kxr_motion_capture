import sys
import socket
import json
import time

sys.path.append("./RCB4Lib_for_Python_V100B/Rcb4Lib")

from Rcb4BaseLib import Rcb4BaseLib
import time

def angle_to_position(angle_degrees):
    """角度をRCB4ポジションに変換"""
    # -135度から+135度を3500から11500に変換
    angle_degrees = max(-135, min(135, angle_degrees))
    position = 7500 + (angle_degrees / 135.0) * 4000
    return int(position)


def move_servo_to_angle(rcb4, servo_id, sio, angle, frame_time=100):
    """サーボを指定角度に移動"""
    position = angle_to_position(angle)
    servo_data = rcb4.ServoData(servo_id, sio, position)

    result = rcb4.setServoPos([servo_data], frame_time)
    if result:
        print(f"サーボ{servo_id}: {angle}度に移動 (位置: {position})")
    else:
        print(f"サーボ{servo_id}: 移動失敗")
    return result


def main():
    
    # UDP受信スクリプトを別スレッドで起動する場合はここにコードを追加

    # UDPソケット作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 9000))
        # メイン処理
    rcb4 = Rcb4BaseLib()

    # 接続
    print("RCB4に接続中...")
    connection_result = rcb4.open("COM3", 115200, 1.3)  # COMポートを適切に設定
    if not connection_result:
        print("COMポートのオープンに失敗。適切なCOMポートを指定してください。")
        exit()

    print("UDP受信開始 - ポート9000")
    print("Ctrl+Cで停止")

    try:
        count = 0
        while True:
            data, addr = sock.recvfrom(1024)
            count += 1

            # UTF-8テキストとして表示を試行
            text = data.decode('utf-8')
            # 取得したJsonをパースする
            command = json.loads(text)
            # print(f"    コマンド: {command.get('leftUpperArm', 0)}")
            print(f"    コマンド: {command}")
            left_shoulder_angle = command.get('leftShoulder', 0)
            left_upper_arm_angle = command.get('leftUpperArm', 0)
            left_lower_arm_angle = command.get('leftLowerArm', 0)
            right_shoulder_angle = command.get('rightShoulder', 0)
            right_upper_arm_angle = command.get('rightUpperArm', 0)
            right_lower_arm_angle = command.get('rightLowerArm', 0)
            
            if rcb4.checkAcknowledge():
                move_servo_to_angle(rcb4, servo_id=1, sio=1, angle=right_shoulder_angle, frame_time=50)
                move_servo_to_angle(rcb4, servo_id=2, sio=1, angle=right_upper_arm_angle, frame_time=50)
                move_servo_to_angle(rcb4, servo_id=3, sio=1, angle=right_lower_arm_angle, frame_time=50)

                # move_servo_to_angle(rcb4, servo_id=1, sio=2, angle=left_shoulder_angle-90, frame_time=50)
                # move_servo_to_angle(rcb4, servo_id=2, sio=2, angle=left_upper_arm_angle-90, frame_time=50)
                # move_servo_to_angle(rcb4, servo_id=3, sio=2, angle=left_lower_arm_angle-90, frame_time=50)
            else:
                print("RCB4接続失敗!")
            print()
            time.sleep(0.56)

    except KeyboardInterrupt:
        print("\n受信停止")
    finally:
        sock.close()
        rcb4.close()


if __name__ == "__main__":
    main()