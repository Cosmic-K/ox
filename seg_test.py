#Name: Krishna Mooroogen 
#Date: 05/07/2019
#Last update: 08/07/2019
#description: 
'''
Oxford heartbeat, 
region growing segmentation method to extract
left ventrical from dicom images of heart 
'''

import pydicom
import numpy as np 
import matplotlib.pyplot as plt 
#from time import sleep

def main() : 
	areas=[]
	#store seg areas of slices
	thresh=200
	#intesnity threshold 
	region_array=np.empty((256,256,11))
	for i in range(2,12):
	#loop over dcm files 
	#display and set seed point by clicking
	#run seg grow algorithm and store seg area 
	#sum areas as integral estimate of volume
	#only looping over files where left ventrical is visible
		if i < 10: 
			ds=pydicom.read_file('volunteer/00'+str(i)+'.dcm')
		else:		
			ds=pydicom.read_file('volunteer/0'+str(i)+'.dcm')

		#ds=pydicom.read_file('volunteer/002.dcm')
		ds=ds.pixel_array
		ds=ds.reshape([ds.shape[0],ds.shape[1]])
		plt.imshow(ds,cmap='Greys_r')
			
		#select crop region 
		print('click on lower left x location')
		xy_1 = plt.ginput(1) 
		print('click on lower righ x location')
		xy_2 = plt.ginput(1) 
		print('click on upper y location')
		xy_3 = plt.ginput(1) 
		plt.close()


		ds1=ds[int(xy_3[0][1]):int(xy_1[0][1]),int(xy_1[0][0]):int(xy_2[0][0])]
		plt.imshow(ds1,cmap='Greys_r')

		#select seed point
		seed = plt.ginput(1) #mouse capture
		#print(seed)
		plt.close()
		#ds1, xy1 etc
		area,seg_region=reg_grow(ds1,ds,int(seed[0][0]),int(seed[0][1]),thresh,int(xy_3[0][1]),int(xy_1[0][0]))
		areas.append(area)
		region_array[:,:,i-2]=seg_region
		#plt.imshow(seg_region)
		#sleep(30) # check image time 
		plt.close()

	return region_array, areas
def neighbour_coord(xc,yc) : 
	#nearest 8 neighbouring pixels coordinates 
	#starting from seed pixel
	
	x = [-1, 0, 1, -1, 1, -1, 0, 1]
	y = [-1, -1, -1, 0, 0, 1, 1, 1]

	neighbours=[]
	
	for i in range(8):
		neighbours.append((xc+x[i],yc+y[i]))	


	return neighbours

def reg_grow(im,im2, seed_x,seed_y,thresh,x,y) :

	rows,columns = np.shape(im)#cropped image

	rows_1,columns_1 = np.shape(im2)#full image to get size for mapping - could just send size from main function
	#print(rows, columns)
	#create array for segmented region
	#using binary format so it can be applied as mask later
	seg_region = np.ones((rows_1,columns_1))
	seg_region[seed_x][seed_y] = 0

	#create queue list and processed list 
	#of checked points
	#points in seg points are in the queue when there are zero points left then 
	#checking stops
	#processed stores a list of pixels that have been checked 

	seg_points = []
	seg_points.append((seed_x,seed_y))
	processed = []

	while(len(seg_points) > 0):
		loc = seg_points[0]
		for point in neighbour_coord(loc[0], loc[1]): #find list of neighbouring pixels
			check_inside_image = (point[0]>= 0) & (point[1] >= 0) & (point[1] < columns) & (point[0] < rows)
			if check_inside_image : #check within image boundaries 
				#print(point)
				if im[point[0], point[1]] >= thresh: # check against threshold to find image boundary
					seg_region[point[0]+x, point[1]+y] = 0 #add point to seg region to build image 
					if not point in processed: # check if point has been processed as new seed
						seg_points.append(point)
					processed.append(point)
		seg_points.pop(0) #remove last used seed point
       
	area=len(np.where( seg_region == 0)[0])
	#count the segmented area to determine later volume
	return area, seg_region

#Final comments and improvments: 
'''
current prototype grows region around seed point cropped area to segment image
cropping used to minimise search space for speed

current threshold value correctly identifies bright regions 
though does not isolate the left ventricle automatically in full FOV as there is no growth boundary defined
current manual crop slection is not efficent and subject to bias and likely under/over estimation 

further tests are needed to better detmerine the boundary conditions to halt the growth in smaller region
could try a hugh trasform  or edge detection to first find circular shapes thus reducing the image space 
then using image geometry to further isolate

should add plotting with binary mask overlay
should apply pre-processing to improve boundary contrast 

or when changing growth method to a circular growth by using region points
could just check threshold on either side of circular perimeter until some boundary is found

volumes estimated by integrating segmented areas over the slices 

automated - 11538 (in pixels) likley underestimated 
manual - 16650.835 (in pixels) probably slightly overestimated

pre-processing may assist in reducing intensity variability
could use mean thresholding instead of discrete value 


limitations of method as a whole and possible alternatives: : 

subjective seed point choice 
could use histogram to choose a seed point 
due to loop structures searching image is computational expensive 
could limit image region space to increase speed but requires some prior knowledge of heart
can use weighted means or cog method to find bright points if the ventrical falls with those areas all the time 
this method will fall over when image intesnities are too similiar - i.e reduced contrast - gradient problem
will also be very sensitive to image noise 
that may require extensive pre-processing 

image capture regulating could be imposed 


other methods worth trying:

watershed segmentation with flooding 

semi-supervised cnn approach 

k-means clustering 

'''
