import inspect
import os
import sys
import threading

import requests
from colorama import deinit

from lib.controller.controller import start, task_push_from_name
from lib.core.enums import HTTPMETHOD
from lib.parse.parse_request import FakeReq
from lib.parse.parse_responnse import FakeResp
from lib.proxy.baseproxy import AsyncMitmProxy

from lib.parse.cmdparse import cmd_line_parser
from lib.core.data import logger, conf, KB
from lib.core.option import init


# python版本不能低于3.6
def version_check():
    if sys.version.split()[0] < "3.6":
        logger.error(
            "incompatible Python version detected ('{}'). To successfully run sqlmap you'll have to use version >= 3.6 (visit 'https://www.python.org/downloads/')".format(
                sys.version.split()[0]))
        sys.exit()


def modulePath():
    """
    This will get us the program's directory, even if we are frozen
    using py2exe
    """

    try:
        _ = sys.executable if hasattr(sys, "frozen") else __file__
    except NameError:
        _ = inspect.getsourcefile(modulePath)

    return os.path.dirname(os.path.realpath(_))


def main():
    # 检查版本信息
    version_check()

    # 获取绝对路径
    root = modulePath()
    # 解析命令行参数
    cmdline = cmd_line_parser()
    # 初始化执行
    init(root, cmdline)

    # 从命令行中或者文件中读取
    if conf.url or conf.url_file:
        urls = []
        # 判断命令行中是否填入了URL地址
        if conf.url:
            urls.append(conf.url)
        # 判断是否从文件中读取URL地址
        if conf.url_file:
            urlfile = conf.url_file
            if not os.path.exists(urlfile):
                logger.error("File:{} don't exists".format(urlfile))
                sys.exit()
            with open(urlfile) as f:
                _urls = f.readlines()
            _urls = [i.strip() for i in _urls]
            urls.extend(_urls)
        # 开始对每一条URL做处理，将其插入到队列中
        for domain in urls:
            # domain = "http://www.achr.net/activities-de.php?id=2"
            try:
                req = requests.get(domain)
            except Exception as e:
                logger.error("request {} faild,{}".format(domain, str(e)))
                continue
            # 解析URL地址
            fake_req = FakeReq(domain, {}, HTTPMETHOD.GET, "")
            fake_resp = FakeResp(req.status_code, req.content, req.headers)
            task_push_from_name('loader', fake_req, fake_resp)
        # 从队列中开始扫描
        start()
    # 如果是用代理模式启动
    elif conf.server_addr:
        KB["continue"] = True
        # 启动漏洞扫描器
        scanner = threading.Thread(target=start)
        scanner.setDaemon(True)
        scanner.start()
        # 启动代理服务器
        baseproxy = AsyncMitmProxy(server_addr=conf.server_addr, https=True)

        try:
            baseproxy.serve_forever()
        except KeyboardInterrupt:
            scanner.join(0.1)
            threading.Thread(target=baseproxy.shutdown, daemon=True).start()
            deinit()
            print("\n[*] User quit")
        baseproxy.server_close()


if __name__ == '__main__':
    main()
