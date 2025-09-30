# coding: UTF-8
"""
RCB4サーボモータ制御スクリプト
サーボを指定した角度に回転させる
"""
import sys

sys.path.append("./RCB4Lib_for_Python_V100B/Rcb4Lib")  # Rcb4Libの検索パスを追加

from Rcb4BaseLib import Rcb4BaseLib
import time
import math


class RcbServoController:
    def __init__(self, com_port="COM3"):
        """
        RCB4サーボコントローラーを初期化

        Args:
            com_port (str): COMポート名 (例: 'COM1', 'COM3')
        """
        self.rcb4 = Rcb4BaseLib()
        self.com_port = com_port
        self.is_connected = False

    def connect(self):
        """RCB4に接続"""
        try:
            result = self.rcb4.open(self.com_port, 115200, 1.3)
            if result and self.rcb4.checkAcknowledge():
                self.is_connected = True
                print(f"RCB4に正常に接続しました (ポート: {self.com_port})")
                print(f"バージョン: {self.rcb4.Version}")
                return True
            else:
                print(f"RCB4への接続に失敗しました (ポート: {self.com_port})")
                return False
        except Exception as e:
            print(f"接続エラー: {e}")
            return False

    def disconnect(self):
        """RCB4から切断"""
        if self.is_connected:
            self.rcb4.close()
            self.is_connected = False
            print("RCB4から切断しました")

    def angle_to_position(self, angle_degrees):
        """
        角度(度)をRCB4のポジションデータに変換

        Args:
            angle_degrees (float): 角度（度）-135度から+135度

        Returns:
            int: RCB4ポジションデータ (3500-11500)
        """
        # RCB4のサーボは通常-135度から+135度の範囲
        # ポジションデータは3500(最小)から11500(最大)

        # 角度を-135度から+135度の範囲に制限
        angle_degrees = max(-135, min(135, angle_degrees))

        # 角度をポジションデータに変換
        # -135度 → 3500, 0度 → 7500, +135度 → 11500
        center_position = 7500  # 中央位置
        max_range = 4000  # 中央から最大/最小までの範囲

        position = center_position + (angle_degrees / 135.0) * max_range
        return int(position)

    def position_to_angle(self, position):
        """
        RCB4のポジションデータを角度(度)に変換

        Args:
            position (int): RCB4ポジションデータ (3500-11500)

        Returns:
            float: 角度（度）
        """
        center_position = 7500
        max_range = 4000

        angle = ((position - center_position) / max_range) * 135.0
        return angle

    def move_servo(self, servo_id, sio, angle_degrees, frame_time=100):
        """
        サーボを指定角度に移動

        Args:
            servo_id (int): サーボID (0-17)
            sio (int): SIO番号 (1: SIO1-4, 2: SIO5-8)
            angle_degrees (float): 目標角度（度）-135度から+135度
            frame_time (int): 移動時間（フレーム数、1フレーム≒11.2ms）

        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected:
            print("RCB4が接続されていません")
            return False

        try:
            # 角度をポジションデータに変換
            position = self.angle_to_position(angle_degrees)

            # ServoDataオブジェクトを作成
            servo_data = self.rcb4.ServoData(servo_id, sio, position)

            # サーボを移動
            result = self.rcb4.setServoPos([servo_data], frame_time)

            if result:
                print(f"サーボ{servo_id} (SIO{sio}) を {angle_degrees:.1f}度 (ポジション{position}) に移動しました")
                return True
            else:
                print(f"サーボ{servo_id} (SIO{sio}) の移動に失敗しました")
                return False

        except Exception as e:
            print(f"サーボ移動エラー: {e}")
            return False

    def move_multiple_servos(self, servo_angles, frame_time=100):
        """
        複数のサーボを同時に移動

        Args:
            servo_angles (list): [(servo_id, sio, angle), ...] のリスト
            frame_time (int): 移動時間（フレーム数）

        Returns:
            bool: 成功時True、失敗時False
        """
        if not self.is_connected:
            print("RCB4が接続されていません")
            return False

        try:
            servo_data_list = []

            # 各サーボのデータを準備
            for servo_id, sio, angle_degrees in servo_angles:
                position = self.angle_to_position(angle_degrees)
                servo_data = self.rcb4.ServoData(servo_id, sio, position)
                servo_data_list.append(servo_data)
                print(f"サーボ{servo_id} (SIO{sio}): {angle_degrees:.1f}度 → ポジション{position}")

            # 複数サーボを同時移動
            result = self.rcb4.setServoPos(servo_data_list, frame_time)

            if result:
                print(f"{len(servo_angles)}個のサーボを同時に移動しました")
                return True
            else:
                print("複数サーボの移動に失敗しました")
                return False

        except Exception as e:
            print(f"複数サーボ移動エラー: {e}")
            return False

    def set_servo_free(self, servo_id, sio):
        """サーボをフリー状態にする"""
        if not self.is_connected:
            print("RCB4が接続されていません")
            return False

        try:
            servo_data = self.rcb4.ServoData(servo_id, sio, 0)
            result = self.rcb4.setFreePos(servo_data)

            if result:
                print(f"サーボ{servo_id} (SIO{sio}) をフリー状態にしました")
                return True
            else:
                print(f"サーボ{servo_id} (SIO{sio}) のフリー設定に失敗しました")
                return False

        except Exception as e:
            print(f"サーボフリー設定エラー: {e}")
            return False


def main():
    """使用例"""
    # コントローラーを作成（COMポートを適切に設定してください）
    controller = RcbServoController("COM3")  # 実際のCOMポートに変更

    try:
        # RCB4に接続
        if not controller.connect():
            print("接続に失敗しました。COMポートを確認してください。")
            return

        # 使用例1: 単一サーボを90度に移動
        print("\n=== 単一サーボ制御例 ===")
        controller.move_servo(servo_id=0, sio=1, angle_degrees=90, frame_time=200)
        time.sleep(2)

        # 使用例2: 単一サーボを-45度に移動
        controller.move_servo(servo_id=0, sio=1, angle_degrees=-45, frame_time=150)
        time.sleep(2)

        # 使用例3: 複数サーボを同時移動
        print("\n=== 複数サーボ制御例 ===")
        servo_movements = [
            (0, 1, 0),  # サーボID0, SIO1, 0度
            (1, 1, 45),  # サーボID1, SIO1, 45度
            (2, 1, -30),  # サーボID2, SIO1, -30度
        ]
        controller.move_multiple_servos(servo_movements, frame_time=180)
        time.sleep(3)

        # 使用例4: サーボを中央位置に戻す
        print("\n=== 中央位置に戻す ===")
        reset_movements = [
            (0, 1, 0),  # 中央位置
            (1, 1, 0),  # 中央位置
            (2, 1, 0),  # 中央位置
        ]
        controller.move_multiple_servos(reset_movements, frame_time=200)
        time.sleep(2)

        # 使用例5: サーボをフリー状態にする
        print("\n=== フリー状態設定 ===")
        controller.set_servo_free(0, 1)

    except KeyboardInterrupt:
        print("\n操作が中断されました")
    finally:
        # 切断
        controller.disconnect()


if __name__ == "__main__":
    main()
