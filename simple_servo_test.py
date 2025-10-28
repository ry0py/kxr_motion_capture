# coding: UTF-8
"""
RCB4サーボ制御 - シンプル使用例
"""
import sys

sys.path.append("./RCB4Lib_for_Python_V100B/Rcb4Lib")

from Rcb4BaseLib import Rcb4BaseLib
import time


def angle_to_position(angle_degrees):
    """角度をRCB4ポジションに変換"""
    # -135度から+135度を3500から11500に変換
    # angle_degrees = max(-180, min(180, angle_degrees))
    # position = 7500 + (angle_degrees / 180.0) * 4000
    position = (12900 - 3500) / (180 + 135) * (angle_degrees) + 7500
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


# メイン処理
rcb4 = Rcb4BaseLib()
id = 2
sio =2

# 接続
print("RCB4に接続中...")
connection_result = rcb4.open("COM3", 115200, 1.3)  # COMポートを適切に設定
if not connection_result:
    print("COMポートのオープンに失敗。適切なCOMポートを指定してください。")
    exit()

if rcb4.checkAcknowledge():
    print("RCB4接続成功!")

    try:
        # サーボID 0番, SIO1 を様々な角度に動かす
        print("\n=== サーボテスト開始 ===")

        # 0度（中央）
        move_servo_to_angle(rcb4, servo_id=id, sio=sio, angle=90, frame_time=150)
        # servo_data = rcb4.ServoData(id, sio, 12900)
        # result = rcb4.setServoPos([servo_data], 150)
        time.sleep(2)

        # # 90度（右）
        # move_servo_to_angle(rcb4, servo_id=id, sio=sio, angle=10, frame_time=50)
        # time.sleep(2)

        # # # -90度（左）
        # # move_servo_to_angle(rcb4, servo_id=id, sio=sio, angle=-90, frame_time=150)
        # # time.sleep(2)

        # # 45度
        # move_servo_to_angle(rcb4, servo_id=id, sio=sio, angle=45, frame_time=150)
        # time.sleep(2)

        # # 0度に戻す
        # move_servo_to_angle(rcb4, servo_id=id, sio=sio, angle=0, frame_time=150)
        # time.sleep(1)

        print("\n=== テスト完了 ===")

    except KeyboardInterrupt:
        print("\n操作が中断されました")

else:
    print("RCB4への接続に失敗しました")

# 切断
rcb4.close()
print("切断しました")
