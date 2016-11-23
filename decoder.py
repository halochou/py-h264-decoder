from bitstring import BitArray, BitStream
from h264bits import H264Bits
from nalsps import SPS
from nalpps import PPS
from nalslice import Slice
from pprint import pprint
from copy import copy
import utilities
import json


def dump_params(d, filename):
    tmp = copy(d.__dict__)
    tmp.pop('bits', None)
    tmp.pop('sps', None)
    tmp.pop('pps_list', None)
    tmp.pop('pps', None)
    tmp.pop('mbs', None)
    with open(filename, 'w') as outfile:
        json.dump(tmp, outfile)

def dump_mbs(slice, filename):
    mbs_coeffs = []
    for mb in slice.mbs:
        blk_coeffs = []
        for blk in mb.luma_blocks:
            blk_coeffs.append(blk.coeffLevel)
        mbs_coeffs.append(blk_coeffs)
    with open(filename, 'w') as outfile:
        json.dump(mbs_coeffs, outfile)

def decode_slice(slice):
    for mb in slice.mbs:
        import intra_pred
        intra_pred.luma_pred(mb)
        intra_pred.chroma_pred(mb)
    utilities.pic_paint(slice.S_prime_L, "Luma")
    utilities.pic_paint(slice.S_prime_Cb, "Cb")
    utilities.pic_paint(slice.S_prime_Cr, "Cr")


input_file = open("baseline.264", "rb")
nalus_ba = list(BitArray(input_file).split('0x000001', bytealigned=True))[1:]
sps = None
ppss = []
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
        dump_params(sps, "sps.json")
    elif params["nal_unit_type"] == 8: # PPS
        pps = PPS(nb, sps = sps, params = params)
        ppss.append(pps)
        fname = "pps_" + str(len(ppss)) + ".json"
        dump_params(pps, fname)
    elif params["nal_unit_type"] in [1, 5]: # Slice
        slice = Slice(nb, sps = sps, ppss = ppss, params = params)
        decode_slice(slice)
        slices.append(slice)
        dump_mbs(slice, "slice_" + str(len(slices)) + "_mb.json")
        fname = "slice_" + str(len(slices)) + ".json"
        dump_params(slice, fname)
    else:
        print("Unknown Slice type, ignore...")

# nalus = [NalUnit(nalu_bit) for nalu_bit in nalus_bit]
input_file.close()


