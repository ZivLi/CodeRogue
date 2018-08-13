#!/usr/bin/env python
"""Contains a number of data processing functions
   Created by Minh-Anh Vuong 
"""

import numpy as np
from . import consts

def ProcTimeDomain(data, args):
  """Computes ACF and RMS values
  """
  # Sampling time in microsecs
  ts_us = np.arange(data.shape[-1]) / args.rsam_mhz

  # Complex-valued signals
  dcpx = np.vstack( (data[0,0] + 1j*data[0,1],
                     data[1,0] + 1j*data[1,1]) )

  # Auto-correlation functions
  from scipy.signal import lfilter
  acf = lfilter(np.ones(consts.CP_LEN[1]), consts.CP_LEN[1],
      dcpx[:,:-consts.FFT_SIZE].conj() * dcpx[:,consts.FFT_SIZE:]) / np.var(dcpx)

  # Return
  return ts_us, dcpx, acf, np.max(np.abs(data))

def ComputePsd(dcpx, args):
  """Computes power spectrum density data
  """
  # Compute Welch PSD
  from scipy.signal import welch
  f, P = welch(dcpx, fs=args.rsam_mhz, nfft=consts.FFT_SIZE, axis=-1)

  # Return
  return np.fft.fftshift(f, axes=-1), np.fft.fftshift(P, axes=-1)

def ProcFreqDomain(dcpx, args):
  """Computes energy maps
  """
  # Compute frequency domain symbols
  backoff = consts.CP_LEN[1]//2
  # for NR, slot contains 14 symbols for normal cp
  slots = dcpx.reshape(2, -1, consts.LEN_SLOT)[:,:,-consts.NUM_SYM_SLOT*consts.LEN_SYM:]
  fft_i = slots.reshape(2, -1, consts.LEN_SYM)[:,:,-consts.FFT_SIZE-backoff:-backoff]
  fft_s = np.dstack( (fft_i[:,:,backoff:], fft_i[:,:,:backoff]) )
  fft_o = np.fft.fft(fft_s, axis=-1) / np.sqrt(consts.FFT_SIZE)

  # Energy maps
  emaps = np.dstack( ( fft_o[:,:,-(consts.USED_RES//2+12):],
                       fft_o[:,:,:(consts.USED_RES//2+13)] ) )

  # Process DMRS
  dmrs, timofs = ProcDmrs(fft_o, args)

  # Return
  return np.abs(emaps), dmrs, timofs

def ProcDmrs(fft_o, args):
  """Processes DMRS
  """
  # Extract used REs and DMRS
  used_res = np.dstack( ( fft_o[:,:,-(consts.USED_RES//2):],
                          fft_o[:,:,0:(consts.USED_RES//2)] ) )
  # take consideration of floating raster
  dmrs = used_res[:,args.const_symbol::14,(consts.USED_RES//2)-(10*consts.RE_RB)-2*args.freqshift:(consts.USED_RES//2)+(10*consts.RE_RB)-2*args.freqshift]
  n_ant, n_subf, n_re = dmrs.shape
  n_combs = 4

  # Estimate timing offset
  dmr4 = dmrs ** 4
  phx_dy = dmr4[:,:,n_combs:] * dmr4[:,:,:-n_combs].conj()
  timofs = np.angle(np.sum(phx_dy, axis=(1,2))) * consts.FFT_SIZE / (8 * np.pi * n_combs)

  # Correct for timing offset
  re_idx = timofs.reshape(-1, 1).dot(
      np.append(range(-n_re>>1, 0), range(1, n_re//2+1)).reshape(1, -1))
  phasor = np.exp(-2j * np.pi * re_idx / consts.FFT_SIZE)
  dmrs[0] *= np.tile(phasor[0], (n_subf, 1))
  dmrs[1] *= np.tile(phasor[1], (n_subf, 1))

  # Return
  return dmrs.reshape(n_ant, n_subf, -1, n_combs), timofs
