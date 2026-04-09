import mne
import matplotlib.colors as mcolors
from pathlib import Path
from typing import Union
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import OptionsBaseClass, get_new_filename


class PlotTypes(OptionsBaseClass):

    PLOT = 1
    SENSORS = 2

    def __init__(self, sel_options=0):
        super().__init__(sel_options)


class Plot(BaseClass):
    """
    Class for plotting data interactively and optionally save part of the figure.

    Displays the data using MNE's ``plot()`` method. If save options are
    provided, a screenshot of the figure is saved to disk.

    Parameters
    ----------
    raw : mne.io.Raw | mne.Epochs
        Input data.
    title : str | None
        Title of the plot window.
    plot_types : PlotTypes | None
        Types of plots to make; use | to specify multiple plot types
        (eg. PlotTypes.PLOT|PlotTypes.SENSORS)
    save_folder : str | None
        Folder in which to save the plot. If None, the figure is not saved.
    save_postfix : str | None
        Postfix appended to the plot filename.
    save_overwrite : bool, default False
        Whether to overwrite files with the same name.
    **kwargs
        Additional keyword arguments passed to MNE's ``plot()`` method.

    Attributes
    ----------
    processed : mne.io.Raw | mne.Epochs
        Output data (signal data unchanged; metadata may be modified via the interactive plot).
    """

    # https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.plot

    halt_on_exceptions = False

    def __init__(self,
                 raw,
                 plot_types: Union[str, int, list[str]]=PlotTypes.PLOT,
                 save_folder=None,
                 save_postfix=None,
                 save_overwrite=False,
                 silent: bool=False,
                 **kwargs):


        super().__init__(silent)

        with self.capture_stdout as self.stdout:

            self.raw = raw
            self.processed = self.raw.copy()

            p_kwargs = kwargs['plot'] if 'plot' in kwargs else {}
            s_kwargs = kwargs['plot_sensors'] if 'plot_sensors' in kwargs else {}

            p_types = PlotTypes(plot_types)
            stem = Path(self.raw.info['subject_info']['his_id']).stem

            if p_types.is_selected(PlotTypes.PLOT):

                if isinstance(self.processed, mne.io.BaseRaw):
                    events = mne.find_events(self.processed)
                else:
                    events = self.processed.events

                event_colors = dict(zip(events[:, 2], {k:v for k, v in \
                    mcolors.CSS4_COLORS.items() if 'white' not in k and k != 'cyan'}))
                event_colors[-1] = 'cyan'

                args = { 'block': False, 'show': False, 'events': events, 'event_color': event_colors }

                if save_folder:
                    p_out = get_new_filename(Path(f"{stem}_plot").with_suffix('.png'),
                                             save_folder,
                                             save_postfix,
                                             save_overwrite)                    
                    plot = self.processed.plot(** args | p_kwargs)
                    plot.grab().save(str(p_out))
                    print(f"wrote plot to '{p_out}'")
                else:
                    _ = self.processed.plot(** args | { 'block': True, 'show': True } | p_kwargs)

            if p_types.is_selected(PlotTypes.SENSORS):

                if save_folder:
                    p_out = get_new_filename(Path(f"{stem}_sensors").with_suffix('.png'),
                                            save_folder,
                                            save_postfix,
                                            save_overwrite)

                    plot = self.raw.plot_sensors(** { 'block': False, 'show': False } | s_kwargs)
                    plot.savefig(p_out)
                    print(f"wrote sensor plot to '{p_out}'")
                else:
                    _ = self.raw.plot_sensors(** { 'block': True, 'show': True } | s_kwargs)

