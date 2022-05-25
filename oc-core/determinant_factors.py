determinant_factors = ['duration',
                      'waiting_time',
                      'time_to_departure',
                     'total_stops_norm',
                     'road_dist_norm',
                     'traffic_ratio',
                     'likelihood_of_delays',      
                     'last_minute_changes',
                     'rush_overlap',
                     'frequency_of_service',
                     'weather',
                     'total_price', 
                     'can_share_cost',
                     'ticket_coverage',
                     'user_feedback',
                     'cleanliness',
                     'seating_quality',
                     'space_available',
                     'silence_area_presence',
                     'privacy_level',
                     'ride_smoothness',
                     'total_walk_distance',
                     'total_co2_offer',
                     'co2_per_km_offer',
                     'bike_on_board',
                     'total_distance',
                     'business_area_presence', 
                     'internet_availability',
                     'plugs_or_charging_points',
                     'total_legs_norm',
                     'ratio_dist_norm',
                     'leg_fraction',
                     'bike_walk_distance',
                     'bike_walk_legs',
                     'panoramic']

# PLEASE NOTE:
# the order of the determinant factors within each category determines their ROD weights
categories = {'quick' : ['duration',
                         'waiting_time',
                         'total_stops_norm',
                         'traffic_ratio'],
              'reliable' : ['likelihood_of_delays',
                            'traffic_ratio',
                            'last_minute_changes',
                            'rush_overlap',
                            'frequency_of_service',
                            'weather'],
              'cheap' : ['total_price',
                         'can_share_cost',
                         'ticket_coverage'],
              'comfortable' : ['user_feedback',
                               'cleanliness',
                               'seating_quality',
                               'total_legs_norm'],
              # missing starting point and end point
              'door-to-door' : ['total_walk_distance'],
              'environmentally_friendly' : ['total_co2_offer',
                                            'co2_per_km_offer'],
              'short' : ['total_distance',
                         'road_dist_norm',
                         'total_stops_norm'],
              'multitasking' : ['space_available',
                                'silence_area_presence',
                                'business_area_presence',
                                'internet_availability',
                                'plugs_or_charging_points',
                                'privacy_level'],
              #'social' : [],
              'panoramic' : ['panoramic'],
              'healthy' : ['leg_fraction',
                           'total_walk_distance',
                           'bike_walk_distance',
                           'bike_walk_legs']
}

rod_weights = {1: [1.0],
               2: [0.6932, 0.3068],
               3: [0.5232, 0.3240, 0.1528],
               4: [0.4180, 0.2986, 0.1912, 0.0922],
               5: [0.3471, 0.2686, 0.1955, 0.1269, 0.0619],
               6: [0.2966, 0.2410, 0.1884, 0.1387, 0.0908, 0.0445],
               7: [0.2590, 0.2174, 0.1781, 0.1406, 0.1038, 0.0679, 0.0334],
               8: [0.2292, 0.1977, 0.1672, 0.1375, 0.1084, 0.0805, 0.0531, 0.0263],
               9: [0.2058, 0.1808, 0.1565, 0.1332, 0.1095, 0.0867, 0.0644, 0.0425, 0.0211],
               10: [0.1867, 0.1667, 0.1466, 0.1271, 0.1081, 0.0893, 0.0709, 0.0527, 0.0349, 0.0173]}