#!/usr/bin/env python

"""Analyzes I/Q samples from RTT buffer or capture
   Created by Minh-Anh Vuong 
"""

import matplotlib.pyplot as plt, numpy as np

class TvaPlot(object):
  obj_cnt = 0
  figsize = (14, 8)
  rows, cols = 10, 32
  btn_gray = '0.85', '0.95'
  btn_red  = [0.8, 0.0, 0.0], [1.0, 0.0, 0.0]
  def __init__(self, cl_args):
    self.id = TvaPlot.obj_cnt
    TvaPlot.obj_cnt += 1
    self.args = cl_args
    self.name = '{}_slots{}'.format(self.args.tv_nam, self.args.subframes)
    self.fig = plt.figure(num=self.name, figsize=TvaPlot.figsize)
    self.events = [
        self.fig.canvas.mpl_connect('key_press_event', self.key_event),
        self.fig.canvas.mpl_connect('button_press_event', self.button_event)
      ]
  def shutdown(self):
    plt.close(self.fig)
    import sys; sys.exit(1)
  def start(self):
    from matplotlib.animation import FuncAnimation
    self.anim = FuncAnimation(self.fig, self.update, init_func=self.init,
        frames=None, interval=200, blit=False)
  def init(self):
    import matplotlib.gridspec as gridspec
    gs = gridspec.GridSpec(TvaPlot.rows, TvaPlot.cols,
        left=0.07, right=0.95, bottom=0.04, top=0.96, wspace=1.2, hspace=0.5)
    # Create TD plots
    self.IQA = []
    for r in (0, 1):
      ax = plt.subplot(gs[2*r:2*(r+1),:TvaPlot.cols//2])
      l_iq = ax.plot([], [], 'b-', [], [], 'r-.', lw=1)
      plt.locator_params(axis='y', nbins=5)
      ax.set_ylabel('RX {}: TD IQA'.format(r))
      ax.grid(True)
      ax_t = ax.twinx()
      l_acf = ax_t.plot([], [], 'y-', lw=1, alpha=0.8)
      plt.locator_params(axis='y', nbins=5)
      ax_t.set_xlim(0, self.args.sam_len/self.args.rsam_mhz)
      ax_t.set_ylim(0, 1.0)
      ax_t.yaxis.set_ticklabels([])
      self.IQA.extend(l_iq + l_acf)
    # Create PSD plots
    ax = plt.subplot(gs[0:4,TvaPlot.cols//2:])
    plt.locator_params(axis='y', nbins=5)
    ax.yaxis.tick_right()
    ax.yaxis.set_ticks_position('both')
    ax.yaxis.set_label_position('right')
    ax.set_ylabel('Spectrum')
    ax.set_xlim(-self.args.rsam_mhz/2, self.args.rsam_mhz/2)
    ax.grid(True)
    self.PSD = ax.semilogy([], [], 'b-', [], [], 'g-', lw=2)
    # Create ERG maps
    self.ERG = []
    for p in range(2):
      ax = plt.subplot(gs[p+4:(p+1)+4,:-1])
      plt.locator_params(axis='y', nbins=2)
      ax.set_ylabel('RX {}'.format(p))
      self.ERG.append(ax)
      ax = plt.subplot(gs[p+4:(p+1)+4,-1])
      self.ERG.append(ax)
    # Create DMRS plots
    mrks = 'b+', 'rx', 'g^', 'yv'
    K = len(mrks)
    self.DMRS = []
    for p in range(2):
      for q in range(0, TvaPlot.cols//2, TvaPlot.cols//8):
        ax = plt.subplot(gs[2*p+6:2*(p+1)+6,q:q+TvaPlot.cols//8])
        plt.locator_params(axis='y', nbins=5)
        plt.locator_params(axis='x', nbins=3)
        if q > 0: ax.yaxis.set_ticklabels([])
        if p == 0: ax.xaxis.set_ticklabels([])
        ax.grid(True)
        k = 0
        for s in range(self.args.slot_len):
          l = ax.scatter([], [], c=mrks[k][0], marker=mrks[k][1], alpha=0.5)
          self.DMRS.append(l)
          k = (k + 1) % K
    # Control buttons
    import matplotlib.widgets as wgt
    self.Controls = {}
    ax = plt.subplot(gs[-1,-3:])
    wg = wgt.Button(ax, 'RESTART')
    self.set_btn_color(wg, False)
    self.Controls['restart'] = wg
    ax = plt.subplot(gs[-2,-3:])
    wg = wgt.Button(ax, 'STATS')
    self.set_btn_color(wg, False)
    self.Controls['stats'] = wg
    ax = plt.subplot(gs[-3,-3:])
    wg = wgt.Button(ax, 'PAUSE')
    self.set_btn_color(wg, False)
    self.Controls['pause'] = wg
    # Other properties
    self.connected = True
    self.pause = False
    return None #self.IQA + self.PSD + self.DMRS
  def update(self, num):
    # Read and process data
    from tva import rtt_reader
    #retries = self.args.retries
    #while retries:
    #  try:
    #    data = rtt_reader.Read(self.args)
    #  except Exception as ex:
    #    print('Read() error: {}'.format(repr(ex)))
    #    retries -= 1
    #    if retries:
    #      print('Retries remaining {}'.format(retries))
    #    else:
    #      self.shutdown()
    data = rtt_reader.Read(self.args)
    ts_us, dcpx, acf, y_lim, f_mhz, psd, emaps, dmrs, timofs = self.proc(data)
    # Update front end
    self.updateIQA(ts_us, dcpx, acf, y_lim)
    self.updatePSD(f_mhz, psd, y_lim)
    self.updateERG(emaps)
    self.updateDMRS(dmrs, y_lim, timofs)
    # If bin or txt files, pause
    self.pause |= self.args.intype in ('bin', 'txt')

    if self.pause:
      self.anim.event_source.stop()
      self.set_btn_color(self.Controls['pause'], True)
    else:
      self.anim.event_source.start()
      self.set_btn_color(self.Controls['pause'], False)
    return None #self.IQA + self.PSD + self.DMRS
  def proc(self, data):
    from tva import data_proc as dp
    ts_us, dcpx, acf, y_max = dp.ProcTimeDomain(data, self.args)
    f_mhz, psd = dp.ComputePsd(dcpx, self.args)
    emaps, dmrs, timofs = dp.ProcFreqDomain(dcpx, self.args)
    y_lim = np.sqrt(2) ** np.ceil(np.log2(y_max / 45.0) * 2) * 50.0
    return ts_us, dcpx, acf, y_lim, f_mhz, psd, emaps, dmrs, timofs
  def updateIQA(self, ts_us, dcpx, acf, y_lim):
    for n in range(2):
      self.IQA[3*n+0].set_data(ts_us, dcpx[n].real)
      self.IQA[3*n+1].set_data(ts_us, dcpx[n].imag)
      self.IQA[3*n+1].axes.set_ylim(-y_lim, y_lim)
      self.IQA[3*n+2].set_data(ts_us[-len(acf[n]):], np.abs(acf[n]))
  def updatePSD(self, f_mhz, psd, y_lim):
    for i, l in enumerate(self.PSD):
      l.set_data(f_mhz, psd[i])
    l.axes.set_ylim(0.5E-3*y_lim, 20*y_lim)
  def updateERG(self, emaps):
    n_ant, n_sym, n_re = emaps.shape
    for p in range(n_ant):
      img = self.ERG[2*p].imshow(emaps[p],
          extent=[-0.5*n_re, 0.5*n_re, n_sym-0.5, -0.5],
          interpolation='none', origin='upper', aspect='auto')
      cb = plt.colorbar(img, cax=self.ERG[2*p+1])
      from matplotlib import ticker
      cb.locator = ticker.MaxNLocator(nbins=5)
      cb.update_ticks()
  def updateDMRS(self, dmrs, y_lim, timofs):
    n_ant, n_sf, n_rs, n_combs = dmrs.shape
    for p in range(n_ant):
      for q in range(n_combs):
        t = p*n_combs+q
        for s in range(n_sf):
          lh = self.DMRS[t*n_sf+s]
          rs = dmrs[p,s,:,q].reshape(-1, 1)
          lh.set_offsets(np.hstack( (rs.real, rs.imag) ))
        lh.axes.axis([-1.05*y_lim, 1.05*y_lim, -y_lim, y_lim])
        if q == 0: lh.axes.set_ylabel('RX {}: TO {:.1f}'.format(p, timofs[p]))
  def button_event(self, event):
    if event.inaxes == self.Controls['restart'].ax:
      print('RESTART clicked')
    elif event.inaxes == self.Controls['stats'].ax:
      print('STATS clicked')
    elif event.inaxes == self.Controls['pause'].ax:
      self.toggle_pause()
    else:
      print('Mouse clicked: {}'.format(event.inaxes))
  def set_btn_color(self, btn, is_active):
    if is_active:
      btn.color = TvaPlot.btn_red[0]
      btn.hovercolor = TvaPlot.btn_red[1]
    else:
      btn.color = TvaPlot.btn_gray[0]
      btn.hovercolor = TvaPlot.btn_gray[1]
  def key_event(self, event):
    from tva import consts
    if event.key in ('t', ' '):
      self.toggle_pause()
    elif event.key in ('right',):
      self.args.offset = min(self.args.offset + 8, 2*consts.LEN_SLOT - 8)
    elif event.key in ('left',):
      self.args.offset = max(self.args.offset - 8, 0)
    elif event.key in ('up',):
      self.args.offset = min(self.args.offset + 128, 2*consts.LEN_SLOT - 128)
    elif event.key in ('down',):
      self.args.offset = max(self.args.offset - 128, 0)
    elif event.key in ('pageup',):
      self.args.offset = min(self.args.offset + consts.FFT_SIZE, 2*consts.LEN_SLOT - consts.FFT_SIZE)
    elif event.key in ('pagedown',):
      self.args.offset = max(self.args.offset - consts.FFT_SIZE, 0)
    elif event.key in ('>',):
      self.args.slot_idx = min(self.args.slot_idx + 1, 100 - self.args.slot_len)
    elif event.key in ('<',):
      self.args.slot_idx = max(self.args.slot_idx - 1, 0)
    elif event.key in ('+',):
      self.args.slot_len = min(self.args.slot_len + 1, 100 - self.args.slot_idx)
    elif event.key in ('-',):
      self.args.slot_len = max(self.args.slot_len - 1, 1)
    elif event.key in '0123':
      self.args.cc_index = int(event.key)
      print('cc goes to {}'.format(self.args.cc_index))
    else:
      print('Key event "{}"'.format(event.key))
  def toggle_pause(self):
    self.pause ^= True
    if self.pause:
      self.anim.event_source.stop()
      self.set_btn_color(self.Controls['pause'], True)
    else:
      self.anim.event_source.start()
      self.set_btn_color(self.Controls['pause'], False)

def Main(cl_args):
  """Creates animation objects and allocates communication resources
  """
  # Create and start TD/FD plot
  print('Creating TVA main plot ...\r\n'),
  MainPlot = TvaPlot(cl_args)

  from tva import rtt_reader
  #data = rtt_reader.Read(MainPlot.args)
  #ts_us, dcpx, acf, y_lim, f_mhz, psd, emaps, dmrs, timofs = MainPlot.proc(data)
  MainPlot.start()
  print('done')

  # Display plots
  plt.show()

def ParseArgs(args=None):
  """Parses command line arguments
  """
  # Parse arguments
  import argparse
  parser = argparse.ArgumentParser(
      description = 'Analyzes I/Q samples from RTT buffer or capture',
      epilog      = 'Please send suggestions to <mqvuong@sc.intel.com>')
  parser.add_argument('input', nargs='+', type=str,
      help='input data file, *.bin|*.dat for binary or *.txt for text, or MTP IP address')
  parser.add_argument('-t' ,'--intype', action='store', default='', type=str,
      help='input source type, "bin", "txt", "rtt" or specify none for auto-detection')
  parser.add_argument('-f', '--subframes', action='store', default='0-2', type=str,
      help='range of subframe indices to be retrieved, specify <first>-<last>')
  parser.add_argument('--offset', action='store', default=0, type=int,
      help='offset from subframe start in samples')
  parser.add_argument('-s', '--rsam_mhz', action='store', default=122.88, type=float,
      help='sampling rate in MHz')
  parser.add_argument('-r', '--rtt_version', action='store', default=2, type=int,
      help='RTT version')
  parser.add_argument('-c', '--cc_index', action='store', default=0, type=int,
      help='selects carrier component index')
  parser.add_argument('-d', '--data_sock', action='store', default='', type=str,
      help='address and port tuple for data socket')
  parser.add_argument('-u', '--uplink', action='store_true',
      help='capture uplink data')
  parser.add_argument('--fft_backoff', action='store', default=72, type=int,
      help='backoff in samples from nominal symbol boundary for FFT input')
  parser.add_argument('--freqshift', action='store', default=3, type=int,
      help='frequence shift of SSB (floating raster). ')
  parser.add_argument('--const_symbol', action='store', default=5, type=int,
      help='on which the constellation will be generated). ')
  parser.add_argument('--gen_awg_tv', action='store_true',
      help='generate AWG test vectors from RTT content')
  parser.add_argument('--timeout', action='store', default=5.0, type=float,
      help='timeout duration for telnet and ftp sessions')
  parser.add_argument('--retries', action='store', default=10, type=int,
      help='number of retries if encountering errors reading data')
  parser.add_argument('--txt_delim', action='store', default=' ',
      help='text delimiter used for importing data from text files')
  parser.add_argument('--txt_cmnt', action='store', default='#',
      help='comment delimiter used for importing data from text files')
  parser.add_argument('--txt_skip', action='store', default=1, type=int,
      help='number of text rows to skip when importing data from text files')

  # Return
  return parser.parse_args(args)

def VerifyArgs(cl_args):
  """Verifies command line arguments
  """
  from subprocess import os

  # Auto-detect input type
  if cl_args.intype not in ('bin', 'txt', 'rtt'):
    if len(cl_args.input) == 2 \
        and os.path.splitext(cl_args.input[0])[1] in ('.txt',) \
        and os.path.splitext(cl_args.input[1])[1] in ('.txt',):
          cl_args.intype = 'txt'
          from difflib import SequenceMatcher
          a, b = [os.path.split(cl_args.input[n])[1] for n in (0, 1)]
          t = SequenceMatcher(a=a, b=b).find_longest_match(0, len(a)-4, 0, len(b)-4)
          cl_args.tv_nam = a[t.a:t.a+t.size]
    elif len(cl_args.input) == 1 \
        and os.path.splitext(cl_args.input[0])[1] in ('.bin', '.dat'):
          cl_args.intype = 'bin'
          cl_args.tv_nam = os.path.splitext(os.path.split(cl_args.input[0])[1])[0]
    else:
      cl_args.intype = 'rtt'
      cl_args.tv_nam = cl_args.input[0].replace('.', '_').replace(':', '-')

  # Make sure offset is multiple of 8
  offset = round(0.125 * cl_args.offset) * 8
  cl_args.offset = int(offset)

  # Derive index of first sample and number of samples
  if cl_args.subframes == 'all' or cl_args.gen_awg_tv:
    cl_args.slot_idx,  cl_args.slot_len  = 0, None
    cl_args.sam_1st, cl_args.sam_len = cl_args.offset, None
  else:
    idx = [int(x) for x in cl_args.subframes.split('-')]
    if len(idx) < 2:
      cl_args.slot_idx, cl_args.slot_len = idx[0], 1
    else:
      cl_args.slot_idx, cl_args.slot_len = idx[0], idx[1] - idx[0] + 1
    from tva import consts
    cl_args.sam_1st = cl_args.slot_idx * consts.LEN_SLOT + cl_args.offset
    cl_args.sam_len = cl_args.slot_len * consts.LEN_SLOT

if __name__ == '__main__':
  cl_args = ParseArgs()
  VerifyArgs(cl_args)

 # from tva import rtt_reader
 # data = rtt_reader.Read(cl_args)
  if cl_args.gen_awg_tv:
    data = rtt_reader.Read(cl_args)
    rtt_reader.GenAwgTV(data, cl_args.fnames[1:3], cl_args.rsam_mhz)
  else:
    Main(cl_args)
