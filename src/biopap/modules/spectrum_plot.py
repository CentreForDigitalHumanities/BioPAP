import mne
from dataclasses import dataclass
from pathlib import Path
from biopap.modules.base_class import BaseClass
from biopap.modules.helpers import get_new_filename

class SpectrumPlot(BaseClass):

    def __init__(self,
                 raw,
                 plots_to_save=[],
                 save_folder=None,
                 save_postfix=None,
                 save_overwrite=False,
                 silent: bool=False,
                 **kwargs):
        # power spectral density (PSD) 
        super().__init__(silent)

        with self.capture_stdout as self.stdout:
            self.raw = raw
            self.processed = self.raw.copy()
            self.spectrum = raw.compute_psd()

            self.save_folder = Path(save_folder)
            self.save_postfix = save_postfix
            self.save_overwrite = save_overwrite

            if len(plots_to_save)>0 and save_folder is None:
                raise ValueError('need a save_folder for saving plots')

            s_kwargs = kwargs['spectrum_plot'] if 'spectrum_plot' in kwargs else {}
            t_kwargs = kwargs['topo'] if 'topo' in kwargs else {}
            m_kwargs = kwargs['topo_map'] if 'topo_map' in kwargs else {}

            if 'spectrum_plot' in plots_to_save:
                self.spectrum_plot(save=True, **s_kwargs)

            if 'topo' in plots_to_save:
                self.topo(save=True, **t_kwargs)

            if 'topo_map' in plots_to_save:
                self.topo_map(save=True, **m_kwargs)

    def spectrum_plot(self, save=False, **kwargs):
        # self.spectrum.plot(exclude='bads', amplitude=False, **kwargs)
        img = self.spectrum.plot(show=not save, **kwargs)
        if save:
            img.savefig(
                get_new_filename('spectrum.png',
                    self.save_folder,
                    self.save_postfix,
                    self.save_overwrite)
                )

    def topo(self, save=False, **kwargs):
        img = self.spectrum.plot_topo(show=not save, **kwargs)
        if save:
            img.savefig(
                get_new_filename('topo.png',
                    self.save_folder,
                    self.save_postfix,
                    self.save_overwrite)
                )

    def topo_map(self, save=False, **kwargs):
        # self.spectrum.plot_topomap(**kwargs)
        img = self.spectrum.plot_topomap(show=not save, **kwargs)
        if save:
            img.savefig(
                get_new_filename('topomap.png',
                    self.save_folder,
                    self.save_postfix,
                    self.save_overwrite)
                )
