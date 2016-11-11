class NalUnit:

    slice_types = {0:"P",1:"B",2:"I",3:"SP",4:"SI",5:"P",6:"B",7:"I",8:"SP",9:"SI"}

    # def __init__(self, bits, sps = {}, pps = []):
    #     self.bits = bits
    #     self.params = {}
    #     self.var = {}
    #     self.sps = sps
    #     self.pps = pps
    #     self.parse()

    def rbsp_trailing_bits(self):
        # if self.bits.more_data():
        self.params["rbsp_stop_one_bit"] = self.bits.f(1)
        assert self.params["rbsp_stop_one_bit"] == 1
        # self.params["rbsp_alignment_zero_bit"] = self.bits[self.bits.pos:].int
        while not self.bits.byte_aligned():
            assert self.bits.f(1) == 0  

    # def parse(self):
    #     # if nal_unit_type == 14 or nal_unit_type == 20 or nal_unit_type == 21 :
    #     #     if nal_unit_type != 21 :
    #     #         self.params["svc_extension_flag"] = u(1)
    #     #     else:
    #     #         self.params["avc_3d_extension_flag"] = u(1)
    #     #     if self.params["svc_extension_flag"] :
    #     #         pass
    #     if self.params["nal_unit_type"] == 1:
    #         self.slice_layer_without_partitioning_rbsp()
    #     elif self.params["nal_unit_type"] == 5:
    #         self.slice_layer_without_partitioning_rbsp()
    #     elif self.params["nal_unit_type"] == 7:
    #         self.seq_parameter_set_rbsp()
    #     elif self.params["nal_unit_type"] == 8:
    #         self.pic_parameter_set_rbsp()
    #     else:
    #         print("NO MATCH")
