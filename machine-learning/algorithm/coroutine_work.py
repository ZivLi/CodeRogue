from collections import deque

def student(name, homeworks):
    for homework in homeworks.items():
        yield (name, homework[0], homework[1])


class Teacher(object):

    def __init__(self, students):
        self.students = deque(students)

    def handle(self):
        while len(self.students):
            student = self.students.pop()
            try:
                homework = next(student)
                print 'handling', homework[0], homework[1], homework[2]
            except StopIteration:
                pass
            else:
                self.students.appendleft(student)


if __name__ == '__main__':
    Teacher([
            student('Student1', {'math': '1+1=2', 'cs': 'operating system'}),
            student('Student2', {'math': '2+2=4', 'cs': 'computer graphics'}),
            student('Student3', {'math': '3+3=5', 'cs': 'compiler construction'})
    ]).handle()
