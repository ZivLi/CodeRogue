class DummyResource:

    def __init__(self, tag):
        self.tag = tag
        print 'Resource [%s]' % tag

    def __enter__(self):
        print '[Enter %s]: Allocate resource.' % self.tag
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        print '[Exit %s]: Free resource.' % self.tag
        if exc_tb is None:
            print '[Exit %s]: Exited without exception.' % self.tag
        else:
            print '[Exit %s]: Exited with exception raised.' % self.tag
            return False


def dummy_resource_normal():
    with DummyResource('Normal'):
        print '[with-body] Run without exceptions.'


def dummy_resource_with_exception():
    with DummyResource('With-Exception'):
        print '[with-body] Run with exception.'
        raise Exception
        print '[with-body] Run with exception. Failed to finish statement-body!'


def main():
    dummy_resource_normal()
    dummy_resource_with_exception()


if __name__ == '__main__':
    main()
