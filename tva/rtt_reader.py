#!/usr/bin/env python
"""Contains a number of methods to retrieve I/Q samples from RTT buffer or capture
   Created by Minh-Anh Vuong 
"""
#import pdb
import numpy as np
from . import consts

PROMPTS = '[vxWorks *]# ', '-> '
RTT_PATH = '/ata0:1', 'rtt.bin'

def Read(args):
  """Reads I/Q samples from RTT or capture
  """
  args.sam_1st = args.slot_idx * consts.LEN_SLOT + args.offset
  if args.intype == 'bin':
    data = ReadBinFile(args.input[0], args.cc_index, args.rtt_version)\
        [:,:,args.sam_1st:args.sam_1st+args.sam_len]
  elif args.intype == 'txt':
    data = ReadTxtFile(args.input[:2], args.txt_delim, args.txt_cmnt, args.txt_skip)\
        [:,:,args.sam_1st:args.sam_1st+args.sam_len]
  else:
    data = ReadRttBuffer(args.input[0], args.sam_1st, args.sam_len,
        args.cc_index, args.rtt_version, args.uplink, args.timeout)

  # Return
  return data

def ReadRttBuffer(ipaddr, sam_1st, sam_len, cc_id, rtt_ver, uplink, timeout):
  """Initiates an RTT capture then reads from DDR
  """
  if sam_1st < 0 or (sam_1st & 7) != 0 \
      or sam_len < 1 or (sam_len & 7) != 0 \
      or 30720*100 < (sam_1st + sam_len):
    raise Exception('Invalid SF index or length requested!')

  # Initiate an RTT capture
  CaptureRtt(ipaddr, sam_1st, sam_len, cc_id, rtt_ver, uplink, timeout)

  # Retrieve the RTT capture file
  FetchRttFile(ipaddr, timeout)

  # Read from capture file
  data = ReadBinFile(RTT_PATH[1], cc_id, rtt_ver)

  # Return data
  return data

def CaptureRtt(ipaddr, sam_1st, sam_len, cc_id, rtt_ver, uplink, timeout):
  """Telnets to MTP and initiates an RTT capture
  """
  # Error checking
  if rtt_ver not in (1, 2):
    raise Exception('Invalid RTT version!')

  # Parameters
  sam_bytes = 4 * 2     # 4 bytes/word * 2 ants
  if rtt_ver == 2:
    sam_bytes *= 2      # 2 CCs per capture
  ddr_start, ddr_bytes = sam_1st * sam_bytes, sam_len * sam_bytes

  # Capture control registers
  if rtt_ver == 2 and cc_id & 2:
    reg201 = 0x0032     # {CC3, CC2}
  else:
    reg201 = 0x0010     # {CC1, CC0} if RTT v2 or {Im1, Re1, Im0, Re0} o.w.

  if uplink:
    reg201 = reg201 | 0x44     # fmtu_sync=1, arm_capture=1, capture COM5 TX
 

  # Telnet to MTP
  import telnetlib
  telnet = telnetlib.Telnet(ipaddr, timeout=timeout)
  telnet.read_until(PROMPTS[0], timeout=timeout)
  telnet.write('cd {}\r\n'.format(RTT_PATH[0]))
  telnet.read_until(PROMPTS[0], timeout=timeout)

  # Initiate capture
  telnet.write('C\r\n')
  telnet.read_until(PROMPTS[1], timeout=timeout)
  rmi_reg_val = [   [ 0x201, reg201 ] ]
  for rv in rmi_reg_val:
    telnet.write('hiphy_rmi_write_32({}, {})\r\n'.format(*rv))
    telnet.read_until(PROMPTS[1], timeout=timeout)

  # Dump DDR to file
  telnet.write('hiphy_ddr_rtf({}, {}, "{}")\r\n'.format(ddr_start, ddr_bytes, RTT_PATH[1]))
  telnet.read_until(PROMPTS[1], timeout=timeout)

  # Close telnet session
  telnet.close()

def FetchRttFile(ipaddr, timeout):
  """Connects to MTP using FTP and fetches the captured RTT file
  """
  # FTP to MTP
  import ftplib
  ftp = ftplib.FTP(host=ipaddr, timeout=timeout)
  ftp.login()
  ftp.cwd(RTT_PATH[0])
  with open(RTT_PATH[1], 'wb') as fh:
    ftp.retrbinary('RETR {}'.format(RTT_PATH[1]), fh.write)

  # Close FTP session
  try: ftp.quit()
  except: ftp.close()

