import os
o_lables = open('label.list').readlines()
images_dir = 'CheckCode/checkcode_bin'
filelist = os.listdir(images_dir)
labels = open("labels", "w+")
for filename in filelist:
    image_path = images_dir + '/' + filename
    filename_split = filename.replace('.png', '').split('_')
    labels.write(o_lables[int(filename_split[0])].replace(
        '\n', '')[int(filename_split[1])]+'#'+image_path+'\n')

# print(images_path)
