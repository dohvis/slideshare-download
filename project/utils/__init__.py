def get_tasks():
    from requests import get
    data = get("http://localhost:5555/api/tasks?result").json()
    return list(data.keys())
