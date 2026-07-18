import pandas as pd
import sys
import os

def main(fname):
    df = pd.read_csv(fname)
    df = df[["Ref", "PosX", "PosY", "Side", "Rot"]]
    df.columns = ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]
    df.to_csv(os.path.join(".", "CPL.csv"), index = False)

if __name__ == "__main__":
    main(sys.argv[1])