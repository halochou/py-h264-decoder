class Macroblock:
    mb_type = {
        0: "I_NxN"
    }

    def __init__(self, parent_slice):
        self.slice = parent_slice
        self.params = {}
        self.var = {}
        self.parse()

    def parse(self):
        print("MacroBlock:")
        self.macroblock_layer()

    def macroblock_layer(self) :
        self.params["mb_type_int"] = self.slice.bits.ue()
        self.params["mb_type"] = Macroblock.mb_type[self.params["mb_type_int"]]
        if self.params["mb_type"] == "I_PCM" :
            print("Not Impl")
            # while not self.slice.bits.byte_aligned() :
            #     self.params["pcm_alignment_zero_bit"] = self.slice.bits.f(1)
            # for i in range(256) :
            #     self.params["pcm_sample_luma"][i] = self.slice.bits.u(v)
            # for i in (2 * MbWidthC * MbHeightC) :
            #     self.params["pcm_sample_chroma"][i] = self.slice.bits.u(v)
        else :
            noSubMbPartSizeLessThan8x8Flag = 1
            if self.params["mb_type"] != "I_NxN" and \
               MbPartPredMode(self.params["mb_type"], 0) != "Intra_16x16" and \
               NumMbPart(self.params["mb_type"]) == 4 :
                pass
                # sub_mb_pred(self.params["mb_type"])
                # for mbPartIdx in range(4) :
                #     if sub_self.params["mb_type"][mbPartIdx] != "B_Direct_8x8" :
                #         if NumSubMbPart(sub_self.params["mb_type"][mbPartIdx] > 1 :
                #             noSubMbPartSizeLessThan8x8Flag = 0
                #     elif not direct_8x8_inference_flag :
                #         noSubMbPartSizeLessThan8x8Flag = 0
            else :
                if self.slice.pps["transform_8x8_mode_flag"] and self.params["mb_type"] == "I_NxN" :
                    self.params["transform_size_8x8_flag"] = self.slice.bits.u(1)
                self.mb_pred( self.params["mb_type"] )
            if self.MbPartPredMode() != "Intra_16x16" :
                self.params["coded_block_pattern"] = self.slice.bits.me(self.MbPartPredMode())
                if self.params["mb_type"] == "I_NxN":
                    self.var["CodedBlockPatternLuma"] = self.params["coded_block_pattern"] % 16
                    self.var["CodedBlockPatternChroma"] = self.params["coded_block_pattern"] / 16
                else:
                    print("CodedBlockPatternLuma/Chroma not derived!!!!")
                if self.var["CodedBlockPatternLuma"] > 0 and \
                   self.slice.pps["transform_8x8_mode_flag"] and \
                   self.params["mb_type"] != "I_NxN" and \
                   noSubMbPartSizeLessThan8x8Flag and \
                   (self.params["mb_type"] != "B_Direct_16x16" or self.params["direct_8x8_inference_flag"]) :
                    self.params["transform_size_8x8_flag"] = self.slice.bits.u(1)
            if self.var["CodedBlockPatternLuma"] > 0 or self.var["CodedBlockPatternChroma"] > 0 or \
               self.MbPartPredMode() == "Intra_16x16" :
                self.params["mb_qp_delta"] = self.slice.bits.se()
                self.residual(0, 15)

    def MbPartPredMode(self):
        if self.params["mb_type_int"] == 0 and self.slice.pps["transform_8x8_mode_flag"] == 0:
            return "Intra_4x4"
        elif self.params["mb_type_int"] == 0 and self.slice.pps["transform_8x8_mode_flag"] == 1:
            return "Intra_8x8"
        else:
            print("MbPartPredMode Not Impl")

    def mb_pred(self, mb_type):
        print("mb_pred not impl")

    def residual(self, a, b):
        print("residual not impl")

