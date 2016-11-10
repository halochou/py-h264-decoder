from bitstring import BitStream
from h264bits import H264Bits
from nalsps import SPS
from nalpps import PPS
from nalslice import Slice
from pprint import pprint

input_file = open("test.264", "rb")
nalus_bs = list(BitStream(input_file).split('0x00000001', bytealigned=True))[1:]
sps = []
pps = []
slices = []
for nalu_bs in nalus_bs:
    nb = H264Bits(nalu_bs)
    params = {"forbidden_zero_bit" : nb.f(1),
              "nal_ref_idc" : nb.u(2),
              "nal_unit_type" : nb.u(5)}
    # nalu = NalUnit(nb, sps = [] if sps == [] else sps[0], pps = pps)
    if params["nal_unit_type"] == 7: # SPS
        sps = SPS(nb, params = params)
    elif params["nal_unit_type"] == 8: # PPS
        pps.append(PPS(nb, sps = sps, params = params))
    elif params["nal_unit_type"] in [1, 5]: # Slice
        slices.append(Slice(nb, sps = sps, pps = pps, params = params))
        pass

# nalus = [NalUnit(nalu_bit) for nalu_bit in nalus_bit]
input_file.close()
