#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet
import subprocess


class Bridge(object):
    def __init__(self, cmd):
        self._command = cmd

    @property
    def value(self):
        return next(self.command_run())

    def command_run(self):
        """
            Don't use some os commands like `cmd` to start `dos`, or it's infinite loop
        """
        child = subprocess.Popen(self._command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if child.stderr:
            with child.stderr as fd_err:
                stderr = fd_err.read()
                charset = chardet.detect(stderr)['encoding']
                if charset is not None:
                    raise IOError(stderr.decode(charset).encode('utf-8'))
        with child.stdout as fd_out:
            yield fd_out.read()


if __name__ == '__main__':
    print Bridge('ls').value