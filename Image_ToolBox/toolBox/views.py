import pathlib
from pytesseract import pytesseract
pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Rendering Libs
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse


# Login Docirators
from django.contrib.auth.decorators import login_required


# User Model
from django.contrib.auth.models import User
from numpy.core.fromnumeric import shape
from numpy.lib.type_check import imag


# Current app files
from .models import *
from .forms import *

# OpenCV
import cv2
import numpy as np
from django.core.files.base import ContentFile

# ---------- [1] Project Main Actions

@login_required
def toolBox_view(request):
    """
        [+] Function name: ToolBox View
        [+] Function parameters: [request]
        [+] Function description:
                    This function load the all projects data and
                    render the all projects pages
    """

    # Get all Projects Data
    projects = Projects.objects.filter(User = request.user).order_by('-id')

    # Returned Data
    context = {
        'Projects': projects,
        'Projects_Form':ProjectForm,
    }

    # Returned Page and Data
    return render(request, 'pages/home/home.html', context)

@login_required
def open_project(request, project_id):
    """
        [+] Function name: Open Project
        [+] Function parameters: [request, project_id]
        [+] Function description:
                This function open the project and display the last updates
    """

    # Check if the project exist or not
    project = get_object_or_404(Projects, id = project_id)

    # Check the request method
    if request.method == 'GET':

        # Get project data
        project = Projects.objects.get(id = project_id)

        # Get project images
        images = ProjectsImages.objects.filter( Project = project)

        
        # Set the initial value of the current image
        current_image = None

        # Get the current image
        if images:

            # Inverse the array 
            image_invers = images.order_by('-id')

            # catch the current image
            current_image = image_invers[0]

        RED_VALUE, GREEN_VALUE, BLUE_VALUE = None, None, None
        HUE_VALUE, SATURATION_VALUE, VALUE_VALUE = None, None, None
        GRAY_VALUE = None
        
        # Get the current image
        if current_image:

            # Current work directory
            base = pathlib.Path().resolve()

            if current_image.current_image_format == 1:
                # Load the image [GRAY]
                image = cv2.imread(f'{base}/{current_image.Image.url}', 0)

                # Get the avarage value
                GRAY_VALUE = int(image.mean())


            elif current_image.current_image_format == 2:
                # Load the image [HSV]
                image = cv2.imread(f'{base}/{current_image.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (current_image.current_image_width, current_image.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to H, S, V
                hue, saturation, value = cv2.split(image)

                # Get the avarage value
                HUE_VALUE = int(hue.mean())
                SATURATION_VALUE = int(saturation.mean())
                VALUE_VALUE = int(value.mean())

            else:
                
                # Load the image [RGB]
                image = cv2.imread(f'{base}/{current_image.Image.url}')

                # Split channals to R, G, B
                blue, green, red = cv2.split(image)

                # Get the avarage value
                RED_VALUE = int(red.mean())
                GREEN_VALUE = int(green.mean())
                BLUE_VALUE = int(blue.mean())




        # Check the if the current project belong to the 
        if project.User == request.user:

            # Returned Data
            context = {
                'Project':project,
                'Images': images.order_by('-id'),
                'current_image':current_image,
                'RED_VALUE':RED_VALUE,
                'GREEN_VALUE':GREEN_VALUE,
                'BLUE_VALUE':BLUE_VALUE,
                'HUE_VALUE':HUE_VALUE,
                'SATURATION_VALUE':SATURATION_VALUE,
                'VALUE_VALUE':VALUE_VALUE,
                'GRAY_VALUE':GRAY_VALUE,
            }

            return render(request, 'pages/toolbox/toolbox.html', context)
            


    return redirect('toolbox_home')

@login_required
def create_project(request):
    """
        [+] Function name: Create Project
        [+] Function parameters: [request]
        [+] Function description:
                    This function create a new project
    """

    # Check the request method
    if request.method == 'POST':

        project = ProjectForm(request.POST)

        if project.is_valid():
            project = project.save(commit=False)
            project.User = request.user
            project.status = '1'
            project.save()


    return redirect('toolbox_home')


@login_required
def update_project(request, project_id):
    # Check if the project exist or not
    project = get_object_or_404(Projects, id = project_id)

    # Get the project Effects
    effects = ProjectsImages.objects.filter(Project = project)

    # Check user relation
    if request.user == project.User:
        
        # Check the request method
        if request.method == "POST":
            
            # Catche the returned form 
            form = UpdateProjectForm(request.POST)

            # Check the form validiation
            if form.is_valid():
                form = form.save(commit=False)
                project.Project_Name =form.Project_Name
                project.Progress =form.Progress
                project.status = form.status
                project.Total_effects = len(effects)
                project.save()
        
    return redirect('toolbox_home')

@login_required
def delete_project(request, project_id):
    """
        [+] Function name: Delete Project
        [+] Function parameters: [request, project_id]
        [+] Function description:
                    This function delete a selected project depend on the projec id
                    and user that request the delete option
    """

    # Check if the project exist or not
    project = get_object_or_404(Projects, id = project_id)

    # Check the request method
    if request.method == 'POST':

        project = Projects.objects.get(id = project_id)

        if project.User == request.user:
            project.delete()


    return redirect('toolbox_home')



# ------------ [2] Project Functions
@login_required
def add_work_image(request, project_id):
    
    # Check the request method
    if request.method == 'POST':

        form = ProjectImageForm(request.POST, request.FILES)
        project = Projects.objects.get(id = int(project_id))

        if form.is_valid():
            form = form.save(commit=False)
            form.Project = project
            form.save()

            # Get the image
            image = ProjectsImages.objects.get(id = form.id)

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            cv_image = cv2.imread(f'{base}/{image.Image.url}')

            # Reset the image values
            image.current_image_width = cv_image.shape[1]
            image.current_image_height = cv_image.shape[0]
            image.current_image_format = 0
            image.current_image_Min_intensity = cv_image.min()
            image.current_image_Max_intensity = cv_image.max()

            # Update the image values
            image.save()


    # Return to the project page
    return redirect('open_project', project_id)

# Save the converted image
def save_converted_image(image_src, image, extiention, format):
    # Convert from cv2 image to normal image
    ret, buf = cv2.imencode(str(f'.{extiention}'), image)
    content = ContentFile(buf.tobytes())

    # Save image
    image_model = ProjectsImages()
    image_model.Project = image_src.Project

    image_model.current_image_width = image.shape[1]
    image_model.current_image_height = image.shape[0]
    image_model.current_image_format = format
    image_model.current_image_Min_intensity = image.min()
    image_model.current_image_Max_intensity = image.max()

    image_model.Image.save(f'{image_src.Project}_output.{extiention}', content)
    image_model.save()

    # Return the image path
    image_id = str(image_model.id)
    image_path = str(image_model.Image.url)
    current_image_width = str(image_model.current_image_width)
    current_image_height = str(image_model.current_image_height)
    current_image_format = str(image_model.current_image_format)
    current_image_Min_intensity = str(image_model.current_image_Min_intensity)
    current_image_Max_intensity = str(image_model.current_image_Max_intensity)

    # List of color Data
    color_data = list()

    if format == 1:

        # Get the avarage value
        GRAY_VALUE = int(image.mean())

        # Add Gray Mean
        color_data.append(GRAY_VALUE)


    elif format == 2:

        # Split channals to H, S, V
        hue, saturation, value = cv2.split(image)

        # Get the avarage value
        HUE_VALUE = int(hue.mean())
        SATURATION_VALUE = int(saturation.mean())
        VALUE_VALUE = int(value.mean())

        # Add HSV Mean
        color_data.append(HUE_VALUE)
        color_data.append(SATURATION_VALUE)
        color_data.append(VALUE_VALUE)

    else:
        

        # Split channals to R, G, B
        blue, green, red = cv2.split(image)

        # Get the avarage value
        RED_VALUE = int(red.mean())
        GREEN_VALUE = int(green.mean())
        BLUE_VALUE = int(blue.mean())

        # Add RGB Mean
        color_data.append(RED_VALUE)
        color_data.append(GREEN_VALUE)
        color_data.append(BLUE_VALUE)


    data = {"image_id": image_id,
            "image_path": image_path,
            "current_image_width": current_image_width,
            "current_image_height": current_image_height,
            "current_image_format": current_image_format,
            "current_image_Min_intensity": current_image_Min_intensity,
            "current_image_Max_intensity": current_image_Max_intensity,
            "Color_data":color_data,
            }

    return data


# Save the converted image
def save_selected_image(image_src, image, extiention, format, left_position, top_position):
    # Convert from cv2 image to normal image
    ret, buf = cv2.imencode(str(f'.{extiention}'), image)
    content = ContentFile(buf.tobytes())

    # Save image
    image_model = ZoomedImages()
    image_model.target_image = image_src

    image_model.width = image.shape[1]
    image_model.height = image.shape[0]
    image_model.x_position = left_position
    image_model.y_position = top_position
    image_model.image_format = format


    image_model.zoomed_image.save(f'{image_src.Project}_output.{extiention}', content)
    image_model.save()

    # Return the image path
    image_id = str(image_model.id)
    image_path = str(image_model.zoomed_image.url)
    current_image_width = str(image_model.width)
    current_image_height = str(image_model.height)
    current_image_format = str(image_model.image_format)


    # Returned Data
    data = {"image_id": image_id,
            "image_path": image_path,
            "current_image_width": current_image_width,
            "current_image_height": current_image_height,
            "current_image_format": current_image_format
            }

    return data

# Save the converted image
def save_selected_image_effect(image_src, image, extiention, format, left_position, top_position):
    # Convert from cv2 image to normal image
    ret, buf = cv2.imencode(str(f'.{extiention}'), image)
    content = ContentFile(buf.tobytes())

    # Save image
    image_model = ZoomedImages()
    image_model.target_image = image_src.target_image

    image_model.width = image.shape[1]
    image_model.height = image.shape[0]
    image_model.x_position = left_position
    image_model.y_position = top_position
    image_model.image_format = format


    image_model.zoomed_image.save(f'{image_src.target_image.Project}_output.{extiention}', content)
    image_model.save()

    # Return the image path
    image_id = str(image_model.id)
    image_path = str(image_model.zoomed_image.url)
    current_image_width = str(image_model.width)
    current_image_height = str(image_model.height)
    current_image_format = str(image_model.image_format)


    # Returned Data
    data = {"image_id": image_id,
            "image_path": image_path,
            "current_image_width": current_image_width,
            "current_image_height": current_image_height,
            "current_image_format": current_image_format
            }

    return data


@login_required
def convert_image_to_rgb(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')   

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}')

            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 0)

            # Return image data
            return JsonResponse(data)


