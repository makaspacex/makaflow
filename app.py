import json
import os
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from io import StringIO
from pathlib import Path

import flask
import numpy as np
import requests
from flask import Flask, request

import configs
import tools
from tools import common, subscrib, subscrib_xray
from tools.common import ClientApp, yaml
from tools.subscrib_common import start_tasks

app = Flask(__name__)


# 节点本身的操作
@app.route("/serverop/<op>")
def api_service_op(op):
    resp_data = tools.get_default_resp_data()
    try:
        res1 = tools.service_op(op, "sing-box")
        res2 = tools.service_op(op, "xray")

        resp_data["data"] = f"singbox:ok xray:ok"

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


# 节点本身的操作
@app.route("/serverlog/<service>")
def api_server_log(service):
    # parame: last_rows  default 300
    # 应该要实时返回用户的日志, 默认返回最新的300条数据
    resp_data = tools.get_default_resp_data()
    try:
        server_profile = tools.load_server_profile(service)
        log_path = server_profile["log"]["output"]
        with open(log_path, "r") as f:
            lines = f.readlines()

        last = min(len(lines), 300)
        out_str = "\n".join(lines[-last:])

        return out_str

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


# 节点本身的操作
@app.route("/serverconfig/<service>")
def api_server_config(service):
    # API接口 返回本服务器的相关配置的一些信息，需要验证统一的key
    resp_data = tools.get_default_resp_data()
    try:
        server_profile = tools.load_server_profile(service)
        config_json = tools.load_server_config(
            config_json_path=server_profile["dst_server_cfg"]
        )
        return config_json
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


@app.route("/serverstate")
def api_user_state():
    # TODO 查看服务状态和用户状态，流量等
    resp_data = tools.get_default_resp_data()
    try:
        state1 = tools.get_service_state("sing-box")
        state2 = tools.get_service_state("xray")

        data = {"service": f"singbox:{state1} xray:{state2}"}
        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


@app.route("/update_config", methods=["POST"])
def update_config():
    # 接收配置
    resp_data = tools.get_default_resp_data()
    try:
        xray_config = request.form.get("xray_config", "{}")
        singbox_config = request.form.get("singbox_config", "{}")

        xray_config = json.loads(xray_config)
        singbox_config = json.loads(singbox_config)

        common.dump_server_config(
            xray_config,
            configs.env[f"xray_server_cfg"],
        )
        common.dump_server_config(
            singbox_config,
            configs.env[f"singbox_server_cfg"],
        )
        resp_data["data"] = f"xray:ok singbox:ok"

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
        raise e
    return resp_data


# =====================================================================================
# 管理节点
@app.route("/subscrib")
def api_subscrib():
    # 返回用户的的订阅，需要检查用户名和密码，和客户端，clash_verge 支持吃v2的tls
    resp_data = tools.get_default_resp_data()
    try:
        username = request.args.get("uname", None)
        password = request.args.get("password", None)
        client_type = request.args.get("client", None)

        if client_type is None:
            user_agent = request.headers.get("User-Agent", "").lower()
            if "shadowrocket" in user_agent:
                client_type = ClientApp.shadowrocket

            # clash meta内核
            elif "clash-verge" in user_agent or "ClashX Meta" in user_agent:
                client_type = ClientApp.clashmeta

            # 含有clash关键字，但是不能有clash-verge
            elif "clash" in user_agent and "clash-verge" not in user_agent:
                client_type = ClientApp.clash

            elif "loon" in user_agent:
                client_type = ClientApp.loon
            elif "Stash" in user_agent:
                client_type = ClientApp.stash
            else:
                client_type = ClientApp.browser

        if not username or not password:
            raise Exception("miss uname or password ")

        users = configs.users

        users_dict = {ele["name"]: ele for ele in users}
        if username not in users_dict.keys():
            raise Exception("user not found")

        user_auth = users_dict[username]["auth"]
        assert user_auth == password, "password mismatch"

        # clashmeta_config = subscrib_xray.render_tp(username, client_type=client_type)
        resp_txt, resp_headers = subscrib_xray.render_tp(
            username, client_type=client_type
        )

        resp = flask.Response()
        for hname, hvalue in resp_headers.items():
            resp.headers[hname] = hvalue
        resp.headers["content-type"] = "text/yaml; charset=utf-8"
        resp.set_data(resp_txt)

        return resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)

    return resp_data


# 管理节点
@app.route("/generate_config/<service>")
def api_generate_config(service):
    # 更新服务器参数
    resp_data = tools.get_default_resp_data()
    try:
        tools.serverconfig.update(service)
    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
        raise e
    return resp_data


@app.route("/push_config")
def api_push_config():
    # 推送配置到远程节点
    resp_data = tools.get_default_resp_data()
    try:
        resp = tools.serverconfig.push_config()
        resp_data["data"] = resp

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


@app.route("/push_service_op/<op>")
def api_push_service_op(op):
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():
            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]

                push_api_url = f"{api_base}/serverop/{op}"
                resp = requests.get(push_api_url, headers={"rpckey": rpc_key})
                if resp.status_code != 200:
                    raise Exception(resp.reason)
                data[node_name] = resp.json()
            except Exception as e:
                data[node_name] = f"failed: {e}"

        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


@app.route("/get_service_status")
def api_get_service_status():
    resp_data = tools.get_default_resp_data()
    try:
        nodes = configs.env["slaver"]["nodes"]
        data = {}

        for node_name, node_conf in nodes.items():
            try:
                api_base = node_conf["api_base"]
                rpc_key = node_conf["rpc_key"]

                push_api_url = f"{api_base}/serverstate"
                resp = requests.get(push_api_url, headers={"rpckey": rpc_key})
                if resp.status_code != 200:
                    raise Exception(resp.reason)
                data[node_name] = resp.json()

            except Exception as e:
                data[node_name] = f"failed: {e}"

        resp_data["data"] = data

    except Exception as e:
        resp_data["code"] = 0
        resp_data["info"] = "Failed: " + str(e)
    return resp_data


@app.before_request
def print_request_info():
    white_list = ["/subscrib"]
    print("请求地址：" + str(request.path))
    print("请求方法：" + str(request.method))
    print("---请求headers--start--")
    print(str(request.headers).rstrip())
    print("---请求headers--end----")
    # configs.load_env()
    env = configs.env

    if str(request.path) not in white_list:
        # 验证头部auth
        auth = request.headers.get("rpckey", None)
        env = configs.env
        rpc = str(env["rpc_key"])

        if auth is None:
            return "rpckey header is none"

        if rpc != auth:
            return "rpc key error"


def get_opt():
    parser = ArgumentParser()
    parser.add_argument("--mode", type=str, default="default")
    opt = parser.parse_args()
    return opt


def main(port=8180, host="127.0.0.1"):
    start_tasks()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    env = configs.env
    opt = get_opt()

    if opt.mode != "default":
        env["mode"] = opt.mode

    port = env["port"]
    host = env["listen"]
    main(port=port, host=host)

    # api_update_server()
