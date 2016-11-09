class Macroblock:
    def __init__(self, bits, sps, pps, sh, shvar):
        self.bits = bits
        self.sps = sps
        self.pps = pps
        self.sh = sh
        self.shvar = shvar
        self.params = {}
        self.parse()

    def parse(self) :
        self.params["mb_type"] = self.ue()
        if self.mb[-1]["mb_type"] == "I_PCM" :
            while self.bits.pos % 8 != 0 :
                self.mb[-1]["pcm_alignment_zero_bit"] = self.f(1)
            for i in range(256) :
                self.mb[-1]["pcm_sample_luma"][i] = self.u(v)
            for i in (2 * MbWidthC * MbHeightC) :
                self.mb[-1]["pcm_sample_chroma"][i] = self.u(v)
        else :
            noSubMbPartSizeLessThan8x8Flag = 1
            if self.mb[-1]["mb_type"] != "I_NxN" and \
               MbPartPredMode(self.mb[-1]["mb_type"], 0) != "Intra_16x16" and \
               NumMbPart(self.mb[-1]["mb_type"]) == 4 :
                sub_mb_pred(self.mb[-1]["mb_type"])
                for mbPartIdx in range(4) :
                    if sub_self.mb[-1]["mb_type"][mbPartIdx] != "B_Direct_8x8" :
                        if NumSubMbPart(sub_self.mb[-1]["mb_type"][mbPartIdx] > 1 :
                            noSubMbPartSizeLessThan8x8Flag = 0
                    elif not direct_8x8_inference_flag :
                        noSubMbPartSizeLessThan8x8Flag = 0
            else :
                if transform_8x8_mode_flag and self.mb[-1]["mb_type"] == "I_NxN" :
                    transform_size_8x8_flag = self.u(1)
                mb_pred( self.mb[-1]["mb_type"] )
            if MbPartPredMode(self.mb[-1]["mb_type"], 0) != "Intra_16x16" :
                coded_block_pattern = self.me()
                if CodedBlockPatternLuma > 0 and \
                   transform_8x8_mode_flag and \
                   self.mb[-1]["mb_type"] != "I_NxN" and \
                   noSubMbPartSizeLessThan8x8Flag and \
                   (self.mb[-1]["mb_type"] != "B_Direct_16x16" or direct_8x8_inference_flag) :
                    transform_size_8x8_flag = self.u(1)
            if CodedBlockPatternLuma > 0 or CodedBlockPatternChroma > 0 or \
               MbPartPredMode(self.mb[-1]["mb_type"], 0) == "Intra_16x16" :
                mb_qp_delta = self.se()
                residual( 0, 15 )

