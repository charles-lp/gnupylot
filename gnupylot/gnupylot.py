#!/usr/bin/env python
# coding: utf-8

import subprocess as sub
import tempfile as tmp

class Figure(object):

    def __init__(self, verbose=False, replot=False, interactive=True):
        """
        Parameters
        ----------
        verbose : bool
            If set to True, commands sent to gnuplot are printed to the console.
        replot : bool
            If set to True, subsequent plot commands will replot the same figure 
            window, rather than creating a new one.
        interactive : bool
            If set to False, script execution will not pause after showing a figure.
        """
        
        self.command = b""
        self._process = sub.Popen(
            ["gnuplot"], 
            stdin=sub.PIPE, 
            # stdout=sub.PIPE, 
            # stderr=sub.PIPE
        )
        self._data_files = []
        self._replot_active = False

        self.verbose = verbose
        self.interactive = interactive
        self.replot = replot 

    def show(self):
        """
        Shows the current figure.

        Flushes the gnuplot process pipe and then waits for user input
        (i.e., script execution is paused) if interactive was set to True
        when the Figure object was created.
        """
        if self.verbose: print(self.command)
        self._process.stdin.write(self.command)
        self._process.stdin.flush()
        if self.interactive: input()

    def _command(self, command):
        if not isinstance(command, str): raise TypeError()
        if self.verbose: print(command)
        self.command += command.encode() + b"\n"

    def set(self, setting):
        """
        Sends a "set" command to gnuplot.

        Parameters
        ----------
        setting : str
            The setting string to send to gnuplot, e.g. "term dumb", "xlabel 'x'", etc.
        """
        self._command("set " + setting)

    def unset(self, setting):
        """
        Sends a "unset" command to gnuplot.

        Parameters
        ----------
        setting : str
            The setting string to send to gnuplot, e.g. "border", "tics", "key", etc.
        """
        self._command("unset " + setting)

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

    def plot(self, x, y=None, *args, **kwargs):
        """
        Plot a 2D graph

        Parameters
        ----------
        x : str or array-like
            The x values to plot. If a string, it should be a valid gnuplot command
            (e.g. "'sin(x)'"). If an array-like, it should be an array of x values to
            plot. If only one array-like is provided, it is plotted against its index.
        y : array-like, optional
            The y values to plot. Should be an array of the same length as x.
        *args : str
            Additional arguments to pass to the gnuplot "plot" command.
        **kwargs : str
            Additional keyword arguments to pass to the gnuplot "plot" command.

        Returns
        -------
        None
        """
        command = ""

        if self.replot and self._replot_active:
            command += "replot "
        else:
            command += "plot "

        # Check if x is a string command or array-like
        if x is None: raise ValueError()
        x_array_like = False
        if isinstance(x, str):
            command += x + " "
        else:
            x_array_like = True

        # Check if y is array-like depending on what x is
        if x_array_like:
            if y is not None:
                data_file_name = self._save(x, y)
                command += f"'{data_file_name}' "
            elif args[0] is not None:
                data_file_name = self._save(x, args[0])
                command += f"'{data_file_name}' "
                args = tuple(args[i] for i in range(1, len(args)))
            else:
                raise ValueError()

        # Set unamed args
        for arg in args:
            command += f"{arg} "

        # Set named args
        for key,value in kwargs.items():
            command += f"{key} {value} "

        # Send command
        self._command(command)
        self._replot_active = True

    def splot(self, x, y=None, z=None, *args, **kwargs):
        """
        Plot a 3D graph or surface plot

        Parameters
        ----------
        x : array-like or str
            If array-like, the x values to plot. If str, a string command
            to send to gnuplot. Requires y and z arguments.
        y : array-like, optional
            The y values to plot. Ignored if x is a string.
        z : array-like, optional
            The z values to plot. Ignored if x is a string.
        *args : array-like, optional
            Additional array-like arguments to send to gnuplot.
        **kwargs : str, optional
            Additional string arguments to send to gnuplot.
        """
        command = ""

        if self.replot and self._replot_active:
            command += "replot "
        else:
            command += "splot "

        # Check if x is a string command or array-like
        if x is None: raise ValueError()
        x_array_like = False
        if isinstance(x, str):
            command += x + " "
        else:
            x_array_like = True

        # Check if y is array-like depending on what x is
        if x_array_like:
            if y is not None and z is not None:
                data_file_name = self._save(x, y)
                command += f"'{data_file_name}' "
            elif args[0] is not None and args[1] is not None:
                data_file_name = self._save(x, args[0])
                command += f"'{data_file_name}' "
                args = tuple(args[i] for i in range(2, len(args)))
            else:
                raise ValueError()

        # Set unamed args
        for arg in args:
            command += f"{arg} "

        # Set named args
        for key,value in kwargs.items():
            command += f"{key} {value} "

        # Send command
        self._command(command)
        self._replot_active = True

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

        # Necessary to ask gnuplot directly to quit, else the window might stay opened
        # even after SIGTERM/SIGKILL is sent
        self._process.stdin.write("q\n")
        self._process.stdin.flush()
        
        self._process.terminate()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


def show(*args, interactive=True):
    """
    Shows all figures given as arguments.

    Parameters
    ----------
    *args : Figure
        The figures to show.
    interactive : bool, optional
        If set to True (default), script execution will pause after showing
        all figures.
    """
    for fig in args:
        fig._process.stdin.write(fig.command)
        fig._process.stdin.flush()
    if interactive: input()

if __name__ == "__main__":
    with Figure() as fig:
        fig.replot = True
        fig.set("grid")
        fig.set("key outside top horizontal")
        fig.plot("sin(x)", dashtype=0)
        fig.plot(x=[0,1], y=[0,0.5], w="lines", linecolor=" 'red'")
        fig.show()

    with Figure() as fig1, Figure() as fig2:
        fig1.plot("x**2")

        fig2.set("hidden3d")
        fig2.set("isosamples 50")
        fig2.splot("sin(x)*cos(y)")

        show(fig1, fig2)
