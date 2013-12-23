import pandas as pd
import numpy as np

def RunMe():
    Xarray = [1,2,3,4,5]
    
    Search(Xarray)
    print Xarray;
    
def Search(Xarray):
 
    print Xarray   
    Xarray.pop(0)
    
    if Xarray != []:
        return(Search(Xarray))

def main():
    print 'Running Main Function...'
    RunMe();
    
if __name__ == '__main__':
    main()
