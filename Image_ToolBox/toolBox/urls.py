from django.urls import path
from .views import *

urlpatterns = [
    path('', toolBox_view, name="toolbox_home"),
    path('projects/create', create_project, name="create_project"),
    path('projects/update/<project_id>', update_project, name="update_project"),
    path('projects/delete/<project_id>', delete_project, name="delete_project"),
    path('projects/<project_id>', open_project, name="open_project"),

    # TOOLBOX OPTIONS
    path('projects/<project_id>/add_work_image', add_work_image, name="add_work_image"),

    # TOOLBOX [1] Conversion methods

    # --- [0] IMAGE REQUIRED
    path('image/image_data/', image_data, name="image_data"),

    # --- [1] CONVERT IMAGE TO [ GRAY ]
    path('image/convert2rgb/', convert_image_to_rgb, name="convert_image_to_rgb"),
    path('image/convert2gray/', convert_image_to_gray, name="convert_image_to_gray"),
    path('image/convert2hsv/', convert_image_to_hsv, name="convert_image_to_hsv"),
    path('image/image_compression/', image_compression, name="image_compression"),

    # --- [2] RGB RE-SIGN
    path('image/update_red_value/', update_red_value, name="update_red_value"),
    path('image/update_green_value/', update_green_value, name="update_green_value"),
    path('image/update_blue_value/', update_blue_value, name="update_blue_value"),
    

    # --- [3] GRAY RE-SIGN
    path('image/update_gray_value/', update_gray_value, name="update_gray_value"),
    

    # --- [4] HSV RE-SIGN
    path('image/update_hue_value/', update_hue_value, name="update_hue_value"),
    path('image/update_saturation_value/', update_saturation_value, name="update_saturation_value"),
    path('image/update_value_value/', update_value_value, name="update_value_value"),
    

    # ---- [5] image Histogram
    path('image/image_histogram/', image_histogram, name="image_histogram"),
    path('image/apply_histogram_equalization/', apply_histogram_equalization, name="apply_histogram_equalization"),
    

    # ---- [6] Image Transformation
    path('image/flip_image/', flip_image, name="flip_image"),
    path('image/rotate_image/', rotate_image, name="rotate_image"),
    path('image/skew_image/', skew_image, name="skew_image"),
    path('image/translation_image/', translation_image, name="translation_image"),
    path('image/blending_current_image/', blending_current_image, name="blending_current_image"),

    # ---- [7] Image Brightness
    path('image/negative_brightness/', negative_brightness, name="negative_brightness"),
    path('image/log_brightness/', log_brightness, name="log_brightness"),
    path('image/power_brightness/', power_brightness, name="power_brightness"),
    path('image/threshold_brightness/', threshold_brightness, name="threshold_brightness"),
    path('image/bitplan_brightness/', bitplan_brightness, name="bitplan_brightness"),
    

    # ---- [8] Image selection tools
    path('image/image_crop/', image_crop, name="image_crop"),
    path('image/image_zoom_in/', image_zoom_in, name="image_zoom_in"),
    path('image/image_cut_select/', image_cut_select, name="image_cut_select"),
    path('image/image_cut_select_zoom_rotate/', image_cut_select_zoom_rotate, name="image_cut_select_zoom_rotate"),
    path('image/image_cut_select_zoom_flip/', image_cut_select_zoom_flip, name="image_cut_select_zoom_flip"),
    path('image/cut_image_select_avarage_filter/', cut_image_select_avarage_filter, name="cut_image_select_avarage_filter"),
    path('image/cut_image_select_gaussian_filter/', cut_image_select_gaussian_filter, name="cut_image_select_gaussian_filter"),
    path('image/cut_image_select_circular_filter/', cut_image_select_circular_filter, name="cut_image_select_circular_filter"),
    path('image/cut_image_select_cone_filter/', cut_image_select_cone_filter, name="cut_image_select_cone_filter"),
    path('image/cut_image_select_pyrmadial_filter/', cut_image_select_pyrmadial_filter, name="cut_image_select_pyrmadial_filter"),
    path('image/cut_image_select_median_filter/', cut_image_select_median_filter, name="cut_image_select_median_filter"),



    path('image/apply_cut_selected_image_effects/', apply_cut_selected_image_effects, name="apply_cut_selected_image_effects"),
    
    # ---- [9] LPF: IMAGE FILTERS
    path('image/avarage_filter/', avarage_filter, name="avarage_filter"), 
    path('image/gaussian_filter/', gaussian_filter, name="gaussian_filter"), 
    path('image/circular_filter/', circular_filter, name="circular_filter"), 
    path('image/cone_filter/', cone_filter, name="cone_filter"), 
    path('image/pyrmadial_filter/', pyrmadial_filter, name="pyrmadial_filter"), 
    path('image/median_filter/', median_filter, name="median_filter"), 

    # ---- [10] HPF: EDGE DETECTION
    path('image/v_edge/', v_edge, name="v_edge"), 
    path('image/h_edge/', h_edge, name="h_edge"), 
    path('image/sobel_edge/', sobel_edge, name="sobel_edge"), 
    path('image/laplacian_edge/', laplacian_edge, name="laplacian_edge"), 
    path('image/ocr_text_detection/', ocr_text_detection, name="ocr_text_detection"), 

]