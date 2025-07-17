from typing import Union
from pathlib import Path

import pandas as pd


def load_transition_temp(transition_temp_csv: Union[str, Path]) -> dict:
    """
    Loads transition_temp dict from a csv file.
    """
    transition_temp = {}
    
    if Path(transition_temp_csv).exists():
        df = pd.read_csv(transition_temp_csv)
        for i in df.index:
            transition_temp[df.loc[i, 'crystal_key']] = df.loc[i, 'transition_temp']
            
    return transition_temp