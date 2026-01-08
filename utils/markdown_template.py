import re
from django.template import Template, Context
from typing import List, Dict


def parse_complex_log(raw_text: str) -> List[Dict[str, str]]:
    """将 Git Changelog 文笔处理为结构化数据"""
    max_msg_length = 40
    authors = []
    current_author = None
    lines = raw_text.strip().split('\n')

    # 匹配范围文本行
    range_re = re.compile(r"^From: (\w+)\.+(\w+)$")
    # 匹配作者行: "- name (count):"
    author_re = re.compile(r"^- (.+) \((\d+)\):")
    # 匹配提交行: "    hash message"
    commit_re = re.compile(r"^\s+([a-f0-9]{7,9})\s+(.*)")

    for line in lines:
        range_match = range_re.match(line.strip())
        if range_match:
            current_author = {
                "from_start": range_match.group(1),
                "from_end": range_match.group(2)
            }
            authors.append(current_author)
            continue

        a_match = author_re.match(line.strip())
        if a_match:
            current_author = {
                "name": a_match.group(1),
                "count": a_match.group(2),
                "commits": []
            }
            authors.append(current_author)
            continue

        c_match = commit_re.match(line)  # 注意这里不要 strip，因为需要判断缩进
        if c_match and current_author is not None:
            current_author["commits"].append({
                "id": c_match.group(1),
                "msg": re.sub(r" +", " ", c_match.group(2).strip()),
            })
        elif current_author and current_author["commits"]:
            # 处理多行注释的情况：补在前一个 commit 的 msg 后面
            current_author["commits"][-1]["msg"] += " " + line.strip()
        if "msg" in current_author["commits"][-1] and len(current_author["commits"][-1]["msg"]) >= max_msg_length:
            ## replace " +" to " "
            msg = current_author["commits"][-1]["msg"][:max_msg_length] + "..."
            current_author["commits"][-1]["msg"] = msg

    return authors


def render_git_log_to_md(raw_text):
    # 1. 结构化数据 (解析逻辑同前)
    # 这里假设我们已经得到了 structured_data = {"range": "...", "authors": [...]}
    structured_data = parse_complex_log(raw_text)

    # 2. 定义 Django 模板字符串
    template_str = """
### 🚀 代码更新日志
**版本范围**: `{{ log_data.0.from_start }}` › `{{ log_data.0.from_end }}`

---{% for author in log_data|slice:"1:" %}
#### 👨🏻‍💻 {{ author.name }} ({{ author.count }})
{% for c in author.commits %}- `{{ c.id }}` {{ c.msg }}
{% endfor %}{% endfor %}
    """

    # 3. 使用 Django Context 渲染
    t = Template(template_str)
    c = Context({"log_data": structured_data})
    return t.render(c)


if __name__ == '__main__':
    raw_data = '''
From: f6811dea..HEAD
- user1 (1):
    823dd4fb5 feat(亲密关系): feat1

- user2 (3):
    6928e5f2d feat2.0
    a924adf33 feat2.1
    123e8b054 feat2.2'''

    print(render_git_log_to_md(raw_data))