import time
from config import *

timezone = TIMEZONE

def lokalzeit(tz = timezone):
    
  
    add_timetupel = (0, 0, 0, tz, 0, 0, 0, 0)
    
    localzeit = tuple ( map ( sum, zip(time.localtime(), add_timetupel)))
        
    return localzeit


if __name__ == "__main__":
    
    lokalzeit()

