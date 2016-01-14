def get_tasks():
    from requests import get
    data = get("http://layer7.kr:5555/api/tasks?result").json()
    return list(data.keys())