@login_required
def convert_image_to_gray(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 1)

            # Return image data
            return JsonResponse(data)


@login_required
def convert_image_to_hsv(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            elif image_src.current_image_format == 2:
                
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
            else:
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 2)
            
            # Return image data
            return JsonResponse(data)

@login_required
def image_data(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image = ProjectsImages.objects.get(id = int(image_id))

            # Return the image path
            current_image_width = str(image.current_image_width)
            current_image_height = str(image.current_image_height)
            current_image_format = str(image.current_image_format)
            current_image_Min_intensity = str(image.current_image_Min_intensity)
            current_image_Max_intensity = str(image.current_image_Max_intensity)

            # Current work directory
            base = pathlib.Path().resolve()

            # List of color Data
            color_data = list()

            if image.current_image_format == 1:

                # Read the Gray Image
                image = cv2.imread(f'{base}/{image.Image.url}', 0)

                # Get the avarage value
                GRAY_VALUE = int(image.mean())

                # Add Gray Mean
                color_data.append(GRAY_VALUE)


            elif image.current_image_format == 2:

                # Read the HSV IMage
                image = cv2.imread(f'{base}/{image.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (int(current_image_width), int(current_image_height)), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to H, S, V
                hue, saturation, value = cv2.split(image)

                # Get the avarage value
                HUE_VALUE = int(hue.mean())
                SATURATION_VALUE = int(saturation.mean())
                VALUE_VALUE = int(value.mean())

                # Add HSV Mean
                color_data.append(HUE_VALUE)
                color_data.append(SATURATION_VALUE)
                color_data.append(VALUE_VALUE)

            else:
                
                # Read the RGB Image
                image = cv2.imread(f'{base}/{image.Image.url}')

                # Split channals to R, G, B
                blue, green, red = cv2.split(image)

                # Get the avarage value
                RED_VALUE = int(red.mean())
                GREEN_VALUE = int(green.mean())
                BLUE_VALUE = int(blue.mean())

                # Add RGB Mean
                color_data.append(RED_VALUE)
                color_data.append(GREEN_VALUE)
                color_data.append(BLUE_VALUE)


            # Returned data
            data = {"current_image_width": current_image_width,
                    "current_image_height": current_image_height,
                    "current_image_format": current_image_format,
                    "current_image_Min_intensity": current_image_Min_intensity,
                    "current_image_Max_intensity": current_image_Max_intensity,
                    'color_data':color_data,
                    }

            return JsonResponse(data)


@login_required
def update_red_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            red_value = float(request.POST.get('red_value'))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}')
            
            # Split channals to R, G, B
            blue, green, red = cv2.split(image)

            # Increase the value
            for hP in range(red.shape[0]):
                for wP in range(red.shape[1]):
                    red[hP,  wP] = np.clip(red[hP, wP] + int(red_value), 0, 255)

            
            # Merg the red image
            image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 0)

            # Return image data
            return JsonResponse(data)

@login_required
def update_green_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            green_value = request.POST.get('green_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}')
            
            # Split channals to R, G, B
            blue, green, red = cv2.split(image)

            # Increase the value
            for hP in range(green.shape[0]):
                for wP in range(green.shape[1]):
                    green[hP,  wP] = np.clip(green[hP, wP] + int(green_value), 0, 255)


            # Merg the green image
            image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 0)

            # Return image data
            return JsonResponse(data)

@login_required
def update_blue_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            blue_value = request.POST.get('blue_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}')
            
            # Split channals to R, G, B
            blue, green, red = cv2.split(image)

            # Increase the value
            for hP in range(blue.shape[0]):
                for wP in range(blue.shape[1]):
                    blue[hP,  wP] = np.clip(blue[hP, wP] + int(blue_value), 0, 255)


            # Merg the blue image
            image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 0)

            # Return image data
            return JsonResponse(data)


@login_required
def update_gray_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            gray_value = request.POST.get('gray_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}', 0)
            

            # Increase the value
            for hP in range(image.shape[0]):
                for wP in range(image.shape[1]):
                    image[hP,  wP] = np.clip(image[hP, wP] + int(gray_value), 0, 255)


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 1)

            # Return image data
            return JsonResponse(data)

