from nalunit import NalUnit
from pprint import pprint

class SPS(NalUnit):

    def __init__(self, bits, params):
        self.bits = bits
        self.params = params
        self.parse()

    def parse(self):
        self.seq_parameter_set_rbsp()

    def seq_parameter_set_rbsp(self):
        self.params["profile_idc"] = self.bits.u(8)
        self.params["constraint_set0_flag"] = self.bits.u(1)
        self.params["constraint_set1_flag"] = self.bits.u(1)
        self.params["constraint_set2_flag"] = self.bits.u(1)
        self.params["constraint_set3_flag"] = self.bits.u(1)
        self.params["constraint_set4_flag"] = self.bits.u(1)
        self.params["constraint_set5_flag"] = self.bits.u(1)
        self.params["reserved_zero_2bits"]  = self.bits.u(2)
        self.params["level_idc"] = self.bits.u(8)
        self.params["seq_parameter_set_id"] =  self.bits.ue()
        if self.params["profile_idc"] == 100 or self.params["profile_idc"] == 110 or self.params["profile_idc"] == 122 or self.params["profile_idc"] == 244 or self.params["profile_idc"] == 44 or self.params["profile_idc"] == 83 or self.params["profile_idc"] == 86 or self.params["profile_idc"] == 118 or self.params["profile_idc"] == 128 or self.params["profile_idc"] == 138 or self.params["profile_idc"] == 139 or self.params["profile_idc"] == 134 or self.params["profile_idc"] == 135 :
            self.params["chroma_format_idc"] = self.bits.ue()
            if self.params["chroma_format_idc"] == 3 :
                self.params["separate_colour_plane_flag"] = self.bits.u(1)
            else :
                self.params["separate_colour_plane_flag"] = 0
            self.params["bit_depth_luma_minus8"] = self.bits.ue()
            self.params["bit_depth_chroma_minus8"] = self.bits.ue()
            self.params["qpprime_y_zero_transform_bypass_flag"] = self.bits.u(1)
            self.params["seq_scaling_matrix_present_flag"] = self.bits.u(1)
            #if( seq_scaling_matrix_present_flag )    self.bits.u(1)
            #for( i = 0; i < ( ( chroma_format_idc != 3 ) ? 8 : 12 ); i++ ) {
            #seq_scaling_list_present_flag[ i ]    self.bits.u(1)
            #if( seq_scaling_list_present_flag[ i ] )
            #if( i < 6 )
            #scaling_list( ScalingList4x4[ i ], 16, UseDefaultScalingMatrix4x4Flag[ i ] )
            #else
            #scaling_list( ScalingList8x8[ i − 6 ], 64, UseDefaultScalingMatrix8x8Flag[ i − 6 ] )
        self.params["log2_max_frame_num_minus4"] = self.bits.ue()
        self.params["pic_order_cnt_type"] = self.bits.ue()
        if self.params["pic_order_cnt_type"] == 0 :
            self.params["log2_max_pic_order_cnt_lsb_minus4"] = self.bits.ue()
        # elif self.params["pic_order_cnt_type == 1"] :
        #     self.params["delta_pic_order_always_zero_flag"] = self.bits.u(1)
        #     self.params["offset_for_non_ref_pic"] = self.se()
        #     self.params["offset_for_top_to_bottom_field"] = self.se()
        #     self.params["num_ref_frames_in_pic_order_cnt_cycle"] = self.bits.ue()
        #     for( i = 0; i < num_ref_frames_in_pic_order_cnt_cycle; i++ )
        #         offset_for_ref_frame[ i ] = self.se()
        self.params["max_num_ref_frames"] = self.bits.ue()
        self.params["gaps_in_frame_num_value_allowed_flag"] = self.bits.u(1)
        self.params["pic_width_in_mbs_minus1"] = self.bits.ue()
        self.params["pic_height_in_map_units_minus1"] = self.bits.ue()
        self.params["frame_mbs_only_flag"] = self.bits.u(1)
        if self.params["frame_mbs_only_flag"] == 0 :
            self.params["mb_adaptive_frame_field_flag"] = self.bits.u(1)
        else:
            self.params["mb_adaptive_frame_field_flag"] = 0
        self.params["direct_8x8_inference_flag"] = self.bits.u(1)
        self.params["frame_cropping_flag"] = self.bits.u(1)
        if self.params["frame_cropping_flag"] != 0 :
            self.params["frame_crop_left_offset"] = self.bits.ue()
            self.params["frame_crop_right_offset"] = self.bits.ue()
            self.params["frame_crop_top_offset"] = self.bits.ue()
            self.params["frame_crop_bottom_offset"] = self.bits.ue()
        self.params["vui_parameters_present_flag"] = self.bits.u(1)
        # if self.params["vui_parameters_present_flag"] :
        #     vui_parameters()
        self.rbsp_trailing_bits()
        print("SPS:")
        pprint(self.params)