def ReadBinFile(fname, cc_id, rtt_ver):
  """Reads samples from a binary RTT capture file
  """
  # Reads little-endian 32-bit integers from file
  i32s = np.fromfile(fname, '<i4')

  # Extract data
  data = ExtractRttData(i32s)

  # Return data
  if rtt_ver == 1: return data
  return data[:,:,(cc_id&1)::2]

def ExtractRttData(i32s):
  """Extracts I/Q samples from a string representing the RTT content or capture

  The RTT content consists of a sequence of 256-bit words.
  Each word contains eight 32-bit samples resulted from interlacing two RX streams.
  Each 32-bit sample is composed of, MSB to LSB, 8 padding 0's, 12-bit Q and 12-bit I.

  Below is a graphical representation of the RTT content.
  Each rectangular box represents a 32-bit word.
  The order of 32-bit words are from top-left and increases row-wise
  then next row.
  Obviously, the correct retrieval of data from the file necessitates
  a word reordering within a 256-bit row.

  ,--------,--------,--------,--------,--------,--------,--------,--------,
  | rx1[3] | rx0[3] | rx1[2] | rx0[2] | rx1[1] | rx0[1] | rx1[0] | rx0[0] |
  :--------:--------:--------:--------:--------:--------:--------:--------:
  | rx1[7] | rx0[7] | rx1[6] | rx0[6] | rx1[5] | rx0[5] | rx1[4] | rx0[4] |
  :--------'--------'--------'--------'--------'--------'--------'--------'
  | . . .
  """
  # Retrieve all samples as little endian 32-bit integers
  # and reverse order of samples per groups of consecutive eight
  Nmax = ((len(i32s)-2) >> 3) << 3
  #print("expect number of bytes %d. size of the file %d\r\n" %(Nmax*4, i32s[1]))
  sams = i32s[2:Nmax+2].reshape(-1, 8)[:,::-1].flatten()

  # Extract Q (bits 11-0) and I (bits 23-12)
  # then regroup into RX0 I/Q and RX1 I/Q
  data = np.array([ [ (sams[0::2] << 8) >> 20, (sams[0::2] << 20) >> 20 ],
                    [ (sams[1::2] << 8) >> 20, (sams[1::2] << 20) >> 20 ]], np.float64)
  sfn = ((sams[0]>>24&0xFF)<<24)|((sams[1]>>24&0xFF)<<16)|((sams[2]>>24&0xFF)<<8)|((sams[3]>>24&0xFF));
  print("Current SFN is {}".format(sfn&0xFFFFFFFF));
  # Format and return data
  return data

def ReadTxtFile(fnames, delim, cmnt, skip):
  """Reads samples from two 2-column text files
  """
  # Make sure there are 2 files
  if len(fnames) != 2:
    raise Exception('Requiring 2 files, one per antenna')

  # Return data combined from two antennas
  return np.append(
      [np.loadtxt(fnames[0], delimiter=delim, comments=cmnt, skiprows=skip).T],
      [np.loadtxt(fnames[1], delimiter=delim, comments=cmnt, skiprows=skip).T],
      axis=0)

def GenAwgTV(data, fnames, rate_mhz):
  """Writes samples to a two-column text file in the format ready for AWG
  """
  # Make sure there are 2 files
  if len(fnames) != 2:
    raise Exception('Requiring 2 files, one per antenna')

  # Normalize data values
  data_f = data * 0.05 / np.mean(np.std(data, axis=-1))
  data_f[data_f >  0.9999] =  0.9999
  data_f[data_f < -0.9999] = -0.9999

  # Write to file
  for f, x in zip(fnames, data_f):
    np.savetxt(f, x.T, fmt='% .10f', delimiter=', ',
        header='SampleRate = {} MHz'.format(rate_mhz), comments='')

  # Return
  return

def Main(args):
  """Main function
  """
  print(args)

def ParseArgs(args=None):
  """Parses command line arguments
  """
  # Parse arguments
  import argparse
  parser = argparse.ArgumentParser(
      description = 'Generates AWG test vector for RTT capture',
      epilog      = 'Please send suggestions to <mqvuong@sc.intel.com>')
  parser.add_argument('input', nargs='+', type=str,
      help='input data file, *.bin|*.dat for binary or *.txt for text, or MTP IP address')

  # Return
  return parser.parse_args(args)

if __name__ == '__main__':
  cl_args = ParseArgs()
  Main(cl_args)
