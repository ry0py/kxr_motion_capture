import json
import queue
import socket
import sys
import threading
import time

sys.path.append("./RCB4Lib_for_Python_V100B/Rcb4Lib")

from Rcb4BaseLib import Rcb4BaseLib
from json import JSONDecodeError


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
    if not result:
        print(f"サーボ{servo_id}: 移動失敗")
    return result


def apply_servo_command(rcb4, command, frame_time=50):
    """受信コマンドをRCB4へ反映"""

    right_shoulder_angle = command.get("rightShoulder", 0)
    right_upper_arm_angle = command.get("rightUpperArm", 0)
    right_lower_arm_angle = command.get("rightLowerArm", 0)

    move_servo_to_angle(rcb4, servo_id=1, sio=1, angle=right_shoulder_angle, frame_time=frame_time)
    move_servo_to_angle(rcb4, servo_id=2, sio=1, angle=right_upper_arm_angle, frame_time=frame_time)
    move_servo_to_angle(rcb4, servo_id=3, sio=1, angle=right_lower_arm_angle, frame_time=frame_time)

    # 左腕を使用する場合は以下を有効化
    # left_shoulder_angle = command.get("leftShoulder", 0)
    # left_upper_arm_angle = command.get("leftUpperArm", 0)
    # left_lower_arm_angle = command.get("leftLowerArm", 0)
    # move_servo_to_angle(rcb4, servo_id=1, sio=2, angle=left_shoulder_angle, frame_time=frame_time)
    # move_servo_to_angle(rcb4, servo_id=2, sio=2, angle=left_upper_arm_angle, frame_time=frame_time)
    # move_servo_to_angle(rcb4, servo_id=3, sio=2, angle=left_lower_arm_angle, frame_time=frame_time)


def udp_listener(sock, command_queue, stop_event):
    """UDPでコマンドを受信しキューへ投入"""

    while not stop_event.is_set():
        try:
            data, _ = sock.recvfrom(2048)
        except socket.timeout:
            continue
        except OSError:
            # ソケットが閉じられた
            break

        try:
            text = data.decode("utf-8")
            command = json.loads(text)
        except (UnicodeDecodeError, JSONDecodeError) as exc:
            print(f"受信データ解析エラー: {exc}")
            continue

        try:
            command_queue.put(command, timeout=0.05)
        except queue.Full:
            # 最新コマンドで上書きするため古いものを破棄
            try:
                command_queue.get_nowait()
                command_queue.task_done()
            except queue.Empty:
                pass
            try:
                command_queue.put_nowait(command)
            except queue.Full:
                # それでも投入できなければスキップ
                pass


def servo_worker(rcb4, command_queue, stop_event, frame_time=50):
    """キューからコマンドを取得してサーボへ反映"""

    while not stop_event.is_set():
        try:
            command = command_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        try:
            apply_servo_command(rcb4, command, frame_time=frame_time)
        finally:
            command_queue.task_done()


def main():

    # UDPソケット作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 9000))
    sock.settimeout(0.2)

    rcb4 = Rcb4BaseLib()

    # 接続
    print("RCB4に接続中...")
    connection_result = rcb4.open("COM3", 115200, 1.3)  # COMポートを適切に設定
    if not connection_result or not rcb4.checkAcknowledge():
        print("RCB4への接続に失敗しました。COMポートや配線を確認してください。")
        sock.close()
        return

    print("UDP受信開始 - ポート9000")
    print("Ctrl+Cで停止")

    command_queue = queue.Queue(maxsize=5)
    stop_event = threading.Event()

    listener_thread = threading.Thread(
        target=udp_listener,
        args=(sock, command_queue, stop_event),
        name="UDPListener",
        daemon=True,
    )
    worker_thread = threading.Thread(
        target=servo_worker,
        args=(rcb4, command_queue, stop_event),
        name="ServoWorker",
        daemon=True,
    )

    listener_thread.start()
    worker_thread.start()

    try:
        while listener_thread.is_alive() and worker_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n停止要求を受信しました")
    finally:
        stop_event.set()
        sock.close()
        listener_thread.join(timeout=1.0)
        worker_thread.join(timeout=1.0)
        rcb4.close()

    print("終了しました")


if __name__ == "__main__":
    main()
