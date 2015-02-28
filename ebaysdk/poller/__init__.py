

class BasePoller(BaseGlue):
    base_type = 'Poller'

   def run(self):
        usage = 'usage: %prog [options]'
        parser = OptionParser(usage=usage)
        parser.add_option(
            '-s', '--settings',
            dest='settings', default='staging',
            help='specify the settings to use [default: %default]',
        )
        parser.add_option(
            '-d', '--debug', type='int',
            dest='debug', default=1,
            help='specify the debugging level [default: %default]',
        )
        parser.add_option(
            '-w', '--wait', type='int',
            dest='wait', default=0,
            help='specify the time to wait between polls [default: %default]',
        )
        parser.add_option(
            '', '--hours', type='int',
            dest='hours', default=0,
            help='specify the number of search hours [default: %default]',
        )
        (self.opts, self.args) = parser.parse_args()
        self.configure()

        try:
            while True:
                self.poll(process=self.process_wrapper)
                if self.opts.wait > 0:
                    time.sleep(self.opts.wait)
                else:
                    break
        except KeyboardInterrupt:
            pass
        self.connection.close()
        if self.agent:
            try:
                self.agent.shutdown_agent(timeout=2.5)
            except RuntimeError:
                pass