@login_required
def update_hue_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            hue_value = request.POST.get('hue_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
            image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

            # Split channals to R, G, B
            hue, saturation, value = cv2.split(image)

            # Increase the value
            for hP in range(hue.shape[0]):
                for wP in range(hue.shape[1]):
                    hue[hP,  wP] = np.clip(hue[hP, wP] + int(hue_value), 0, 255)

            # Merg the hue image
            image = cv2.merge((hue, saturation, value))

            # Read the hue extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 2)

            # Return image data
            return JsonResponse(data)

@login_required
def update_saturation_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            saturation_value = request.POST.get('saturation_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
            image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
            
            # Split channals to R, G, B
            hue, saturation, value = cv2.split(image)

            # Increase the value
            for hP in range(saturation.shape[0]):
                for wP in range(saturation.shape[1]):
                    saturation[hP,  wP] = np.clip(saturation[hP, wP] + int(saturation_value), 0, 255)

            # Merg the hue image
            image = cv2.merge((hue, saturation, value))

            # Read the hue extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 2)

            # Return image data
            return JsonResponse(data)

@login_required
def update_value_value(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            value_value = request.POST.get('value_value')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
            image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
            
            # Split channals to R, G, B
            hue, saturation, value = cv2.split(image)

            # Increase the value
            for hP in range(value.shape[0]):
                for wP in range(value.shape[1]):
                    value[hP,  wP] = np.clip(value[hP, wP] + int(value_value), 0, 255)

            # Merg the hue image
            image = cv2.merge((hue, saturation, value))

            # Read the hue extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Convert the image
            data = save_converted_image(image_src, image, extiention, 2)

            # Return image data
            return JsonResponse(data)



# =============== [2] Image Histogram ===================

# [1] Display the image histogram
@login_required
def image_histogram(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Histogram List
            histogram_data = dict()

            if image.current_image_format == 1:

                # Read the Gray Image
                image = cv2.imread(f'{base}/{image.Image.url}', 0)

                # Count histogram data
                unique, counts = np.unique(image, return_counts=True)

                # Catch the data
                data_list = list()

                # Loop to get data
                for i in range(256):
                    if i not in unique:
                        data_list.append(0)
                    else:
                        index = np.where(unique == i)
                        data_list.append(int(counts[index]))

                histogram_data['Format'] = 1
                histogram_data['data'] = data_list


            elif image.current_image_format == 2:

                # Read the current image width and height
                current_image_width = image.current_image_width
                current_image_height = image.current_image_height

                # Read the HSV IMage
                image = cv2.imread(f'{base}/{image.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (int(current_image_width), int(current_image_height)), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to H, S, V
                hue, saturation, value = cv2.split(image)

                # Count histogram data
                hue_unique, hue_counts = np.unique(hue, return_counts=True)
                saturation_unique, saturation_counts = np.unique(saturation, return_counts=True)
                value_unique, value_counts = np.unique(value, return_counts=True)

                # Catch the data
                hue_data_list = list()
                saturation_data_list = list()
                value_data_list = list()


                # Loop to get Hue data
                for i in range(256):
                    if i not in hue_unique:
                        hue_data_list.append(0)
                    else:
                        index = np.where(hue_unique == i)
                        hue_data_list.append(int(hue_counts[index]))
                
                # Loop to get Saturation data
                for i in range(256):
                    if i not in saturation_unique:
                        saturation_data_list.append(0)
                    else:
                        index = np.where(saturation_unique == i)
                        saturation_data_list.append(int(saturation_counts[index]))

                # Loop to get Value data
                for i in range(256):
                    if i not in value_unique:
                        value_data_list.append(0)
                    else:
                        index = np.where(value_unique == i)
                        value_data_list.append(int(value_counts[index]))

                # Response Data
                histogram_data['Format'] = 2
                histogram_data['hue_data'] = hue_data_list
                histogram_data['saturation_data'] = saturation_data_list
                histogram_data['value_data'] = value_data_list

            else:
                
                # Read the RGB Image
                image = cv2.imread(f'{base}/{image.Image.url}')

                # Split channals to R, G, B
                blue, green, red = cv2.split(image)

                # Count histogram data
                red_unique, red__counts = np.unique(red, return_counts=True)
                green_unique, green_counts = np.unique(green, return_counts=True)
                blue_unique, blue_counts = np.unique(blue, return_counts=True)

                # Catch the data
                red_data_list = list()
                green_data_list = list()
                blue_data_list = list()

                # Loop to get Red data
                for i in range(256):
                    if i not in red_unique:
                        red_data_list.append(0)
                    else:
                        index = np.where(red_unique == i)
                        red_data_list.append(int(red__counts[index]))

                # Loop to get Green data
                for i in range(256):
                    if i not in green_unique:
                        green_data_list.append(0)
                    else:
                        index = np.where(green_unique == i)
                        green_data_list.append(int(green_counts[index]))

                # Loop to get Blue data
                for i in range(256):
                    if i not in blue_unique:
                        blue_data_list.append(0)
                    else:
                        index = np.where(blue_unique == i)
                        blue_data_list.append(int(blue_counts[index]))

                # Response Data
                histogram_data['Format'] = 0
                histogram_data['red_data'] = red_data_list
                histogram_data['green_data'] = green_data_list
                histogram_data['blue_data'] = blue_data_list


            # Data Range
            data_rang = list()
            for i in range(256):
                data_rang.append(i)

            # Add Data range to response
            histogram_data['range'] = data_rang

            # Return image data
            return JsonResponse(histogram_data)


# [2] Apply the histogram equalization
@login_required
def apply_histogram_equalization(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl histogram
                image = cv2.equalizeHist(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl histogram
                hue = cv2.equalizeHist(hue)
                saturation = cv2.equalizeHist(saturation)
                value = cv2.equalizeHist(value)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl histogram
                blue = cv2.equalizeHist(blue)
                green = cv2.equalizeHist(green)
                red = cv2.equalizeHist(red)

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


# ============= [3] Image Transformations

@login_required
def flip_image(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            flip_direction = request.POST.get('flip_direction')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Flip initial value
            image_flip = 0

            # Get the requested flip
            if flip_direction == 'X':
                image_flip = 0
            elif flip_direction == 'Y':
                image_flip = 1
            elif flip_direction == 'XY':
                image_flip = -1


            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl histogram
                image = cv2.flip(image, image_flip)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl histogram
                hue = cv2.flip(hue, image_flip)
                saturation = cv2.flip(saturation, image_flip)
                value = cv2.flip(value, image_flip)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl histogram
                blue = cv2.flip(blue, image_flip)
                green = cv2.flip(green, image_flip)
                red = cv2.flip(red, image_flip)

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def rotate_image(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            rotation_angle = int(request.POST.get('rotation_angle'))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Rotation Matrix (Center, angle, scale)
            if abs(rotation_angle) not in [90, -90, 180, 270, -270]:
                rotation_matrix = cv2.getRotationMatrix2D((image_src.current_image_width / 2, image_src.current_image_height / 2), rotation_angle, 1)

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl Rotation
                if abs(rotation_angle) not in  [90, -90, 180, 270, -270]:
                    image = cv2.warpAffine(image, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))
                else:
                    if rotation_angle in [90, -270]:
                        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif rotation_angle in [-90, 270]:
                        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    else:
                        image = cv2.rotate(image, cv2.ROTATE_180)
 

            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl Rotation
                if abs(rotation_angle) not in  [90, -90, 180, 270, -270]:
                    hue = cv2.warpAffine(hue, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))
                    saturation = cv2.warpAffine(saturation, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))
                    value = cv2.warpAffine(value, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))

                else:
                    if rotation_angle in [90, -270]:
                        hue = cv2.rotate(hue, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        saturation = cv2.rotate(saturation, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        value = cv2.rotate(value, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif rotation_angle in [-90, 270]:
                        hue = cv2.rotate(hue, cv2.ROTATE_90_CLOCKWISE)
                        saturation = cv2.rotate(saturation, cv2.ROTATE_90_CLOCKWISE)
                        value = cv2.rotate(value, cv2.ROTATE_90_CLOCKWISE)
                    else:
                        hue = cv2.rotate(hue, cv2.ROTATE_180)
                        saturation = cv2.rotate(saturation, cv2.ROTATE_180)
                        value = cv2.rotate(value, cv2.ROTATE_180)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl Rotation
                if abs(rotation_angle) not in  [90, -90, 180, 270, -270]:
                    blue = cv2.warpAffine(blue, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))
                    green = cv2.warpAffine(green, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))
                    red = cv2.warpAffine(red, rotation_matrix, (image_src.current_image_width, image_src.current_image_height))

                else:
                    if rotation_angle in [90, -270]:
                        blue = cv2.rotate(blue, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        green = cv2.rotate(green, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        red = cv2.rotate(red, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif rotation_angle in [-90, 270]:
                        blue = cv2.rotate(blue, cv2.ROTATE_90_CLOCKWISE)
                        green = cv2.rotate(green, cv2.ROTATE_90_CLOCKWISE)
                        red = cv2.rotate(red, cv2.ROTATE_90_CLOCKWISE)
                    else:
                        blue = cv2.rotate(blue, cv2.ROTATE_180)
                        green = cv2.rotate(green, cv2.ROTATE_180)
                        red = cv2.rotate(red, cv2.ROTATE_180)

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def skew_image(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            point_1_x = float(request.POST.get('point_1_x'))
            point_1_y = float(request.POST.get('point_1_y'))
            point_2_x = float(request.POST.get('point_2_x'))
            point_2_y = float(request.POST.get('point_2_y'))
            point_4_x = float(request.POST.get('point_4_x'))
            point_4_y = float(request.POST.get('point_4_y'))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Skewing Source points
            src_points = np.float32([(point_1_x, point_1_y),(point_4_x, point_4_y),(point_2_x, point_2_y)])

            # Skewing Destnation points
            dst_points = np.float32([(0, 0), (image_src.current_image_width - 1, 0), (0, image_src.current_image_height -1)])

            # Skewing matrix
            skewing_matrix = cv2.getAffineTransform(src_points, dst_points)

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl SKEW
                image = cv2.warpAffine(image, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl SKEW
                hue = cv2.warpAffine(hue, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))
                saturation = cv2.warpAffine(saturation, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))
                value = cv2.warpAffine(value, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl SKEW
                blue = cv2.warpAffine(blue, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))
                green = cv2.warpAffine(green, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))
                red = cv2.warpAffine(red, skewing_matrix, (image_src.current_image_width, image_src.current_image_height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def translation_image(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            Tx = int(request.POST.get('Tx'))
            Ty = int(request.POST.get('Ty'))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Rotation Matrix (Center, angle, scale)
            translation_matrix = np.float32([[1, 0, Tx],[0, 1, Ty]])

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply TRANSLATION
                image = cv2.warpAffine(image, translation_matrix, (image_src.current_image_width, image_src.current_image_height))


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply TRANSLATION
                hue = cv2.warpAffine(hue, translation_matrix, (image_src.current_image_width, image_src.current_image_height))
                saturation = cv2.warpAffine(saturation, translation_matrix, (image_src.current_image_width, image_src.current_image_height))
                value = cv2.warpAffine(value, translation_matrix, (image_src.current_image_width, image_src.current_image_height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply TRANSLATION
                blue = cv2.warpAffine(blue, translation_matrix, (image_src.current_image_width, image_src.current_image_height))
                green = cv2.warpAffine(green, translation_matrix, (image_src.current_image_width, image_src.current_image_height))
                red = cv2.warpAffine(red, translation_matrix, (image_src.current_image_width, image_src.current_image_height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def blending_current_image(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            blending_persentage_value = request.POST.get('blending_persentage_value')
            blending_image = request.FILES.get('blending_image')

            
            # Get the current image
            current_image = ProjectsImages.objects.get(id = int(image_id))

            # create new blending image
            blending_image = BlendingWithCurrentImage.objects.create(
                                                                        current_image = current_image,
                                                                        blending_image = blending_image,
            
                                                                    )

            # save the blending image                                   
            blending_image.save()
            
            # Reload the current blending data
            current_blending_image = BlendingWithCurrentImage.objects.get(id = blending_image.id)
            
            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if current_image.current_image_format == 1:
                
                # Read the current Image data
                current_image_data = cv2.imread(f'{base}/{current_image.Image.url}', 0)

                # Read Blending image data
                blending_image_data = cv2.imread(f'{base}/{current_blending_image.blending_image.url}', 0)
                
                # Get Image Width and Height
                img_1_height, img_1_width = np.shape(current_image_data)
                img_2_height, img_2_width = np.shape(blending_image_data)

                # Resize the current blending image with current image size
                blending_image_data = cv2.resize(blending_image_data, (img_1_width, img_1_height))

                # Output image matrix
                output_image = np.ndarray((img_1_height, img_1_width), np.uint8)

                # Blinding the images
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image[i][j] = (current_image_data[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_data[i][j] * float(blending_persentage_value))
                

            elif current_image.current_image_format == 2:

                # Read the HSV Image
                current_image_data = cv2.imread(f'{base}/{current_image.Image.url}', cv2.COLOR_BGR2HSV)
                current_image_data = cv2.resize(current_image_data, (current_image.current_image_width, current_image.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Read the HSV Blending Image
                blending_image_data = cv2.imread(f'{base}/{current_blending_image.blending_image.url}', cv2.COLOR_BGR2HSV)
                blending_image_data = cv2.resize(blending_image_data, (current_image.current_image_width, current_image.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Get Image Width and Height
                img_1_height, img_1_width, img_1_channal = np.shape(current_image_data)
                img_2_height, img_2_width, img_2_channal = np.shape(blending_image_data)

                # Split current image channals to HSV
                current_image_hue, current_image_saturation, current_image_value = cv2.split(current_image_data)

                # Split blending image channels to HSV
                blending_image_hue, blending_image_saturation, blending_image_value = cv2.split(blending_image_data)

                # Resize the current blending image with current image size
                blending_image_hue = cv2.resize(blending_image_hue, (img_1_width, img_1_height))
                blending_image_saturation = cv2.resize(blending_image_saturation, (img_1_width, img_1_height))
                blending_image_value = cv2.resize(blending_image_value, (img_1_width, img_1_height))

                # Output image matrix
                output_image_hue = np.ndarray((img_1_height, img_1_width), np.uint8)
                output_image_saturation = np.ndarray((img_1_height, img_1_width), np.uint8)
                output_image_value = np.ndarray((img_1_height, img_1_width), np.uint8)


                # Blinding the hue
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_hue[i][j] = (current_image_hue[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_hue[i][j] * float(blending_persentage_value))


                # Blinding the saturation
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_saturation[i][j] = (current_image_saturation[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_saturation[i][j] * float(blending_persentage_value))

                # Blinding the value
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_value[i][j] = (current_image_value[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_value[i][j] * float(blending_persentage_value))                        


                # Merg the HSV OUTPUT image
                output_image = cv2.merge((output_image_hue, output_image_saturation, output_image_value))


            else:

                # Read the RGB Image
                current_image_data = cv2.imread(f'{base}/{current_image.Image.url}')
                
                # Read the RGB Blending Image
                blending_image_data = cv2.imread(f'{base}/{current_blending_image.blending_image.url}')

                # Get Image Width and Height
                img_1_height, img_1_width, img_1_channal = np.shape(current_image_data)
                img_2_height, img_2_width, img_2_channal = np.shape(blending_image_data)

                # Split current image channals to HSV
                current_image_blue, current_image_green, current_image_red = cv2.split(current_image_data)

                # Split blending image channels to HSV
                blending_image_blue, blending_image_green, blending_image_red = cv2.split(blending_image_data)

                # Resize the current blending image with current image size
                blending_image_blue = cv2.resize(blending_image_blue, (img_1_width, img_1_height))
                blending_image_green = cv2.resize(blending_image_green, (img_1_width, img_1_height))
                blending_image_red = cv2.resize(blending_image_red, (img_1_width, img_1_height))

                # Output image matrix
                output_image_blue = np.ndarray((img_1_height, img_1_width), np.uint8)
                output_image_green = np.ndarray((img_1_height, img_1_width), np.uint8)
                output_image_red = np.ndarray((img_1_height, img_1_width), np.uint8)

                # Blinding the blue
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_blue[i][j] = (current_image_blue[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_blue[i][j] * float(blending_persentage_value))


                # Blinding the green
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_green[i][j] = (current_image_green[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_green[i][j] * float(blending_persentage_value))

                # Blinding the red
                for i in range(0, img_1_height):
                    for j in range(0, img_1_width):
                        output_image_red[i][j] = (current_image_red[i][j] * float(1.0 - float(blending_persentage_value))) + (blending_image_red[i][j] * float(blending_persentage_value))                        


                # Merg the RGB OUTPUT image
                output_image = cv2.merge((output_image_blue, output_image_green, output_image_red))



            # Read the image extention
            path_list = str(current_image.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = current_image.current_image_format

            # Convert the image
            data = save_converted_image(current_image, output_image, extiention, image_format)
            

            # Return image data
            return JsonResponse(data)


@login_required
def negative_brightness(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply Negative
                image = np.subtract(image_src.current_image_Max_intensity, image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply Negative
                hue = np.subtract(image_src.current_image_Max_intensity, hue)
                saturation = np.subtract(image_src.current_image_Max_intensity, saturation)
                value = np.subtract(image_src.current_image_Max_intensity, value)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply TRANSLATION
                blue = np.subtract(image_src.current_image_Max_intensity, blue)
                green = np.subtract(image_src.current_image_Max_intensity, green)
                red = np.subtract(image_src.current_image_Max_intensity, red)

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def log_brightness(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Convert image intensities to float 32
                image = np.float32(image)

                # Apply TRANSLATION
                image = np.log(1 + image)

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
                
                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Convert image intensities to float 32
                hue = np.float32(hue)
                saturation = np.float32(saturation)
                value = np.float32(value)

                # Apply TRANSLATION
                hue = np.log(1 + hue)
                saturation = np.log(1 + saturation)
                value = np.log(1 + value)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Convert image intensities to float 32
                blue = np.float32(blue)
                green = np.float32(green)
                red = np.float32(red)


                # Apply TRANSLATION
                blue = np.log(1 + blue)
                green = np.log(1 + green)
                red = np.log(1 + red)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def power_brightness(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            gamma = request.POST.get('gamma')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Convert image intensities to float 32
                image = np.float32(image)

                # Apply POWER
                image = np.power(image + 1, np.float32(gamma))

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
                
                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Convert image intensities to float 32
                hue = np.float32(hue)
                saturation = np.float32(saturation)
                value = np.float32(value)

                # Apply POWER
                hue = np.power(hue + 1, np.float32(gamma))
                saturation = np.power(saturation + 1, np.float32(gamma))
                value = np.power(value + 1, np.float32(gamma))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Convert image intensities to float 32
                blue = np.float32(blue)
                green = np.float32(green)
                red = np.float32(red)


                # Apply POWER
                blue = np.power(blue + 1, np.float32(gamma))
                green = np.power(green + 1, np.float32(gamma))
                red = np.power(red + 1, np.float32(gamma))

                # Merg the hue image
                image = cv2.merge((blue, green, red))

                # Normalize the image values
                image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

                # Convert image to unchar8
                image = cv2.convertScaleAbs(image)


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def threshold_brightness(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            threshold = int(request.POST.get('threshold'))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Image Size
                height, width = np.shape(image)

                # Apply Threshold
                for h in range(height):
                    for w in range(width): 
                        if image[h][w] > threshold:
                            image[h][w] = 255
                        else:
                            image[h][w] = 0


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
                
                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Image Size
                height, width, channals = np.shape(image)

                # Apply Threshold over hue
                for h in range(height):
                    for w in range(width): 
                        if hue[h][w] > threshold:
                            hue[h][w] = 255
                        else:
                            hue[h][w] = 0
                
                # Apply Threshold over saturation
                for h in range(height):
                    for w in range(width): 
                        if saturation[h][w] > threshold:
                            saturation[h][w] = 255
                        else:
                            saturation[h][w] = 0

                # Apply Threshold over value
                for h in range(height):
                    for w in range(width): 
                        if value[h][w] > threshold:
                            value[h][w] = 255
                        else:
                            value[h][w] = 0

                # Merg the image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Image Size
                height, width, channals = np.shape(image)

                # Apply Threshold over blue
                for h in range(height):
                    for w in range(width): 
                        if blue[h][w] > threshold:
                            blue[h][w] = 255
                        else:
                            blue[h][w] = 0
                
                # Apply Threshold over green
                for h in range(height):
                    for w in range(width): 
                        if green[h][w] > threshold:
                            green[h][w] = 255
                        else:
                            green[h][w] = 0

                # Apply Threshold over red
                for h in range(height):
                    for w in range(width): 
                        if red[h][w] > threshold:
                            red[h][w] = 255
                        else:
                            red[h][w] = 0

                # Merg the image
                image = cv2.merge((blue, green, red))



            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def bitplan_brightness(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            plan_no = int(request.POST.get('plan_no'))
            
            # Set the bit plan value
            plan_value = 2**(plan_no - 1)


            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Image Size
                height, width = np.shape(image)

                # Apply BitPLan
                for h in range(height):
                    for w in range(width): 
                        if image[h][w] & plan_value:
                            image[h][w] = 255
                        else:
                            image[h][w] = 0


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
                
                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Image Size
                height, width, channals = np.shape(image)

                # Apply BitPLan over hue
                for h in range(height):
                    for w in range(width): 
                        if hue[h][w] & plan_value:
                            hue[h][w] = 255
                        else:
                            hue[h][w] = 0
                
                # Apply BitPLan over saturation
                for h in range(height):
                    for w in range(width): 
                        if saturation[h][w] & plan_value:
                            saturation[h][w] = 255
                        else:
                            saturation[h][w] = 0

                # Apply BitPLan over value
                for h in range(height):
                    for w in range(width): 
                        if value[h][w] & plan_value:
                            value[h][w] = 255
                        else:
                            value[h][w] = 0

                # Merg the image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Image Size
                height, width, channals = np.shape(image)

                # Apply BitPLan over blue
                for h in range(height):
                    for w in range(width): 
                        if blue[h][w] & plan_value:
                            blue[h][w] = 255
                        else:
                            blue[h][w] = 0
                
                # Apply BitPLan over green
                for h in range(height):
                    for w in range(width): 
                        if green[h][w] & plan_value:
                            green[h][w] = 255
                        else:
                            green[h][w] = 0

                # Apply BitPLan over red
                for h in range(height):
                    for w in range(width): 
                        if red[h][w] & plan_value:
                            red[h][w] = 255
                        else:
                            red[h][w] = 0

                # Merg the image
                image = cv2.merge((blue, green, red))



            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def image_compression(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            
            # Set the bit plan value
            compression_vector = [int(cv2.IMWRITE_JPEG_QUALITY), 5]


            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Get Width and Height
            width = image_src.current_image_width
            height = image_src.current_image_height

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Image encode
                result, imageEncode = cv2.imencode(".jpg", image, compression_vector)

                #  Compression
                cv2.imwrite(f'{base}/{image_src.Image.url}_commpressed.jpg', image, compression_vector)

                # Reload the commpressed Image
                image = cv2.imread(f'{base}/{image_src.Image.url}_commpressed.jpg', 0) 


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)
                
                # Image encode
                result, imageEncode = cv2.imencode(".jpg", image, compression_vector)

                #  Compression
                cv2.imwrite(f'{base}/{image_src.Image.url}_commpressed.jpg', image, compression_vector)


                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}_commpressed.jpg', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                # Image encode
                result, imageEncode = cv2.imencode(".jpg", image, compression_vector)
                
                #  Compression
                cv2.imwrite(f'{base}/{image_src.Image.url}_commpressed.jpg', image, compression_vector)

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}_commpressed.jpg')



            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Compression ratio
            data["compression_ratio"] = (width * height) / (int(imageEncode.shape[0]))

            # Return image data
            return JsonResponse(data)


# =====================================
# =========== SELECTION ===============

@login_required
def image_crop(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            width = int(float(request.POST.get('width')))
            height = int(float(request.POST.get('height')))
            top = int(float(request.POST.get('top')))
            left = int(float(request.POST.get('left')))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Skewing Source points
            src_points = np.float32([(left, top),(left + width, top),(left, top + height)])

            # Skewing Destnation points
            dst_points = np.float32([(0, 0), (width, 0), (0, height)])

            # Skewing matrix
            skewing_matrix = cv2.getAffineTransform(src_points, dst_points)

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl SKEW
                image = cv2.warpAffine(image, skewing_matrix, (width, height))


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl SKEW
                hue = cv2.warpAffine(hue, skewing_matrix, (width, height))
                saturation = cv2.warpAffine(saturation, skewing_matrix, (width, height))
                value = cv2.warpAffine(value, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl SKEW
                blue = cv2.warpAffine(blue, skewing_matrix, (width, height))
                green = cv2.warpAffine(green, skewing_matrix, (width, height))
                red = cv2.warpAffine(red, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))




            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def image_zoom_in(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            width = int(float(request.POST.get('width')))
            height = int(float(request.POST.get('height')))
            top = int(float(request.POST.get('top')))
            left = int(float(request.POST.get('left')))
            sacle = int(float(request.POST.get('sacle')))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Skewing Source points
            src_points = np.float32([(left, top),(left + width, top),(left, top + height)])

            # Skewing Destnation points
            dst_points = np.float32([(0, 0), (width, 0), (0, height)])

            # Skewing matrix
            skewing_matrix = cv2.getAffineTransform(src_points, dst_points)

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl SKEW
                image = cv2.warpAffine(image, skewing_matrix, (width, height))

                # Resize the image
                image = cv2.resize(image, (width * sacle, height * sacle), fx= 1, fy= 1, interpolation=cv2.INTER_AREA)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl SKEW
                hue = cv2.warpAffine(hue, skewing_matrix, (width, height))
                saturation = cv2.warpAffine(saturation, skewing_matrix, (width, height))
                value = cv2.warpAffine(value, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                # Resize the image
                image = cv2.resize(image, (width * sacle, height * sacle), fx= 1, fy= 1, interpolation=cv2.INTER_AREA)

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl SKEW
                blue = cv2.warpAffine(blue, skewing_matrix, (width, height))
                green = cv2.warpAffine(green, skewing_matrix, (width, height))
                red = cv2.warpAffine(red, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))

                # Resize the image
                image = cv2.resize(image, (width * sacle, height * sacle), fx= 1, fy= 1, interpolation=cv2.INTER_AREA)



            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


def image_cut_select(request):
    if request.method == "POST":
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')
            width = int(float(request.POST.get('width')))
            height = int(float(request.POST.get('height')))
            top = int(float(request.POST.get('top')))
            left = int(float(request.POST.get('left')))

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Skewing Source points
            src_points = np.float32([(left, top),(left + width, top),(left, top + height)])

            # Skewing Destnation points
            dst_points = np.float32([(0, 0), (width, 0), (0, height)])

            # Skewing matrix
            skewing_matrix = cv2.getAffineTransform(src_points, dst_points)
            
            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Appl SKEW
                image = cv2.warpAffine(image, skewing_matrix, (width, height))


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl SKEW
                hue = cv2.warpAffine(hue, skewing_matrix, (width, height))
                saturation = cv2.warpAffine(saturation, skewing_matrix, (width, height))
                value = cv2.warpAffine(value, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl SKEW
                blue = cv2.warpAffine(blue, skewing_matrix, (width, height))
                green = cv2.warpAffine(green, skewing_matrix, (width, height))
                red = cv2.warpAffine(red, skewing_matrix, (width, height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))

            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Save the zoomed image
            data = save_selected_image(image_src, image, extiention, image_format, left, top)
            

            return JsonResponse(data)


def image_cut_select_zoom_rotate(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')
            rotation_angle = int(request.POST.get('rotation_angle'))

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Rotation Matrix (Center, angle, scale)
            rotation_matrix = cv2.getRotationMatrix2D((image_src.width / 2, image_src.height / 2), rotation_angle, 1)

            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Appl Rotation
                image = cv2.warpAffine(image, rotation_matrix, (image_src.width, image_src.height))


            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl Rotation
                hue = cv2.warpAffine(hue, rotation_matrix, (image_src.width, image_src.height))
                saturation = cv2.warpAffine(saturation, rotation_matrix, (image_src.width, image_src.height))
                value = cv2.warpAffine(value, rotation_matrix, (image_src.width, image_src.height))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl Rotation
                blue = cv2.warpAffine(blue, rotation_matrix, (image_src.width, image_src.height))
                green = cv2.warpAffine(green, rotation_matrix, (image_src.width, image_src.height))
                red = cv2.warpAffine(red, rotation_matrix, (image_src.width, image_src.height))

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)


def image_cut_select_zoom_flip(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')
            flip_direction = request.POST.get('flip_direction')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))


            # Current work directory
            base = pathlib.Path().resolve()

            # Flip initial value
            image_flip = 0

            # Get the requested flip
            if flip_direction == 'X':
                image_flip = 0
            elif flip_direction == 'Y':
                image_flip = 1
            elif flip_direction == 'XY':
                image_flip = -1


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Appl flip
                image = cv2.flip(image, image_flip)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Appl Flip
                hue = cv2.flip(hue, image_flip)
                saturation = cv2.flip(saturation, image_flip)
                value = cv2.flip(value, image_flip)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Appl Flip
                blue = cv2.flip(blue, image_flip)
                green = cv2.flip(green, image_flip)
                red = cv2.flip(red, image_flip)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)


def cut_image_select_avarage_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Apply the avarage filter
                image = cv2.blur(image, (3,3))

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the avarage filter
                hue = cv2.blur(hue, (3,3))
                saturation = cv2.blur(saturation, (3,3))
                value = cv2.blur(value, (3,3))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the avarage filter
                blue = cv2.blur(blue, (3,3))
                green = cv2.blur(green, (3,3))
                red = cv2.blur(red, (3,3))

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)


def  cut_image_select_gaussian_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Apply the gaussian filter
                image = cv2.GaussianBlur(image, (3,3), 0)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the gaussian filter
                hue = cv2.GaussianBlur(hue, (3,3), 0)
                saturation = cv2.GaussianBlur(saturation, (3,3), 0)
                value = cv2.GaussianBlur(value, (3,3), 0)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the gaussian filter
                blue = cv2.GaussianBlur(blue, (3,3), 0)
                green = cv2.GaussianBlur(green, (3,3), 0)
                red = cv2.GaussianBlur(red, (3,3), 0)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)

def cut_image_select_circular_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                image = cv2.filter2D(image, -1, kernal)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)

def cut_image_select_cone_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25

                # Apply the circular filter
                image = cv2.filter2D(image, -1, kernal)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25

                # Apply the circular filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25

                # Apply the circular filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)

def cut_image_select_pyrmadial_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81

                # Apply the circular filter
                image = cv2.filter2D(image, -1, kernal)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81

                # Apply the circular filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81

                # Apply the circular filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)

def cut_image_select_median_filter(request):
    if request.method == "POST":
        # if request.is_ajax():
            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ZoomedImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()


            # Read the image
            if image_src.image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', 0)

                # Apply the median filter
                image = cv2.medianBlur(image, 3)

            elif image_src.image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.width, image_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the median filter
                hue = cv2.medianBlur(hue, 3)
                saturation = cv2.medianBlur(saturation, 3)
                value = cv2.medianBlur(value, 3)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.zoomed_image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the median filter
                blue = cv2.medianBlur(blue, 3)
                green = cv2.medianBlur(green, 3)
                red = cv2.medianBlur(red, 3)

                # Merg the hue image
                image = cv2.merge((blue, green, red))


            # Read the image extention
            path_list = str(image_src.zoomed_image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.image_format

            # Convert the image
            data = save_selected_image_effect(image_src, image, extiention, image_format, image_src.x_position, image_src.y_position)
            
            # Return image data
            return JsonResponse(data)




def apply_cut_selected_image_effects(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Get the Last Effect
            effect_src = ZoomedImages.objects.filter(target_image=image_src).last()
            
            # Effect image Data
            height = effect_src.height
            width = effect_src.width
            x = effect_src.x_position
            y = effect_src.y_position

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Read the effect
                effect = cv2.cv2.imread(f'{base}/{effect_src.zoomed_image.url}', 0)

                # Merge the effect to image
                for i in range(height):
                    for j in range(width):
                        image[y + i][x + j] = effect[i][j]

            elif image_src.current_image_format == 2:
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Read the effect
                effect = cv2.cv2.imread(f'{base}/{effect_src.zoomed_image.url}', cv2.COLOR_BGR2HSV)
                effect = cv2.resize(effect, (effect_src.width, effect_src.height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                image_hue, image_saturation, image_value = cv2.split(image)
                effect_hue, effect_saturation, effect_value = cv2.split(effect)

                # Merge the effect to image
                for i in range(height):
                    for j in range(width):
                        image_hue[y + i][x + j] = effect_hue[i][j]

                for i in range(height):
                    for j in range(width):
                        image_saturation[y + i][x + j] = effect_saturation[i][j]

                for i in range(height):
                    for j in range(width):
                        image_value[y + i][x + j] = effect_value[i][j]
                
                # Merg the hue image
                image = cv2.merge((image_hue, image_saturation, image_value))

            else:
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}')

                # Read the effect
                effect = cv2.cv2.imread(f'{base}/{effect_src.zoomed_image.url}')

                # Split channals to HSV
                image_blue, image_green, image_red = cv2.split(image)
                effect_blue, effect_green, effect_red = cv2.split(effect)

                # Merge the effect to image
                for i in range(height):
                    for j in range(width):
                        image_blue[y + i][x + j] = effect_blue[i][j]

                for i in range(height):
                    for j in range(width):
                        image_green[y + i][x + j] = effect_green[i][j]

                for i in range(height):
                    for j in range(width):
                        image_red[y + i][x + j] = effect_red[i][j]
                
                # Merg the hue image
                image = cv2.merge((image_blue, image_green, image_red))



            
            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)





# ============================
# =========== FILTERS ========

@login_required
def avarage_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the avarage filter
                image = cv2.blur(image, (3,3))


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the avarage filter
                hue = cv2.blur(hue, (3,3))
                saturation = cv2.blur(saturation, (3,3))
                value = cv2.blur(value, (3,3))

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the avarage filter
                blue = cv2.blur(blue, (3,3))
                green = cv2.blur(green, (3,3))
                red = cv2.blur(red, (3,3))

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def gaussian_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the gaussian filter
                image = cv2.GaussianBlur(image, (3,3), 0)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the gaussian filter
                hue = cv2.GaussianBlur(hue, (3,3), 0)
                saturation = cv2.GaussianBlur(saturation, (3,3), 0)
                value = cv2.GaussianBlur(value, (3,3), 0)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the gaussian filter
                blue = cv2.GaussianBlur(blue, (3,3), 0)
                green = cv2.GaussianBlur(green, (3,3), 0)
                red = cv2.GaussianBlur(red, (3,3), 0)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def circular_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                image = cv2.filter2D(image, -1, kernal)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]])
                kernal = kernal / 21

                # Apply the circular filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def cone_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25

                # Apply the cone filter
                image = cv2.filter2D(image, -1, kernal)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25

                # Apply the cone filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[0, 0, 1, 0, 0], [0, 2, 2, 2, 0], [1, 2, 5, 2, 1], [0, 2, 2, 2, 0], [0, 0, 1, 0, 0]])
                kernal = kernal / 25
                
                # Apply the cone filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def pyrmadial_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81

                # Apply the pyrmadial filter
                image = cv2.filter2D(image, -1, kernal)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81

                # Apply the pyrmadial filter
                hue = cv2.filter2D(hue, -1, kernal)
                saturation = cv2.filter2D(saturation, -1, kernal)
                value = cv2.filter2D(value, -1, kernal)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Filter Kernal
                kernal = np.array([[1, 2, 3, 2, 1], [2, 4, 6, 4, 2], [3, 6, 9, 6, 3], [2, 4, 6, 4, 2], [1, 2, 3, 2, 1]])
                kernal = kernal / 81
                
                # Apply the pyrmadial filter
                blue = cv2.filter2D(blue, -1, kernal)
                green = cv2.filter2D(green, -1, kernal)
                red = cv2.filter2D(red, -1, kernal)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def median_filter(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the median filter
                image = cv2.medianBlur(image, 3)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the median filter
                hue = cv2.medianBlur(hue, 3)
                saturation = cv2.medianBlur(saturation, 3)
                value = cv2.medianBlur(value, 3)

                # Merg the hue image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the median filter
                blue = cv2.medianBlur(blue, 3)
                green = cv2.medianBlur(green, 3)
                red = cv2.medianBlur(red, 3)

                # Merg the hue image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def v_edge(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the Sobel filter
                image = cv2.Sobel(image, cv2.CV_16UC1, 1, 0, 5)

                # Reconvert the image to uint8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the Sobel filter
                hue = cv2.Sobel(hue, cv2.CV_16UC1, 1, 0, 5)
                saturation = cv2.Sobel(saturation, cv2.CV_16UC1, 1, 0, 5)
                value = cv2.Sobel(value, cv2.CV_16UC1, 1, 0, 5)

                # Reconvert the channals to uint8
                hue = cv2.convertScaleAbs(hue)
                saturation = cv2.convertScaleAbs(saturation)
                value = cv2.convertScaleAbs(value)

                # Merg the HSV image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the Sobel filter
                blue = cv2.Sobel(blue, cv2.CV_16UC1, 1, 0, 5)
                green = cv2.Sobel(green, cv2.CV_16UC1, 1, 0, 5)
                red = cv2.Sobel(red, cv2.CV_16UC1, 1, 0, 5)

                # Reconvert the channals to uint8
                blue = cv2.convertScaleAbs(blue)
                green = cv2.convertScaleAbs(green)
                red = cv2.convertScaleAbs(red)

                # Merg the RGB image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def h_edge(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the Sobel filter
                image = cv2.Sobel(image, cv2.CV_16UC1, 0, 1, 5)

                # Reconvert the image to uint8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the Sobel filter
                hue = cv2.Sobel(hue, cv2.CV_16UC1, 0, 1, 5)
                saturation = cv2.Sobel(saturation, cv2.CV_16UC1, 0, 1, 5)
                value = cv2.Sobel(value, cv2.CV_16UC1, 0, 1, 5)

                # Reconvert the channals to uint8
                hue = cv2.convertScaleAbs(hue)
                saturation = cv2.convertScaleAbs(saturation)
                value = cv2.convertScaleAbs(value)

                # Merg the HSV image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the Sobel filter
                blue = cv2.Sobel(blue, cv2.CV_16UC1, 0, 1, 5)
                green = cv2.Sobel(green, cv2.CV_16UC1, 0, 1, 5)
                red = cv2.Sobel(red, cv2.CV_16UC1, 0, 1, 5)

                # Reconvert the channals to uint8
                blue = cv2.convertScaleAbs(blue)
                green = cv2.convertScaleAbs(green)
                red = cv2.convertScaleAbs(red)

                # Merg the RGB image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def sobel_edge(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the Sobel filter
                image_1 = cv2.Sobel(image, cv2.CV_16UC1, 1, 0, 5)
                image_2 = cv2.Sobel(image, cv2.CV_16UC1, 0, 1, 5)

                # Combine images
                image = cv2.addWeighted(image_1, 1, image_2, 1, 0.0)

                # Reconvert the image to uint8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the Sobel filter over HUE
                hue_1 = cv2.Sobel(hue, cv2.CV_16UC1, 1, 0, 5)
                hue_2 = cv2.Sobel(hue, cv2.CV_16UC1, 0, 1, 5)
                hue = cv2.addWeighted(hue_1, 1, hue_2, 1, 0.0)

                # Apply the Sobel filter over Saturation
                saturation_1 = cv2.Sobel(saturation, cv2.CV_16UC1, 1, 0, 5)
                saturation_2 = cv2.Sobel(saturation, cv2.CV_16UC1, 0, 1, 5)
                saturation = cv2.addWeighted(saturation_1, 1, saturation_2, 1, 0.0)

                # Apply the Sobel filter over value
                value_1 = cv2.Sobel(value, cv2.CV_16UC1, 1, 0, 5)
                value_2 = cv2.Sobel(value, cv2.CV_16UC1, 0, 1, 5)
                value = cv2.addWeighted(value_1, 1, value_2, 1, 0.0)

                # Reconvert the channals to uint8
                hue = cv2.convertScaleAbs(hue)
                saturation = cv2.convertScaleAbs(saturation)
                value = cv2.convertScaleAbs(value)

                # Merg the HSV image
                image = cv2.merge((hue, saturation, value))

                
            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the Sobel filter over Blue
                blue_1 = cv2.Sobel(blue, cv2.CV_16UC1, 1, 0, 5)
                blue_2 = cv2.Sobel(blue, cv2.CV_16UC1, 0, 1, 5)
                blue = cv2.addWeighted(blue_1, 1, blue_2, 1, 0.0)

                # Apply the Sobel filter over Green
                green_1 = cv2.Sobel(green, cv2.CV_16UC1, 1, 0, 5)
                green_2 = cv2.Sobel(green, cv2.CV_16UC1, 0, 1, 5)
                green = cv2.addWeighted(green_1, 1, green_2, 1, 0.0)

                # Apply the Sobel filter over RED
                red_1 = cv2.Sobel(red, cv2.CV_16UC1, 1, 0, 5)
                red_2 = cv2.Sobel(red, cv2.CV_16UC1, 0, 1, 5)
                red = cv2.addWeighted(red_1, 1, red_2, 1, 0.0)

                # Reconvert the channals to uint8
                blue = cv2.convertScaleAbs(blue)
                green = cv2.convertScaleAbs(green)
                red = cv2.convertScaleAbs(red)

                # Merg the RGB image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)


@login_required
def laplacian_edge(request):
    if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the image
            if image_src.current_image_format == 1:
                
                # Read the Gary IMage
                image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

                # Apply the Laplacian filter
                image = cv2.Laplacian(image, cv2.CV_16UC1)

                # Reconvert the image to uint8
                image = cv2.convertScaleAbs(image)


            elif image_src.current_image_format == 2:
                
                # Read the HSV Image
                image = cv2.imread(f'{base}/{image_src.Image.url}', cv2.COLOR_BGR2HSV)
                image = cv2.resize(image, (image_src.current_image_width, image_src.current_image_height), fx= 1, fy= 1, interpolation=cv2.INTER_CUBIC)

                # Split channals to HSV
                hue, saturation, value = cv2.split(image)

                # Apply the Laplacian filter
                hue = cv2.Laplacian(hue, cv2.CV_16UC1)
                saturation = cv2.Laplacian(saturation, cv2.CV_16UC1)
                value = cv2.Laplacian(value, cv2.CV_16UC1)

                # Reconvert the channals to uint8
                hue = cv2.convertScaleAbs(hue)
                saturation = cv2.convertScaleAbs(saturation)
                value = cv2.convertScaleAbs(value)

                # Merg the HSV image
                image = cv2.merge((hue, saturation, value))

                

            else:

                # Read the RGB Image
                image = cv2.imread(f'{base}/{image_src.Image.url}')
                
                
                # Split channals to RGB
                blue, green, red = cv2.split(image)

                # Apply the Laplacian filter
                blue = cv2.Laplacian(blue, cv2.CV_16UC1)
                green = cv2.Laplacian(green, cv2.CV_16UC1)
                red = cv2.Laplacian(red, cv2.CV_16UC1)

                # Reconvert the channals to uint8
                blue = cv2.convertScaleAbs(blue)
                green = cv2.convertScaleAbs(green)
                red = cv2.convertScaleAbs(red)

                # Merg the RGB image
                image = cv2.merge((blue, green, red))

               


            # Read the image extention
            path_list = str(image_src.Image.url).split('.')
            extiention = path_list[-1]

            # Image Forma
            image_format = image_src.current_image_format

            # Convert the image
            data = save_converted_image(image_src, image, extiention, image_format)
            
            # Return image data
            return JsonResponse(data)




def ocr_text_detection(request):
        if request.method == 'POST':
        # if request.is_ajax():

            # Get Data
            image_id = request.POST.get('image_id')

            # get the image
            image_src = ProjectsImages.objects.get(id = int(image_id))

            # Current work directory
            base = pathlib.Path().resolve()

            # Read the Gary IMage
            image = cv2.imread(f'{base}/{image_src.Image.url}', 0)

            # Get Caracters
            text = pytesseract.image_to_string(image)
      
            # Reterned Data
            data = {'text':text}

            print("=" * 50)
            print(text)
            print("=" * 50)

            
            # Return image data
            return JsonResponse(data)

