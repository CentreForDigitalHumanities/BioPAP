"""Class for plotting"""
import mne
from pathlib import Path
from biopap.modules.base_class import BaseClass

class Plot(BaseClass):

    # https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.plot

    def __init__(self,
                 raw,
                 logger,
                 title=None,
                 save_folder=None,
                 save_postfix=None,
                 save_overwrite=False,
                 **kwargs):

        self.raw = raw
        self.processed = self.raw.copy()

        try:
            if save_folder:
                d_out = Path(save_folder)
                d_out.mkdir(parents=True, exist_ok=True)
                f_src = Path(self.raw.info['subject_info']['his_id'])

                if save_postfix:
                    f_new = Path(f_src.with_name(f'{f_src}_{save_postfix}.png').name)
                else:
                    f_new = Path(f_src.with_suffix('.png').name)

                p_out = d_out / f_new

                if not save_overwrite:
                    i = 1
                    while p_out.exists():
                        p_out = d_out / f_new.with_name(f'{f_new.stem}_({i}).png').name
                        i += 1
            else:
                p_out = None

            if isinstance(self.processed, mne.io.BaseRaw):
                events = mne.find_events(self.processed)
            else:
                events = self.processed.events

            args = {
                    'events': events,
                    'title': title,
                    'block': True,
                    'show': True,
                }

            if p_out:
                args['block'] = False
                args['show'] = False

            plot = self.processed.plot(** args | kwargs)

            if p_out:
                plot.grab().save(str(p_out))

        except Exception as e:
            logger.error(str(e))
            self.exit_code = 1

