import json
import queue
import socket
import sys
import threading
import time
from servo_controller import RcbServoController

sys.path.append("./RCB4Lib_for_Python_V100B/Rcb4Lib")

from json import JSONDecodeError

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


def servo_worker(servo_controller,command_queue, stop_event, frame_time=50, is_motion_play=True):
    """キューからコマンドを取得してサーボへ反映"""

    while not stop_event.is_set():
        try:
            command = command_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        try:
            servo_controller.apply_servo_command(command, frame_time=frame_time,is_motion_play=True)
        finally:
            command_queue.task_done()


def main():

    # UDPソケット作成
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 9000))
    sock.settimeout(0.2)

    print("UDP受信開始 - ポート9000")
    print("Ctrl+Cで停止")
    
    # RCB4接続
    com = "COM4"  # 実際のCOMポートに変更
    frame_time = 50  # サーボ移動時間（フレーム数）
    is_motion_play = True  # 歩行モーションを使用するか
    servo_controller = RcbServoController(com)  # 実際のCOMポートに変更

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
        args=(servo_controller, command_queue, stop_event, frame_time,is_motion_play),
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
        servo_controller.disconnect()

    print("終了しました")


if __name__ == "__main__":
    main()
