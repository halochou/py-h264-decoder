# if self.params["num_slice_groups_minus1"] == 1 and self.params["slice_group_map_type"] in [3,4,5] :
#     slice group 01 <- self.params["slice_group_change_direction_flag"], self.params["slice_group_map_type"]
#     8.2.2.4 and 8.2.2.6
# if self.params["num_slice_groups_minus1"] == 1 and self.params["slice_group_map_type"] in [4,5] :
#     sizeOfUpperLeftGroup = ( self.params["slice_group_change_direction_flag"] ? 
#         ( self.var["PicSizeInMapUnits"] − MapUnitsInSliceGroup0 ) : MapUnitsInSliceGroup0 )
def mb_to_slice_group_map() :
    mapUnitToSliceGroupMap = []
    if self.params["num_slice_groups_minus1"] == 0:
        for i in range(self.var["PicSizeInMapUnits"]):
            mapUnitToSliceGroupMap[i] = 0
    else:
        if self.params["slice_group_map_type"] == 0:
            # 8.2.2.1
            i=0
            while True 
                iGroup = 0
                while iGroup <= self.params["num_slice_groups_minus1"] and i < self.var["PicSizeInMapUnits"] :
                    j = 0
                    while j <= self.params["run_length_minus1"][iGroup] and i+j < self.var["PicSizeInMapUnits"] :
                        mapUnitToSliceGroupMap[i+j] = iGroup
                        j += 1
                    i += self.params["run_length_minus1"][iGroup] + 1
                    iGroup += 1
                if i < self.var["PicSizeInMapUnits"] :
                    break
        elif self.params["slice_group_map_type"] == 1:
            # 8.2.2.2
            for i in range(self.var["PicSizeInMapUnits"]):
                mapUnitToSliceGroupMap[i] = ( ( i % self.var["PicWidthInMbs"] ) + \
                    ( ( ( i / self.var["PicWidthInMbs"] ) * ( self.params["num_slice_groups_minus1"] + 1 ) ) / 2 ) ) % \
                ( self.params["num_slice_groups_minus1"] + 1 )
        elif self.params["slice_group_map_type"] == 2:
            # 8.2.2.3
            for i in range(self.var["PicSizeInMapUnits"]):
                mapUnitToSliceGroupMap[i] = self.params["num_slice_groups_minus1"]
            iGroup = self.params["num_slice_groups_minus1"] - 1
            while iGroup >= 0:
                yTopLeft = self.params["top_left"][ iGroup ] / self.var["PicWidthInMbs"] 
                xTopLeft = self.params["top_left"][ iGroup ] % self.var["PicWidthInMbs"] 
                yBottomRight = self.params["bottom_right"][ iGroup ] / self.var["PicWidthInMbs"] 
                xBottomRight = self.params["bottom_right"][ iGroup ] % self.var["PicWidthInMbs"]
                for y in range(yTopLeft, yBottomRight+1):
                    for x in range(xTopLeft, xBottomRight+1):
                        mapUnitToSliceGroupMap[y * self.var["PicWidthInMbs"] + x] = iGroup
                iGroup -= 1
        elif self.params["slice_group_map_type"] == 3:
            # 8.2.2.4
            for i in range(self.var["PicSizeInMapUnits"]):
                mapUnitToSliceGroupMap[i] = 1
            x = ( self.var["PicWidthInMbs"] − self.params["slice_group_change_direction_flag"] ) / 2
            y = ( self.var["PicHeightInMapUnits"] − self.params["slice_group_change_direction_flag"] ) / 2
            ( leftBound, topBound ) = ( x, y )
            ( rightBound, bottomBound ) = ( x, y )
            ( xDir, yDir ) = ( self.params["slice_group_change_direction_flag"] − 1, self.params["slice_group_change_direction_flag"] )
            k = 0
            while k < self.var["MapUnitsInSliceGroup0"] :
                mapUnitVacant = ( mapUnitToSliceGroupMap[ y * self.var["PicWidthInMbs"] + x ] == 1 ) 
                if mapUnitVacant :
                    mapUnitToSliceGroupMap[ y * self.var["PicWidthInMbs"] + x ] = 0 
                if xDir == −1 and x == leftBound :
                    leftBound = max( leftBound − 1, 0 ) 
                    x = leftBound 
                    ( xDir, yDir ) = ( 0, 2 * self.params["slice_group_change_direction_flag"] − 1 )
                elif xDir == 1 and x == rightBound :
                    rightBound = min( rightBound + 1, self.var["PicWidthInMbs"] − 1 )
                    x = rightBound
                    ( xDir, yDir ) = ( 0, 1 − 2 * self.params["slice_group_change_direction_flag"] ) 
                elif yDir == −1 and y == topBound :
                    topBound = max( topBound − 1, 0 )
                    y = topBound 
                    ( xDir, yDir ) = ( 1 − 2 * self.params["slice_group_change_direction_flag"], 0 ) 
                elif yDir == 1 and y == bottomBound : 
                    bottomBound = min( bottomBound + 1, self.var["PicHeightInMapUnits"] − 1 ) 
                    y = bottomBound 
                    ( xDir, yDir ) = ( 2 * self.params["slice_group_change_direction_flag"] − 1, 0 ) 
                else :
                    ( x, y ) = ( x + xDir, y + yDir )
        elif self.params["slice_group_map_type"] == 4:
            # 8.2.2.5
            for i in range(self.var["PicSizeInMapUnits"]):
                if i < sizeOfUpperLeftGroup :
                    mapUnitToSliceGroupMap[i] = self.params["slice_group_change_direction_flag"]
                else :
                    mapUnitToSliceGroupMap[i] = 1 - self.params["slice_group_change_direction_flag"]
        elif self.params["slice_group_map_type"] == 5:
            # 8.2.2.6
            k = 0
            for j in range(self.var["PicWidthInMbs"]) :
                for i in range(self.var["PicHeightInMapUnits"]) :
                    if k < sizeOfUpperLeftGroup :
                        mapUnitToSliceGroupMap[i * self.var["PicWidthInMbs"] + j] = self.params["slice_group_change_direction_flag"]
                    else :
                        mapUnitToSliceGroupMap[i * self.var["PicWidthInMbs"] + j] = 1 - self.params["slice_group_change_direction_flag"]
                    k += 1
        elif self.params["slice_group_map_type"] == 6:
            # 8.2.2.7
            mapUnitToSliceGroupMap[i] = self.params["slice_group_id"][i]
    # 8.2.2.8 mapUnitToSliceGroupMap -> self.var["MbToSliceGroupMap"]
    for i in range(self.var["PicSizeInMbs"]) :
        if self.params["frame_mbs_only_flag"] == 1 or self.params["field_pic_flag"] == 1 :
            self.var["MbToSliceGroupMap"][ i ] = mapUnitToSliceGroupMap[ i ]
        elif self.var["MbaffFrameFlag"] == 1 :
            self.var["MbToSliceGroupMap"][ i ] = mapUnitToSliceGroupMap[ i / 2 ]
        elif self.params["frame_mbs_only_flag"] == 0 and mb_adaptive_frame_field_flag == 0 and self.params["field_pic_flag"] == 0:
            self.var["MbToSliceGroupMap"][ i ] = mapUnitToSliceGroupMap[ ( i / ( 2 * self.var["PicWidthInMbs"] ) ) * self.var["PicWidthInMbs"] + ( i % self.var["PicWidthInMbs"] ) ]
