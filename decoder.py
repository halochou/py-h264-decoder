from bitstring import BitArray, BitStream
from h264bits import H264Bits
from nalsps import SPS
from nalpps import PPS
from nalslice import Slice
from pprint import pprint

input_file = open("baseline.264", "rb")
nalus_ba = list(BitArray(input_file).split('0x000001', bytealigned=True))[1:]
sps = []
pps = []
slices = []
for nalu_ba in nalus_ba:
    nalu_ba.replace('0x000003', '0x0000', bytealigned=True)
    nalu_bs = BitStream(nalu_ba)
    nb = H264Bits(nalu_bs)
    params = {"forbidden_zero_bit" : nb.f(1),
              "nal_ref_idc" : nb.u(2),
              "nal_unit_type" : nb.u(5)}
    if params["nal_unit_type"] == 7: # SPS
        sps = SPS(nb, params = params)
    elif params["nal_unit_type"] == 8: # PPS
        pps.append(PPS(nb, sps = sps, params = params))
    elif params["nal_unit_type"] in [1, 5]: # Slice
        slices.append(Slice(nb, sps = sps, pps = pps, params = params))
    else:
        print("Unknown Slice type, ignore...")

# nalus = [NalUnit(nalu_bit) for nalu_bit in nalus_bit]
input_file.close()
