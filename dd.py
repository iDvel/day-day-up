from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from collections import OrderedDict
import sqlite3
import sys
import os

import pyperclip
import matplotlib.pyplot as plt


class DayDayUp():

    def __init__(self):
        # 学习内容
        self.content = None
        # 开始时间 :datetime
        self.start = None
        # 结束时间 :datetime
        self.end = None
        # db
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_dir = os.path.join(base_dir, 'record.sqlite3')
        self.conn = sqlite3.connect(db_dir)
        self.c = self.conn.cursor()

    def go(self):
        """ 启动。ok: 结束此次学习。 回车：查看持续时长 """

        self.start = datetime.now().replace(microsecond=0)
        print(f'内容 <{self.content}> 于 {self.start} 开始...')

        while True:
            command = input('等待命令...（ok、回车）：').lower().strip()
            if command == '':
                print(f'已经坚持了 {datetime.now().replace(microsecond=0) - self.start}')
            elif command == 'ok':
                # 输出信息、拷贝到剪贴板
                self.output()
                # 日常杂项临时记录的记录，回车不写入。学习时间yes写入
                if input('是否写入日志？（yes、回车）').lower().strip() == 'yes':
                    # 写入日志（数据库）
                    self.log()
                    # 总结（条形图）
                    self.sum_up()
                break

    def output(self):
        """
        输出内容: 内容 2020-02-27 11:02 - 2020-02-27 11:17  （已复制到剪贴板）
        改进:     内容 2020-02-27 11:02 - 11:17  （已复制到剪贴板）
        （为了适应 Fantastical App，之前的格式有时候直接粘贴它可能在越过零点时识别错误）
        """
        self.end = datetime.now().replace(microsecond=0)

        # 记录和输出的信息都去掉秒数，否则显得太乱
        text = f"{self.content} {self.start.strftime('%Y-%m-%d %H:%M')} - {self.end.strftime('%H:%M')}"
        pyperclip.copy(text)
        print('-' * 50)
        print('本次时长:', (self.end - self.start).__str__()[:-3])
        print('-' * 50)
        print(text + '  （已复制到剪贴板）\n' + '-' * 50)

    def log(self):
        """ 学习日志记录，写入数据库 """

        self.c.execute("""
        CREATE TABLE IF NOT EXISTS records (
          "content" VARCHAR(37) NOT NULL,
          "hours" float NOT NULL,
          "start" DATETIME NOT NULL,
          "end" DATETIME NOT NULL
        );
        """)
        self.conn.commit()

        # 持续时间转化为小时数
        self.end += timedelta(minutes=1)  # TODO DELETE
        h = (self.end - self.start).seconds / 60 / 60
        h = Decimal(str(h)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)  # 四舍五入保留2位小数

        self.c.execute(f"""INSERT INTO records VALUES ('{self.content}',
                                                        {h},
                                                        '{self.start.strftime('%Y-%m-%d %H:%M')}',
                                                        '{self.end.strftime('%Y-%m-%d %H:%M')}'
                                                        )""")
        self.conn.commit()

    def sum_up(self):
        """ 条形图展示，默认最近 30 天 """
        d = OrderedDict()
        for i in range(0, 30):
            key = (datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d')
            d[key] = 0.00

        # 查询每日时长，相加
        self.c.execute('SELECT start, hours FROM records')
        for start, hours in self.c.fetchall():
            start = start.split(' ')[0]
            if start in d.keys():
                d[start] += float(hours)

        # 终端显示
        for k, v in reversed(d.items()):
            print(f'{k} → {v:.1f} 小时')

        # 条形图
        title = []
        data = []
        for k, v in d.items():
            title.append(k)
            data.append(v)
        plt.title = '这个参数有用吗？？？'
        plt.barh(title, data)
        plt.show()

    def query_project_duration(self):
        """ 查询每个项目的工作总时长 """
        d = OrderedDict()

        self.c.execute("SELECT content, hours FROM records")

        for content, hour in self.c.fetchall():
            if content not in d.keys():
                d[content] = hour
            else:
                d[content] += hour

        for content, hours in d.items():
            print(f'{hours:>4.1f} |{content}')

    def __del__(self):
        self.conn.close()


def main():
    # 用终端启动：
    # alias dd = "python /.../dd.py"
    # alias dl = "python /.../dd.py log~"
    # alias dq = "python /.../dd.py query~"

    argv = sys.argv
    print(argv)
    dd = DayDayUp()

    if len(argv) == 1:
        print("""\
Usage:
  dd <content>   开始新的学习内容
  dl [days]      默认查询最近30日学习时长
  dq             查询每个项目的总时长""")
    elif len(argv) == 2 and argv[1] == 'log~':
        dd.sum_up()
    elif len(argv) == 2 and argv[1] == 'query~':
        dd.query_project_duration()
    else:
        dd.content = ' '.join(argv[1:])
        dd.go()


if __name__ == '__main__':
    main()
