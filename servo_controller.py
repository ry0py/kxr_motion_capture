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
import numpy as np

from enum import Enum

class UnityHumanoidJson(Enum):
    HIPS = "Hips"
    SPINE = "Spine"
    CHEST = "Chest"
    UPPER_CHEST = "UpperChest"
    NECK = "Neck"
    HEAD = "Head"
    LEFT_SHOULDER = "LeftShoulder"
    LEFT_UPPER_ARM = "LeftUpperArm"
    LEFT_LOWER_ARM = "LeftLowerArm"
    LEFT_HAND = "LeftHand"
    RIGHT_SHOULDER = "RightShoulder"
    RIGHT_UPPER_ARM = "RightUpperArm"
    RIGHT_LOWER_ARM = "RightLowerArm"
    RIGHT_HAND = "RightHand"
    LEFT_UPPER_LEG = "LeftUpperLeg"
    LEFT_LOWER_LEG = "LeftLowerLeg"
    LEFT_FOOT = "LeftFoot"
    LEFT_TOE_BASE = "LeftToeBase"
    RIGHT_UPPER_LEG = "RightUpperLeg"
    RIGHT_LOWER_LEG = "RightLowerLeg"
    RIGHT_FOOT = "RightFoot"
    RIGHT_TOE_BASE = "RightToeBase"
class ServoJson(Enum):
    LEFT_SHOULDER_PITCH = "LeftShoulderPitch"
    LEFT_SHOULDER_YAW = "LeftShoulderYaw"
    LEFT_ELBOW = "LeftElbow"
    RIGHT_SHOULDER_PITCH = "RightShoulderPitch"
    RIGHT_SHOULDER_YAW = "RightShoulderYaw"
    RIGHT_ELBOW = "RightElbow"

    RIGHT_UPPER_LEG0 = "RightUpperLeg0"
    RIGHT_UPPER_LEG1 = "RightUpperLeg1"
    RIGHT_LOWER_LEG = "RightLowerLeg"
    RIGHT_FOOT0 = "RightFoot0"
    RIGHT_FOOT1 = "RightFoot1"
    LEFT_UPPER_LEG0 = "LeftUpperLeg0"
    LEFT_UPPER_LEG1 = "LeftUpperLeg1"
    LEFT_LOWER_LEG = "LeftLowerLeg"
    LEFT_FOOT0 = "LeftFoot0"
    LEFT_FOOT1 = "LeftFoot1"

