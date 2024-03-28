from sql import Database


def task_top_files(db):
    """Most viewed files"""
    limit = int(a) if (a:=input("Limit (10): ")) else 10
    data = db.get_top_files(limit)
    db.print_files(data)


def task_recent_files(db):
    """Recent files"""
    limit = int(a) if (a:=input("Limit (10): ")) else 10
    data = db.get_recent_files(limit)
    db.print_files(data)


def task_mimetype_files(db):
    """Search by mimetype"""
    mimetype = input("Mimetype: ")
    limit = int(a) if (a:=input("Limit (10): ")) else 10
    data = db.get_mimetype_files(mimetype, limit)
    db.print_files(data)


def run():
    tasks = tuple(map(lambda item: item[1], filter(lambda item: item[0].startswith("task_"), globals().items())))
    db = Database()
    while True:
        print("\n".join(map(lambda item: f"{item[0]+1}. {item[1].__doc__}", enumerate(tasks))))
        task = tasks[int(input(">>> "))-1]
        task(db)
        input("...")


if __name__ == "__main__":
    run()
