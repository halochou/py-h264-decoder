from nalunit import NalUnit
from pprint import pprint

class PPS:

    def __init__(self, bits, sps, params):
        self.bits = bits
        self.sps = sps
        for k in params:
            self.__dict__[k] = params[k]
        self.parse()

    def rbsp_trailing_bits(self):
        # if self.bits.more_data():
        self.rbsp_stop_one_bit = self.bits.f(1)
        assert self.rbsp_stop_one_bit == 1
        # self.params["rbsp_alignment_zero_bit"] = self.bits[self.bits.pos:].int
        while not self.bits.byte_aligned():
            assert self.bits.f(1) == 0  

    def parse(self):
        self.pic_parameter_set_rbsp()
        self.sps_not_present()
        self.ScalingList4x4 = [
                [6, 13, 13, 20, 20, 20, 28, 28, 28, 28, 32, 32, 32, 37, 37, 42],
                [6, 13, 13, 20, 20, 20, 28, 28, 28, 28, 32, 32, 32, 37, 37, 42],
                [6, 13, 13, 20, 20, 20, 28, 28, 28, 28, 32, 32, 32, 37, 37, 42],
                [10, 14, 14, 20, 20, 20, 24, 24, 24, 24, 27, 27, 27, 30, 30, 34],
                [10, 14, 14, 20, 20, 20, 24, 24, 24, 24, 27, 27, 27, 30, 30, 34],
                [10, 14, 14, 20, 20, 20, 24, 24, 24, 24, 27, 27, 27, 30, 30, 34]]
        # print("PPS:")
        # pprint(self.params)

    def pic_parameter_set_rbsp(self):
        self.pic_parameter_set_id = self.bits.ue()
        self.seq_parameter_set_id = self.bits.ue()
        self.entropy_coding_mode_flag = self.bits.u(1)
        self.bottom_field_pic_order_in_frame_present_flag = self.bits.u(1)
        self.num_slice_groups_minus1 = self.bits.ue()
        if self.num_slice_groups_minus1 > 0 :
            self.slice_group_map_type = self.bits.ue()
            if self.slice_group_map_type == 0 :
                self.run_length_minus1 = []
                for i in range(self.num_slice_groups_minus1+1):
                    self.run_length_minus1.append(self.bits.ue())
            elif self.slice_group_map_type == 2 :
                self.top_left = []
                self.bottom_right = []
                for i in range(self.num_slice_groups_minus1):
                    self.top_left.append(self.bits.ue())
                    self.bottom_right.append(self.bits.ue())
            elif self.slice_group_map_type == 3 or \
                 self.slice_group_map_type == 4 or \
                 self.slice_group_map_type == 5 :
                self.slice_group_change_direction_flag = self.bits.u(1)
                self.slice_group_change_rate_minus1 = self.bits.ue()
            elif self.slice_group_map_type == 6 :
                self.pic_size_in_map_units_minus1 = self.bits.ue()
                self.slice_group_id = []
                from math import ceil, log2
                for i in range(self.pic_size_in_map_units_minus1+1):
                    tmp = self.bits.u(ceil(log2(self.num_slice_groups_minus1+1)))
                    self.slice_group_id.append(tmp)
        self.num_ref_idx_l0_default_active_minus1 = self.bits.ue()
        self.num_ref_idx_l1_default_active_minus1 = self.bits.ue()
        self.weighted_pred_flag = self.bits.u(1)
        self.weighted_bipred_idc = self.bits.u(2)
        self.pic_init_qp_minus26 = self.bits.se()
        self.pic_init_qs_minus26 = self.bits.se()
        self.chroma_qp_index_offset = self.bits.se()
        self.deblocking_filter_control_present_flag = self.bits.u(1)
        self.constrained_intra_pred_flag = self.bits.u(1)
        self.redundant_pic_cnt_present_flag = self.bits.u(1)

        if self.bits.more_rbsp_data() :
            self.transform_8x8_mode_flag = self.bits.u(1)
            self.pic_scaling_matrix_present_flag = self.bits.u(1)
            if self.pic_scaling_matrix_present_flag > 0 :
                upper = (2 if self.chroma_format_idc != 3 else 6) * self.transform_8x8_mode_flag
                self.pic_scaling_list_present_flag = []
                for i in range(upper) :
                    elem = self.bits.u(1)
                    self.pic_scaling_list_present_flag.append(elem)
                    if elem > 0:
                        raise NameError("scaling_list not impl")
                        if i < 6 :
                            pass
                            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
                        else:
                            pass
                            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
            self.second_chroma_qp_index_offset = self.bits.se()
        self.rbsp_trailing_bits()

    def sps_not_present(self):
        keys = self.__dict__.keys()
        if "transform_8x8_mode_flag" not in keys:
            self.transform_8x8_mode_flag = 0
        if "second_chroma_qp_index_offset" not in keys:
            self.second_chroma_qp_index_offset = 0
