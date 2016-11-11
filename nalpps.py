from nalunit import NalUnit
from pprint import pprint

class PPS(NalUnit):

    def __init__(self, bits, sps, params):
        self.bits = bits
        self.sps = sps
        self.params = params
        self.parse()

    def parse(self):
        self.pic_parameter_set_rbsp()
        self.sps_not_present()
        # print("PPS:")
        # pprint(self.params)

    def pic_parameter_set_rbsp(self):
        self.params["pic_parameter_set_id"] = self.bits.ue()
        self.params["seq_parameter_set_id"] = self.bits.ue()
        self.params["entropy_coding_mode_flag"] = self.bits.u(1)
        self.params["bottom_field_pic_order_in_frame_present_flag"] = self.bits.u(1)
        self.params["num_slice_groups_minus1"] = self.bits.ue()
        if self.params["num_slice_groups_minus1"] > 0 :
            self.params["slice_group_map_type"] = self.bits.ue()
            if self.params["slice_group_map_type"] == 0 :
                self.params["run_length_minus1"] = []
                for i in range(self.params["num_slice_groups_minus1"]+1):
                    self.params["run_length_minus1"].append(self.bits.ue())
            elif self.params["slice_group_map_type"] == 2 :
                self.params["top_left"] = []
                self.params["bottom_right"] = []
                for i in range(self.params["num_slice_groups_minus1"]):
                    self.params["top_left"].append(self.bits.ue())
                    self.params["bottom_right"].append(self.bits.ue())
            elif self.params["slice_group_map_type"] == 3 or \
                 self.params["slice_group_map_type"] == 4 or \
                 self.params["slice_group_map_type"] == 5 :
                self.params["slice_group_change_direction_flag"] = self.bits.u(1)
                self.params["slice_group_change_rate_minus1"] = self.bits.ue()
            elif self.params["slice_group_map_type"] == 6 :
                self.params["pic_size_in_map_units_minus1"] = self.bits.ue()
                self.params["slice_group_id"] = []
                from math import ceil, log2
                for i in range(self.params["pic_size_in_map_units_minus1"]+1):
                    tmp = self.bits.u(ceil(log2(self.params["num_slice_groups_minus1"]+1)))
                    self.params["slice_group_id"].append(tmp)
        self.params["num_ref_idx_l0_default_active_minus1"] = self.bits.ue()
        self.params["num_ref_idx_l1_default_active_minus1"] = self.bits.ue()
        self.params["weighted_pred_flag"] = self.bits.u(1)
        self.params["weighted_bipred_idc"] = self.bits.u(2)
        self.params["pic_init_qp_minus26"] = self.bits.se()
        self.params["pic_init_qs_minus26"] = self.bits.se()
        self.params["chroma_qp_index_offset"] = self.bits.se()
        self.params["deblocking_filter_control_present_flag"] = self.bits.u(1)
        self.params["constrained_intra_pred_flag"] = self.bits.u(1)
        self.params["redundant_pic_cnt_present_flag"] = self.bits.u(1)

        if self.bits.more_rbsp_data() :
            self.params["transform_8x8_mode_flag"] = self.bits.u(1)
            self.params["pic_scaling_matrix_present_flag"] = self.bits.u(1)
            if self.params["pic_scaling_matrix_present_flag"] > 0 :
                upper = (2 if self.params["chroma_format_idc"] != 3 else 6) * self.params["transform_8x8_mode_flag"]
                self.params["pic_scaling_list_present_flag"] = []
                for i in range(upper) :
                    elem = self.bits.u(1)
                    self.params["pic_scaling_list_present_flag"].append(elem)
                    if elem > 0:
                        raise NameError("scaling_list not impl")
                        if i < 6 :
                            pass
                            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
                        else:
                            pass
                            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
            self.params["second_chroma_qp_index_offset"] = self.bits.se()
        self.rbsp_trailing_bits()

    def sps_not_present(self):
        keys = self.params.keys()
        if "transform_8x8_mode_flag" not in keys:
            self.params["transform_8x8_mode_flag"] = 0
        if "second_chroma_qp_index_offset" not in keys:
            self.params["second_chroma_qp_index_offset"] = 0
