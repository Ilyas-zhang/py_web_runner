"""
教学网页后端 - 接收Python代码并在本地解释器中执行
支持 matplotlib 画图（自动捕获为 base64 图片返回前端）
支持代码编辑器：保存/读取/运行/删除 .py 文件
"""
from flask import Flask, request, jsonify, send_file
import subprocess
import sys
import tempfile
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 代码保存目录 —— 放在项目同级目录下，避免 git pull 冲突
# 即 ~/code/，与 ~/py-web-runner/ 平级
CODE_DIR = Path(__file__).parent.parent / "code"
CODE_DIR.mkdir(exist_ok=True)

# 文件名安全校验：只允许 字母/数字/下划线/连字符/中文 + .py
_SAFE_NAME_RE = re.compile(r"^[\w一-鿿\-]+\.py$", re.UNICODE)


def _validate_filename(name: str) -> str:
    """校验并规范化文件名，返回安全的 .py 文件名。异常时返回空串。"""
    name = name.strip()
    if not name:
        return ""
    # 用户可能带了 .py 后缀，也可能没带
    if not name.endswith(".py"):
        name += ".py"
    if not _SAFE_NAME_RE.match(name):
        return ""
    return name


# matplotlib 图片捕获包装代码
WRAPPER_PREFIX = textwrap.dedent("""\
    import os, sys, io, base64
    os.environ["MPLBACKEND"] = "Agg"
    __captured_images__ = []
    __real_print__ = print
""")

WRAPPER_SUFFIX = textwrap.dedent("""\
    # 自动捕获 matplotlib 图片
    try:
        import matplotlib.pyplot as __plt__
        if __plt__.get_fignums():
            for __i__, __fnum__ in enumerate(__plt__.get_fignums()):
                __fig__ = __plt__.figure(__fnum__)
                __buf__ = io.BytesIO()
                __fig__.savefig(__buf__, format="png", dpi=120, bbox_inches="tight")
                __buf__.seek(0)
                __b64__ = base64.b64encode(__buf__.read()).decode()
                __real_print__(f"__IMG_{__i__}__{__b64__}__END_IMG__")
            __plt__.close("all")
    except ImportError:
        pass
""")


def _execute_code(code: str) -> dict:
    """执行一段 Python 代码（带 matplotlib 包装），返回结果字典。"""
    wrapped = WRAPPER_PREFIX + "\n" + code + "\n" + WRAPPER_SUFFIX
    try:
        result = subprocess.run(
            [sys.executable, "-c", wrapped],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=tempfile.gettempdir(),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "⏱ 运行超时（15秒限制），请检查是否有死循环",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"执行错误: {e}",
            "returncode": -1,
        }


# ==================== 页面路由 ====================

@app.route("/")
def index():
    return send_file("index.html")


# ==================== 代码运行 ====================

@app.route("/run", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    if not code.strip():
        return jsonify({"stdout": "", "stderr": "（代码为空）", "returncode": 0})
    return jsonify(_execute_code(code))


# ==================== 文件编辑器 API ====================

@app.route("/files", methods=["GET"])
def list_files():
    """列出 code/ 目录下所有 .py 文件及修改时间"""
    files = []
    for p in sorted(CODE_DIR.glob("*.py")):
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        files.append({
            "name": p.name,
            "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return jsonify(files)


@app.route("/files/<name>", methods=["GET"])
def get_file(name):
    """读取指定 .py 文件内容"""
    safe = _validate_filename(name)
    if not safe:
        return jsonify({"error": "文件名不合法"}), 400
    fpath = CODE_DIR / safe
    if not fpath.exists():
        return jsonify({"error": "文件不存在"}), 404
    mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
    return jsonify({
        "name": safe,
        "code": fpath.read_text(encoding="utf-8"),
        "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.route("/save", methods=["POST"])
def save_file():
    """保存代码到 code/ 目录"""
    data = request.json or {}
    filename = data.get("filename", "")
    code = data.get("code", "")
    safe = _validate_filename(filename)
    if not safe:
        return jsonify({"ok": False, "error": "文件名不合法（仅允许字母、数字、下划线、连字符、中文）"}), 400
    fpath = CODE_DIR / safe
    fpath.write_text(code, encoding="utf-8")
    return jsonify({"ok": True, "filename": safe})


@app.route("/run-file", methods=["POST"])
def run_file():
    """运行 code/ 目录下已保存的 .py 文件"""
    data = request.json or {}
    filename = data.get("filename", "")
    safe = _validate_filename(filename)
    if not safe:
        return jsonify({"stdout": "", "stderr": "文件名不合法", "returncode": -1}), 400
    fpath = CODE_DIR / safe
    if not fpath.exists():
        return jsonify({"stdout": "", "stderr": "文件不存在", "returncode": -1}), 404
    code = fpath.read_text(encoding="utf-8")
    if not code.strip():
        return jsonify({"stdout": "", "stderr": "（代码为空）", "returncode": 0})
    return jsonify(_execute_code(code))


@app.route("/files/<name>", methods=["DELETE"])
def delete_file(name):
    """删除 code/ 目录下的 .py 文件"""
    safe = _validate_filename(name)
    if not safe:
        return jsonify({"ok": False, "error": "文件名不合法"}), 400
    fpath = CODE_DIR / safe
    if not fpath.exists():
        return jsonify({"ok": False, "error": "文件不存在"}), 404
    fpath.unlink()
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("=" * 50)
    print("  教学网页服务器启动中...")
    print("  代码保存目录:", CODE_DIR)
    print("  请在浏览器打开: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=False, host="127.0.0.1", port=5000)
