

from common import BasePoller


class Poller(BasePoller):

    def poll(self):
        pass

    def process(self):
        pass

if __name__ == '__main__':
    poller = Poller()
    poller.run()