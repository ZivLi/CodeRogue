import redis, time

def handle(task):
    print task
    time.sleep(4)

def main():
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    while 1:
        result = r.brpop(['high_task_queue', 'tasklist'], 0)
        handle(result[1])


if __name__ == '__main__':
    main()
