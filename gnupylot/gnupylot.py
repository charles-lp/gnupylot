#!/usr/bin/env python
# coding: utf-8

import subprocess as sub
import tempfile as tmp

class Figure(object):

    def __init__(self, verbose=False, replot=True, interactive=True):
        """
        Constructor for Figure class.

        Parameters
        ----------
        verbose : bool, optional
            Default is False. If True, prints every gnuplot command to stdout.
        replot : bool, optional
            Default is True. If True, will add subsequent plot satements to the same 
            figure. Else, the figure is overwritten
        interactive : bool, optional
            Default is True. If True, show() will pause script until user presses
            enter. Can be set to False if output terminal is non-interactive.
        """
        self._process = sub.Popen(
            ["gnuplot"], 
            stdin=sub.PIPE, 
            # stdout=sub.PIPE, 
            # stderr=sub.PIPE
        )
        self.plot_count = 0
        self._data_files = []

        self.verbose = verbose
        self.replot = replot
        self.interactive = interactive

    def show(self):
        """
        Shows the current figure.

        Flushes the gnuplot process pipe and then waits for user input
        (i.e., script execution is paused) if interactive was set to True
        when the Figure object was created.
        """
        self._process.stdin.flush()
        if self.interactive: input()

    def _command(self, command):
        if not isinstance(command, str): raise TypeError()
        if self.verbose: print(command)
        self._process.stdin.write(command.encode() + b"\n")

    def set(self, setting):
        """
        Sends a "set" command to gnuplot.

        Parameters
        ----------
        setting : str
            The setting string to send to gnuplot, e.g. "term dumb", "xlabel 'x'", etc.
        """
        self._command("set " + setting)

    def command(self, command):
        """
        Sends a custom command to the gnuplot process.

        Parameters
        ----------
        command : str
            The command string to send to gnuplot.
        """

        self._command(command)

    def _save(self, *args):
        self._data_files.append(tmp.NamedTemporaryFile())
        len_arg0 = len(args[0])
        for arg in args: 
            if len(arg) != len_arg0: raise ValueError()
        for row in range(len_arg0):
            for arg in args:
                self._data_files[-1].write((f"{arg[row]:23.16e} ").encode())
            self._data_files[-1].write(b"\n")
        
        # print(self._data_files[-1].read())
        self._data_files[-1].flush()
        return self._data_files[-1].name

    def plot(self, x, *args, **kwargs):
        """
        Sends a "plot" or "replot" command to the gnuplot process.

        Parameters
        ----------
        x : str or array-like
            The x data to plot. If a string, it will be passed directly to gnuplot
            as a command. If an array-like, it will be saved to a temporary file
            and passed to gnuplot as a file name.
        *args : str
            Unnamed string arguments will be passed to gnuplot verbatim.
        **kwargs : str
            Named string arguments will be passed to gnuplot as options. For example,
            y="sin(x)" or title="My Plot".

        Notes
        -----
        If x is an array-like, then the first argument (if present) will be used as the
        y data. If the first argument is not present, or if the y keyword is given,
        then the y data must be given by the y keyword argument.

        Examples
        --------
        >>> fig.plot("sin(x)")
        >>> fig.plot(np.array([1,2,3]), np.array([1,2,3])**2, "u 1:2 w lp")
        >>> fig.plot(x=np.array([1,2,3]), y=np.array([1,2,3])**2, title="My Plot")
        """
        command = ""

        # Check for replot
        if self.plot_count > 0 and self.replot:
            command += "replot "
        else:
            command += "plot "

        # Check if x is a string command or array-like
        if x is None: raise ValueError()
        array_style = False
        if isinstance(x, str):
            command += x + " "
        else:
            array_style = True

        # Check if y is array-like depending on what x is
        skip_first_arg = False
        if array_style:
            if kwargs.get("y") is not None:
                data_file_name = self._save(x, kwargs["y"])
                command += f"'{data_file_name}' "
            elif args[0] is not None:
                data_file_name = self._save(x, args[0])
                command += f"'{data_file_name}' "
                skip_first_arg = True
            else:
                raise ValueError()

        # Set unnamed string args
        for argI,arg in enumerate(args):
            if skip_first_arg and argI == 0: continue
            if not isinstance(arg, str): raise TypeError()
            command += arg + " "

        # Set named args
        for key,value in kwargs.items():
            pass

        # Send command
        self._command(command)
        self.plot_count += 1

    def __enter__(self):
        return self

    def _close_data_files(self):
        for file in self._data_files: file.close()

    def close(self):
        """
        Closes the gnuplot process and associated temporary data files.

        Does not block until process terminates, but instead returns immediately.
        """
        self._close_data_files()
        self._process.terminate()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


def show(*args):
    """
    Shows the specified figures.

    Flushes the stdin of each figure's gnuplot process and waits for user input
    to continue. This pauses script execution, allowing the user to view the
    figures.
    
    Parameters
    ----------
    *args : Figure
        One or more Figure objects to be shown.
    """

    for fig in args:
        fig._process.stdin.flush()
    input()

if __name__ == "__main__":

    with Figure() as fig:
        fig.set("grid")
        fig.set("key outside top horizontal")
        fig.plot("cos(x)", "w p")
        fig.plot("sin(x)")
        fig.plot([0,1,3],[0,2,6], "u 1:2 w lp")
        fig.show()

    # with Figure() as fig:
    #     import numpy as np
    #     fig.plot(np.array([1,2,3,4,5]), np.array([1,2,3,4,5])**2, "u 1:2 w l")
    #     fig.show()

    # with Figure() as f1, Figure() as f2:
    #     f1.plot("log(x)", "w l")
    #     f2.plot("log(x**2)", "w l")
    #     show(f1, f2)