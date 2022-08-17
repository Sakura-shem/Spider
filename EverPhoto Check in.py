import hashlib
import requests as req
from datetime import datetime





# 日期字符串格式化
def dateTime_format(dt: str) -> str:
    try:
        dl = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S+08:00")

        return dl.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"格式化日期时出错, 原因: {e}")

class Everphoto():
    # 登录地址
    LOGIN_URL = "https://web.everphoto.cn/api/auth"
    # 签到地址
    CHECKIN_URL = "https://openapi.everphoto.cn/sf/3/v4/PostCheckIn"
    # 每日奖励
    DAILY_REWARD = "https://openapi.everphoto.cn/sf/3/v4/MissionRewardClaim"
    # # 备注, 收藏等任务共同的 api
    # CMD = "https://openapi.everphoto.cn/sf/3/v4/PostSyncCommand"
    # 任务状态回调
    TASKREPORT = "https://openapi.everphoto.cn/sf/3/v4/MissionReport"

    def __init__(
        self,
        account: str,
        password: str,
        country_code: str = "+86",
    ) -> None:

        self.__account = account
        self.__password = password
        self.headers = {
            "user-agent": "EverPhoto/4.5.0 (Android;4050002;MuMu;23;dev)",
            "application": "tc.everphoto",
        }
        self.userInfo = {}
        self.country_code = country_code

    # 获取 md5 加密后的密码
    def get_pwd_md5(self) -> str:
        salt = "tc.everphoto."
        pwd = salt + self.__password
        md5 = hashlib.md5(pwd.encode())
        return md5.hexdigest()

    # 登陆
    def login(self):
        try:
            data = {
                "mobile": f"{self.country_code}{self.__account}",
                "password": self.get_pwd_md5(),
            }

            print(f"++开始登录账号 {self.__account} ++")

            res = req.post(
                Everphoto.LOGIN_URL,
                data=data,
                headers=self.headers,
            ).json()

            if res.get("code") == 0:
                print(f"🎉 登录账号 {self.__account} 成功")

                data = res.get("data")

                self.headers.update(
                    {
                        "authorization": f"Bearer {data['token']}",
                    },
                )

                profile = data["user_profile"]

                self.userInfo.update(
                    {  # 账号
                        "account": self.__account,
                        # 用户名
                        "name": profile["name"],
                        # vip等级
                        "vip": profile.get("vip_level"),
                        # 创建时间
                        "created": dateTime_format(profile["created_at"]),
                        # 注册时长
                        "day": profile["days_from_created"],
                    },
                )
                return {"status": True}
            else:
                raise Exception(res.get("message"))
        except Exception as e:
            print(f"😭 登录账号 {self.__account} 时出现错误, 原因: {e}")

            return {
                "status": False,
                "message": e,
            }

    # 签到
    def checkin(self):
        try:
            headers = {
                "content-type": "application/json",
                "host": "openapi.everphoto.cn",
                "connection": "Keep-Alive",
            }

            headers.update(self.headers)

            print(f"++账号 {self.__account} 开始签到++")

            res = req.post(
                Everphoto.CHECKIN_URL,
                headers=headers,
            ).json()

            code = res.get("code")

            if code == 0:
                print(f"账号 {self.__account} 签到成功")

                data = res.get("data")

                if data.get("checkin_result") is True:
                    rwd = data["reward"] / (1024 * 1024)  # 今日获得
                    msg = "签到成功"
                else:
                    rwd = 0
                    msg = "今日已签到"

                return {
                    "status": True,
                    "reward": rwd,
                    "message": msg,
                    # 连续签到天数
                    "continuity": data.get("continuity"),
                    # 总计获得
                    "total": data.get("total_reward") / (1024 * 1024),
                    # 明日可获得
                    "tomorrow": data.get("tomorrow_reward") / (1024 * 1024),
                }
            elif code == 20104:
                # 未登录
                raise Exception(res.get("message"))
            elif code == 30001:
                # 服务器内部错误?
                raise Exception(res.get("message"))
            else:
                raise Exception("其他错误")
        except Exception as e:
            print(f"账号 {self.__account} 签到时出现错误, 原因: {e}")

            return {
                "status": False,
                "message": f"签到失败, 原因: {e}",
            }

    def start(self):
        r = self.login()

        if r["status"]:
            res = self.checkin()  # 签到
            print(res)
            return res
        else:
            return {
                "status": False,
                "message": f"登录失败, 原因: {r['message']}",
                "account": self.__account,
            }

if __name__ == "__main__":
    Bot = Everphoto("", "")
    res = Bot.start()