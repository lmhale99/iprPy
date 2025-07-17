from typing import Union
from pathlib import Path

import pandas as pd


def save_transition_temp(transition_temp: dict,
                         transition_temp_csv: Union[str, Path]):
    """
    Saves the transition_temp dict to a csv file.
    """
    df = pd.DataFrame({'crystal_key':list(transition_temp.keys()), 'transition_temp':list(transition_temp.values())})
    df.to_csv(transition_temp_csv, index=False)