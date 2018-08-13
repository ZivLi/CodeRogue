#!/usr/bin/env python
"""Contains constants defined for module TVA
   Created by Minh-Anh Vuong 
"""

FFT_SIZE = 4096
#for NR, 144 normal CP, which make T1 = 500 - (144+2048)/61.44*13 usec, 
# that is (500 - (144+2048)/61.44*13)*61.44 samples
CP_LEN   = 352, 288
NUM_SYM_SLOT = 14
LEN_SYM  = FFT_SIZE + CP_LEN[1]
LEN_SLOT = NUM_SYM_SLOT * LEN_SYM + CP_LEN[0] - CP_LEN[1]
#LEN_SUBF = 2 * LEN_SLOT
USED_RBS = 273
RE_RB   = 12
USED_RES = USED_RBS*RE_RB
