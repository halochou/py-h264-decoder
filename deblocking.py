from utilities import *

def deblock_mb(mb):
    (mbAddrA, blkIdxA) = mb.luma_blocks[0].luma_neighbor("A")
    (mbAddrB, blkIdxB) = mb.luma_blocks[0].luma_neighbor("B")
    mb.fieldMbInFrameFlag = 1 if mb.slice.MbaffFrameFlag == 1 and mb.mb_field_decoding_flag == 1 else 0
    mb.filterInternalEdgesFlag = 0 if mb.slice.disable_deblocking_filter_idc == 1 else 0
    if (mb.slice.MbaffFrameFlag == 0 and mb.idx % mb.slice.PicWidthInMbs == 0) or \
       (mb.slice.MbaffFrameFlag == 1 and (mb.idx >> 1) % mb.slice.PicWidthInMbs == 0) or \
       (mb.slice.disable_deblocking_filter_idc == 1) or \
       (mb.slice.disable_deblocking_filter_idc ==2 and mbAddrA == None):
        mb.filterLeftMbEdgeFlag = 0
    else:
        mb.filterLeftMbEdgeFlag = 1
    if any([
        mb.slice.MbaffFrameFlag == 0 and mb.idx < mb.slice.PicWidthInMbs,
        mb.slice.MbaffFrameFlag == 1 and (mb.idx >> 1) < mb.slice.PicWidthInMbs and mb.idx % 2 == 0,
        mb.slice.disable_deblocking_filter_idc == 1,
        mb.slice.disable_deblocking_filter_idc == 2 and mbAddrB == None
       ]):
        mb.filterTopMbEdgeFlag = 0
    else:
        mb.filterTopMbEdgeFlag = 1




def deblock_blk(blk):