class RcbServoController:
    def __init__(self, com_port="COM3"):
        """
        RCB4サーボコントローラーを初期化

        Args:
            com_port (str): COMポート名 (例: 'COM1', 'COM3')
        """
        self.rcb4 = Rcb4BaseLib()
        self.connect(com_port)
        self.move_t_pose(frame_time=100)

    def connect(self, com_port="COM1"):
        """RCB4に接続"""
        try:
            result = self.rcb4.open(com_port, 115200, 1.3)
            if result and self.rcb4.checkAcknowledge():
                self.is_connected = True
                print(f"RCB4に正常に接続しました (ポート: {com_port})")
                print(f"バージョン: {self.rcb4.Version}")
                return True
            else:
                print(f"RCB4への接続に失敗しました (ポート: {com_port})")
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
    
    def move_t_pose(self, frame_time=100):
        """Tポーズに移動"""
        if not self.is_connected:
            print("RCB4が接続されていません")
            return False

        try:
            # Tポーズのサーボ角度設定
            all_servo_angles = [
                (1, 1, 90),   # 右肩
                (2, 1, 0),    # 右上腕
                (3, 1, 0),    # 右前腕
                (1, 2, -90),  # 左肩
                (2, 1, 0),    # 左上腕
                (3, 1, 0),    # 左前腕
                (4, 1, 0),    # 右太もも0
                (5, 1, 0),    # 右太もも1
                (6, 1, 0),    # 右すね
                (7, 1, 0),    # 右足首0
                (8, 1, 0),    # 右足首1
                (4, 2, 0),   # 左太もも0
                (5, 2, 0),   # 左太もも1
                (6, 2, 0),   # 左すね
                (7, 2, 0),   # 左足首0
                (8, 2, 0),   # 左足首1
            ]
            upper_body_angles = [
                (1, 1, 0,-180,180),   # 右肩
                (2, 1, 90,0,180),    # 右上腕
                (3, 1, 0,-135,135),    # 右前腕
                (1, 2, 0,-180,180),  # 左肩
                (2, 2, 90,0,180),    # 左上腕
                (3, 2, 0,-135,135),    # 左前腕
            ]

            return self.move_multiple_servos(upper_body_angles, frame_time=frame_time)

        except Exception as e:
            print(f"Tポーズ移動エラー: {e}")
            return False

    def angle_to_position(self, angle_degrees,min_angle=-135,max_angle=135):
        """
        角度(度)をRCB4のポジションデータに変換

        Args:
            angle_degrees (float): 角度（度）-135度から+135度

        Returns:
            int: RCB4ポジションデータ (3500-11500)
        """
        # RCB4のサーボは通常-135度から+135度の範囲
        # ポジションデータは3500(最小)から11500(最大)

        # 角度をmin_angle度からmax_angle度の範囲に制限
        angle_degrees = max(min_angle, min(max_angle, angle_degrees))

        # 角度をポジションデータに変換

        position = (11500 - 3500) / (135 + 135) * (angle_degrees) + 7500
        return int(position)
    
    def apply_servo_command(self, command, frame_time=50, is_motion_play=True):
        """受信コマンドをRCB4へ反映"""
        command = self.convert_command2np(command)
        right_shoulder_position = command[UnityHumanoidJson.RIGHT_SHOULDER.value]
        right_upper_arm_position = command[UnityHumanoidJson.RIGHT_UPPER_ARM.value]
        right_lower_arm_position = command[UnityHumanoidJson.RIGHT_LOWER_ARM.value]
        right_hand_position = command[UnityHumanoidJson.RIGHT_HAND.value]
        left_shoulder_position = command[UnityHumanoidJson.LEFT_SHOULDER.value]
        left_upper_arm_position = command[UnityHumanoidJson.LEFT_UPPER_ARM.value]
        left_lower_arm_position = command[UnityHumanoidJson.LEFT_LOWER_ARM.value]
        left_hand_position = command[UnityHumanoidJson.LEFT_HAND.value]
        
        rsp,rsy,re = self.calc_arm_angles(right_upper_arm_position, right_lower_arm_position, right_hand_position)
        lsp,lsy,le = self.calc_arm_angles(left_upper_arm_position, left_lower_arm_position, left_hand_position)
        # print("右肩ピッチの角度は:", rsp,"右肩ヨーの角度は:", rsy,"右肘の角度は:", re)
        # print("左肩ピッチの角度は:", lsp,"左肩ヨーの角度は:", lsy,"左肘の角度は:", le)

        upper_body_angles = [
            (1, 1, -rsp-90,-180,180),   # 右肩ピッチ
            (2, 1, -rsy ,0,180),   # 右肩ヨー
            (3, 1, -re,-135,135),   # 右肘
            (1, 2, lsp+90,-180,180),   # 左肩ピッチ
            (2, 2, lsy,0,180),   # 左肩ヨー
            (3, 2, -le,-135,135),   # 左肘
        ]
        self.move_multiple_servos(upper_body_angles, frame_time=frame_time)

        # 別で腰らへんの位置とつま先の距離で後進か前進か横移動のモーションを実行する
        right_upper_leg = command[UnityHumanoidJson.RIGHT_UPPER_LEG.value]
        right_foot = command[UnityHumanoidJson.RIGHT_FOOT.value]
        left_upper_leg = command[UnityHumanoidJson.LEFT_UPPER_LEG.value]
        left_foot = command[UnityHumanoidJson.LEFT_FOOT.value]

        if is_motion_play:
            self.walk_motion(right_upper_leg, right_foot, left_upper_leg, left_foot)

    def walk_motion(self, right_upper_leg, right_foot, left_upper_leg, left_foot):
        dif_right_x = right_upper_leg[0] - right_foot[0]
        dif_right_y = right_upper_leg[1] - right_foot[1]
        dif_left_x = left_upper_leg[0] - left_foot[0]
        dif_left_y = left_upper_leg[1] - left_foot[1]

        if(dif_right_x < -0.3 or dif_left_x < -0.3):
            print("前進")
            self.rcb4.motionPlay(5)  # モーション番号1を再生
            while True:  # モーションの再生が終わるまで繰り返し
                motionNum = self.rcb4.getMotionPlayNum()  # 現在再生されているモーション番号を取得
                if motionNum < 0:  # モーション番号が0より小さい場合はエラー
                    print("motion get error", motionNum)
                    break
                if motionNum == 0:  # モーション番号が0のときは再生されていない状態
                    print("stop motion or idle")
                    break
                print("play motion -> ", motionNum)
                time.sleep(0.1)

        if(dif_right_x > 0.2 or dif_left_x > 0.2):
            print("後進")
            self.rcb4.motionPlay(6)
            while True:  # モーションの再生が終わるまで繰り返し
                motionNum = self.rcb4.getMotionPlayNum()  # 現在再生されているモーション番号を取得
                if motionNum < 0:  # モーション番号が0より小さい場合はエラー
                    print("motion get error", motionNum)
                    break
                if motionNum == 0:  # モーション番号が0のときは再生されていない状態
                    print("stop motion or idle")
                    break
                print("play motion -> ", motionNum)
                time.sleep(0.1)
        if(dif_right_y > 0.3 or dif_left_y > 0.3):
            print("右に移動")
            self.rcb4.motionPlay(8)
            while True:  # モーションの再生が終わるまで繰り返し
                motionNum = self.rcb4.getMotionPlayNum()  # 現在再生されているモーション番号を取得
                if motionNum < 0:  # モーション番号が0より小さい場合はエラー
                    print("motion get error", motionNum)
                    break
                if motionNum == 0:  # モーション番号が0のときは再生されていない状態
                    print("stop motion or idle")
                    break
                print("play motion -> ", motionNum)
                time.sleep(0.1)
        if(dif_right_y < -0.3 or dif_left_y < -0.3):
            print("左に移動")
            self.rcb4.motionPlay(7)
            while True:  # モーションの再生が終わるまで繰り返し
                motionNum = self.rcb4.getMotionPlayNum()  # 現在再生されているモーション番号を取得
                if motionNum < 0:  # モーション番号が0より小さい場合はエラー
                    print("motion get error", motionNum)
                    break
                if motionNum == 0:  # モーション番号が0のときは再生されていない状態
                    print("stop motion or idle")
                    break
                print("play motion -> ", motionNum)
                time.sleep(0.1)

    def convert_command2np(self, command):
        """コマンドをnumpy配列に変換"""
        joint_angles = {}
        for joint in UnityHumanoidJson:
            each_joint = command.get(joint.value, {"x": 0, "y": 0, "z": 0})
            joint_angles[joint.value] = np.array([each_joint["x"], each_joint["y"], each_joint["z"]])
        return joint_angles

    def calc_arm_angles(self, upper_arm_pos, lower_arm_pos, hand_pos):
        """腕の各関節の角度を計算"""
        # ひじの角度を計算
        s_to_h = hand_pos - upper_arm_pos
        s_to_e = lower_arm_pos - upper_arm_pos
        e_to_h = hand_pos - lower_arm_pos
        l1 = np.linalg.norm(s_to_e, ord=2)  # 上腕の長さ
        l2 = np.linalg.norm(e_to_h, ord=2)       # 前腕の長さ
        d = np.linalg.norm(s_to_h, ord=2)        # 肩から手先までの距離

        # 腕関節のピッチを計算(肩から肘をx,z平面に投影)
        shoulder_pitch_angle = math.atan2(s_to_e[2], s_to_e[0]) * (180.0 / math.pi)

        # 腕関節のヨーを計算)
        s_to_e_xz_len = math.sqrt(s_to_e[0]**2 + s_to_e[2]**2)
        shoulder_yaw_angle = math.atan2(s_to_e[1], s_to_e_xz_len) * (180.0 / math.pi)
        # ひじの角度を計算(余弦定理)
        elbow_angle = (math.pi - math.acos((l1**2 + l2**2 - d**2) / (2 * l1 * l2))) * (180.0 / math.pi)
        return shoulder_pitch_angle, shoulder_yaw_angle, elbow_angle

    def move_multiple_servos(self, servo_angles, frame_time=100):
        """
        複数のサーボを同時に移動

        Args:
            servo_angles (list): [(servo_id, sio, angle, min_angle, max_angle), ...] のリスト
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
            for servo_id, sio, angle_degrees, min_angle, max_angle in servo_angles:
                position = self.angle_to_position(angle_degrees, min_angle, max_angle)
                servo_data = self.rcb4.ServoData(servo_id, sio, position)
                servo_data_list.append(servo_data)
                # print(f"サーボ{servo_id} (SIO{sio}): {angle_degrees:.1f}度 → ポジション{position}")

            # 複数サーボを同時移動
            result = self.rcb4.setServoPos(servo_data_list, frame_time)


            if result:
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
