ref_pic_list_modification( ) {
    if (self.params["slice_type"] % 5 != 2) and (self.params["slice_type"] % 5 != 4) :
        self.params["ref_pic_list_modification_flag_l0"] = self.u(1)
        if self.params["ref_pic_list_modification_flag_l0"] :
            while True :
                self.params["modification_of_pic_nums_idc"] = self.ue()
                if self.params["modification_of_pic_nums_idc"] == 0 or \
                   self.params["modification_of_pic_nums_idc"] == 1 :
                    self.params["abs_diff_pic_num_minus1"] = self.ue()
                elif self.params["modification_of_pic_nums_idc"] == 2 :
                    self.params["long_term_pic_num"] = self.ue()
                if self.params["modification_of_pic_nums_idc"] == 3:
                    break
    if self.params["slice_type"] % 5 == 1 :
        self.params["ref_pic_list_modification_flag_l1"] = self.u(1)
        if self.params["ref_pic_list_modification_flag_l1"]: 
            while True :
                self.params["modification_of_pic_nums_idc"] = self.ue()
                if (self.params["modification_of_pic_nums_idc"] == 0) or \
                   (self.params["modification_of_pic_nums_idc"] == 1) :
                    self.params["abs_diff_pic_num_minus1"] = self.ue()
                elif self.params["modification_of_pic_nums_idc"] == 2 :
                    self.params["long_term_pic_num"] = self.ue()
                if self.params["modification_of_pic_nums_idc"] == 3 :
                    break
